import json
import urllib
import urllib2

__author__ = 'bromix'


class Client(object):
    def __init__(self):
        self._opener = urllib2.build_opener()
        self._opener.addheaders = [('User-Agent', 'Dalvik/1.6.0 (Linux; U; Android 4.4.4; GT-I9100 Build/KTU84Q)'),
                                   ('Host', 'api.netzkino.de.simplecache.net'),
                                   ('Connection', 'Keep-Alive')]
        pass

    def _execute(self, path, params=None):
        """
        [HOME]
        http://api.netzkino.de.simplecache.net/capi-2.0a/index.json?d=android-phone&l=de-DE&g=DE

        [CATEGORY]
        http://api.netzkino.de.simplecache.net/capi-2.0a/categories/5?d=android-phone&l=de-DE&g=DE
        :param params:
        :return:
        """

        # prepare the params
        if not params:
            params = {}
            pass
        params['d'] = 'android-tablet'
        params['l'] = 'de-DE'
        params['g'] = 'DE'

        base_url = 'http://api.netzkino.de.simplecache.net/capi-2.0a/'
        url = base_url + path.strip('/')
        url = url + '?' + urllib.urlencode(params)

        content = self._opener.open(url)
        return json.load(content, encoding='utf-8')

    def get_home(self):
        """
        Main entry point to get data of netzkino.de
        :return:
        """
        return self._execute('index.json')

    def get_categories(self):
        """
        Returns directly the 'categories'
        :return:
        """
        json_data = self.get_home()
        return json_data.get('categories', {})

    pass
