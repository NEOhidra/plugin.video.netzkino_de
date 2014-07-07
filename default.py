# -*- coding: utf-8 -*-

import xbmcplugin
import xbmcgui
import xbmcaddon

import os
import json
import urllib2
import urllib

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

from bromixbmc import Bromixbmc
bromixbmc = Bromixbmc("plugin.video.netzkino_de", sys.argv)

__FANART__ = os.path.join(bromixbmc.Addon.Path, "fanart.jpg")
__ICON_HIGHLIGHTS__ = os.path.join(bromixbmc.Addon.Path, "resources/media/highlight.png")
__ICON_SEARCH__ = os.path.join(bromixbmc.Addon.Path, "resources/media/search.png")

__ACTION_SHOW_CATEGORY__ = 'showCategory'
__ACTION_SEARCH__ = 'search'
__ACTION_PLAY__ = 'play'

__SETTING_SHOW_FANART__ = bromixbmc.Addon.getSetting('showFanart')=="true"
if not __SETTING_SHOW_FANART__:
    __FANART__ = ''

def _request(url_path, params={}):
    params['d'] = 'android-tablet'
    params['l'] = 'de-DE'
    params['g'] = 'DE'
    
    result = {}
    
    url = 'http://api.netzkino.de.simplecache.net'
    if not url_path.startswith('/'):
        url = url+'/'
        
    url = url+url_path
        
    if len(params)>0:
        query_args = urllib.urlencode(params)
        if not url.endswith('?'):
            url = url+'?'
        url = url+query_args
        
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)'),
                         ('Host', 'api.netzkino.de.simplecache.net')]
    try:
        content = opener.open(url)
        result = json.load(content)
    except:
        # do nothing
        pass
    
    return result

def _listCategories(json_categories):
    for category in json_categories:
        id = category.get('id', None)
        name = category.get('title', None)
        if id!=None and name!=None:
            thumbnailImage = 'http://dyn.netzkino.de/wp-content/themes/netzkino/imgs/categories/'+str(id)+'.png'
            if id==8 or id==161:
                thumbnailImage = __ICON_HIGHLIGHTS__
            params = {'action': __ACTION_SHOW_CATEGORY__,
                      'id': id}
            bromixbmc.addDir(name=name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__)

def showIndex():
    params = {'action': __ACTION_SEARCH__}
    bromixbmc.addDir("[B]"+bromixbmc.Addon.localize(30000)+"[/B]", params = params, thumbnailImage=__ICON_SEARCH__, fanart=__FANART__)
    
    categories = _request('/capi-2.0a/index.json')
    
    # first list the homepage categories
    homepage_categories = categories.get('homepage_categories', {})
    _listCategories(homepage_categories)
            
    # after that load all other categories
    categories = categories.get('categories', {})
    _listCategories(categories)
            
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def _listPosts(json_posts):
    for post in json_posts:
        id = post.get('id', None)
        name = post.get('title', None)
        thumbnailImage = post.get('thumbnail', '')
        
        custom_fields = post.get('custom_fields', None)
        if custom_fields!=None:
            fanart = ''
            if __SETTING_SHOW_FANART__:
                fanart = custom_fields.get('featured_img_all', [__FANART__])[0]
            streaming = custom_fields.get('Streaming', None)
            if streaming!=None and len(streaming)>0:
                streamId = streaming[0]
                params = {'action': __ACTION_PLAY__,
                          'id': streamId}
                bromixbmc.addVideoLink(name=name, params=params, thumbnailImage=thumbnailImage, fanart=fanart)

def showCategory(id):
    category = _request('/capi-2.0a/categories/'+id)
    posts = category.get('posts', {})
    _listPosts(posts)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def play(id):
    url = 'http://netzkino_and-vh.akamaihd.net/i/'+id+'.mp4/master.m3u8'
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(bromixbmc.Addon.Handle, True, listitem)
    
def search():
    success = False
    keyboard = xbmc.Keyboard('', bromixbmc.Addon.localize(30000))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        success = True
        
        search_string = keyboard.getText().replace(" ", "+")
        result = _request('/capi-2.0a/search', params = {'q': search_string})
        posts = result.get('posts', [])
        _listPosts(posts)
        
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle, succeeded=success)
    return True

action = bromixbmc.getParam('action')
id = bromixbmc.getParam('id')

if action == __ACTION_SEARCH__:
    search()
elif action == __ACTION_SHOW_CATEGORY__ and id!=None:
    showCategory(id)
elif action == __ACTION_PLAY__ and id!=None:
    play(id)
else:
    showIndex()