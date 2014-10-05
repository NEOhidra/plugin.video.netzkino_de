from resources.lib.kodimon import DirectoryItem
from resources.lib.kodimon.abstract_api import create_content_path

__author__ = 'bromix'

from resources.lib import kodimon


class Provider(kodimon.AbstractProvider):
    def __init__(self, plugin=None):
        kodimon.AbstractProvider.__init__(self, plugin)

        from . import Client
        self._client = Client()
        pass

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