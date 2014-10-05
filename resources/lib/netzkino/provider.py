from resources.lib.kodimon import DirectoryItem, VideoItem
from resources.lib.kodimon.abstract_api import create_content_path

__author__ = 'bromix'

from resources.lib import kodimon


class Provider(kodimon.AbstractProvider):
    def __init__(self, plugin=None):
        kodimon.AbstractProvider.__init__(self, plugin)

        from . import Client
        self._client = Client()
        pass

    @kodimon.RegisterPath('^/category/(?P<categoryid>\d+)/?$')
    def _on_category(self, path, params, re_match):
        result = []
        category_id = re_match.group('categoryid')

        json_data = self._client.get_category_content(category_id)
        posts = json_data['posts']
        for post in posts:
            movie_item = VideoItem(post['title'],
                                   create_content_path('play', str(post['id'])),
                                   image=post['thumbnail'])
            custom_fields = post.get('custom_fields', {})
            featured_img_all = custom_fields.get('featured_img_all', [])
            if len(featured_img_all)>=1:
                movie_item.set_fanart(featured_img_all[0])
                pass

            result.append(movie_item)
            pass

        return result

    def on_root(self, path, params, re_match):
        result = []

        # search
        search_item = DirectoryItem('[B]'+self.localize(self.LOCAL_SEARCH)+'[/B]',
                                    create_content_path(self.PATH_SEARCH, 'list'),
                                    image=self.create_resource_path('media', 'search.png')
                                    )
        search_item.set_fanart(self._plugin.get_fanart())
        result.append(search_item)

        # categories
        categories = self._client.get_categories()
        for category in categories:
            category_id = str(category['id'])
            image = 'http://dyn.netzkino.de/wp-content/themes/netzkino/imgs/categories/%s.png' % category_id
            category_item = DirectoryItem(category['title'],
                                          create_content_path('category', category_id),
                                          image=image)
            category_item.set_fanart(self._plugin.get_fanart())
            result.append(category_item)
            pass

        return result, {self.RESULT_CACHE_TO_DISC: False}

    pass