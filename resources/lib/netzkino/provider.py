from resources.lib.kodimon import DirectoryItem, VideoItem
from resources.lib.kodimon.abstract_api import create_content_path

__author__ = 'bromix'

from resources.lib import kodimon
from resources.lib.kodimon import constants, contextmenu


class Provider(kodimon.AbstractProvider):
    def __init__(self, plugin=None):
        kodimon.AbstractProvider.__init__(self, plugin)

        from . import Client
        self._client = Client()
        pass

    @kodimon.RegisterPath('^/play/?$')
    def _on_play(self, path, params, re_match):
        stream_id = params['stream_id']

        stream_url = self._client.get_video_url(stream_id)
        movie_item = VideoItem(stream_id,
                               create_content_path('play', stream_id))
        movie_item.set_url(stream_url)
        return movie_item

    @kodimon.RegisterPath('^/category/(?P<categoryid>\d+)/?$')
    def _on_category(self, path, params, re_match):
        def _read_custom_fields(_post, field_name):
            custom_fields = post.get('custom_fields', {})
            field = custom_fields.get(field_name, [])
            if len(field) >= 1:
                return field[0]
            return u''

        self.set_content_type(constants.CONTENT_TYPE_MOVIES)

        result = []
        category_id = re_match.group('categoryid')

        json_data = self._client.get_category_content(category_id)
        posts = json_data['posts']
        for post in posts:
            stream_id = _read_custom_fields(post, 'Streaming')
            movie_item = VideoItem(post['title'],
                                   create_content_path('play'),
                                   params={'stream_id': stream_id},
                                   image=post['thumbnail'])

            # year
            year = _read_custom_fields(post, 'Jahr')
            if year:
                # There was one case with '2006/2012' as a result. Therefore we split every year.
                year = year.split('/')[0]
                movie_item.set_year(year)
                pass

            # fanart
            movie_item.set_fanart(_read_custom_fields(post, 'featured_img_all'))

            # plot
            plot = kodimon.strip_html_from_text(post['content'])
            movie_item.set_plot(plot)

            ctx_menu = [contextmenu.create_add_to_watch_later(self._plugin,
                                                              self.LOCAL_WATCH_LATER,
                                                              movie_item)]
            movie_item.set_context_menu(ctx_menu)
            result.append(movie_item)
            pass

        return result

    def on_root(self, path, params, re_match):
        result = []

        # watch later
        if len(self._watch_later.list()) > 0:
            watch_later_item = DirectoryItem('[B]'+self.localize(self.LOCAL_WATCH_LATER)+'[/B]',
                                             create_content_path(self.PATH_WATCH_LATER, 'list'),
                                             image=self.create_resource_path('media', 'watch_later.png'))
            watch_later_item.set_fanart(self._plugin.get_fanart())
            result.append(watch_later_item)
            pass

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