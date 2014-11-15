import re

from .exceptions import KodimonException
from .items import *
from . import constants
from .utils import build_in_functions


class AbstractProvider(object):
    RESULT_CACHE_TO_DISC = 'cache_to_disc'  # (bool)

    def __init__(self):
        # map for regular expression (path) to method (names)
        self._dict_path = {}

        # register some default paths
        self.register_path('^/$', '_internal_root')
        self.register_path('^/' + constants.paths.WATCH_LATER + '/(?P<command>add|remove|list)/?$',
                           '_internal_watch_later')
        self.register_path('^/' + constants.paths.FAVORITES + '/(?P<command>add|remove|list)/?$', '_internal_favorite')
        self.register_path('^/' + constants.paths.SEARCH + '/(?P<command>new|query|list|remove)/?$', '_internal_search')

        """
        Test each method of this class for the appended attribute '_re_match' by the
        decorator (RegisterProviderPath).
        The '_re_match' attributes describes the path which must match for the decorated method.
        """

        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, 'kodimon_re_path'):
                self.register_path(method.kodimon_re_path, method_name)
                pass
            pass

        pass

    def shut_down(self):
        self._search = None
        self._cache = None
        self._watch_later_list = None
        pass

    def register_path(self, re_path, method_name):
        """
        Registers a new method by name (string) for the given regular expression
        :param re_path: regular expression of the path
        :param method_name: name of the method
        :return:
        """
        self._dict_path[re_path] = method_name

    def navigate(self, context):
        path = context.get_path()

        for key in self._dict_path:
            re_match = re.search(key, path, re.UNICODE)
            if re_match is not None:
                method_name = self._dict_path.get(key, '')
                method = getattr(self, method_name)
                if method is not None:
                    result = method(context, re_match)
                    if not isinstance(result, tuple):
                        result = result, {}
                        pass
                    return result
                pass
            pass

        raise KodimonException("Mapping for path '%s' not found" % path)

    def on_search(self, search_text, context, re_match):
        """
        This method must be implemented by the derived class if the default search will be used.
        :param search_text:
        :param path:
        :param params:
        :param re_match:
        :return:
        """
        raise NotImplementedError()

    def on_root(self, context, re_match):
        """
        This method must be implemented by the derived class
        :param path:
        :param params:
        :param re_match:
        :return:
        """
        raise NotImplementedError()

    def on_watch_later(self, context, re_match):
        """
        This method can be implemented by the derived class to set the content type or add a sort method.
        :param path:
        :param params:
        :param re_match:
        :return:
        """
        pass

    def _internal_root(self, context, re_match):
        """
        Internal method to call the on root event.
        :param path:
        :param params:
        :param re_match:
        :return:
        """
        return self.on_root(context, re_match)

    def _internal_favorite(self, context, re_match):
        """
        Internal implementation of handling favorites.
        :param path:
        :param params:
        :param re_match:
        :return:
        """
        context.add_sort_method(constants.sort_method.LABEL_IGNORE_THE)

        params = context.get_params()

        command = re_match.group('command')
        if command == 'add':
            from . import from_json

            fav_item = from_json(params['item'])
            self._favorite_list.add(fav_item)
            pass
        elif command == 'remove':
            from . import from_json

            fav_item = from_json(params['item'])
            self._favorite_list.remove(fav_item)
            context.get_ui().refresh_container()
            pass
        elif command == 'list':

            directory_items = context.get_favorite_list().list()

            for directory_item in directory_items:
                context_menu = []
                remove_item = (context.localize(constants.localize.FAVORITES_REMOVE),
                               build_in_functions.run_plugin_remove_from_favs(context, directory_item))
                context_menu.append(remove_item)
                directory_item.set_context_menu(context_menu)
                pass

            return directory_items
        else:
            pass
        pass

    def _internal_watch_later(self, context, re_match):
        """
        Internal implementation of handling a watch later list.
        :param path:
        :param params:
        :param re_match:
        :return:
        """
        self.on_watch_later(context, re_match)

        params = context.get_params()

        command = re_match.group('command')
        if command == 'add':
            from . import from_json

            item = from_json(params['item'])
            self._watch_later_list.add(item)
            pass
        elif command == 'remove':
            from . import from_json

            item = from_json(params['item'])
            self._watch_later_list.remove(item)
            self.refresh_container()
            pass
        elif command == 'list':
            video_items = context.get_watch_later_list().list()

            for video_item in video_items:
                context_menu = []
                remove_item = (context.localize(constants.localize.WATCH_LATER_REMOVE),
                               build_in_functions.run_plugin_remove_from_watch_later(context, video_item))
                context_menu.append(remove_item)
                video_item.set_context_menu(context_menu)
                pass

            return video_items
        else:
            # do something
            pass
        pass

    def _internal_search(self, context, re_match):
        """
        Internal implementation of handling a search.
        :param path:
        :param params:
        :param re_match:
        :return:
        """
        params = context.get_params()

        command = re_match.group('command')
        search_history = context.get_search_history()
        if command == 'new' or (command == 'list' and search_history.is_empty()):
            result, text = context.get_ui().on_keyboard_input(context.localize(constants.localize.SEARCH_TITLE))
            if result:
                search_history.update(text)

                # we adjust the path and params as would it be a normal query
                new_path = constants.paths.SEARCH + '/query/'
                new_params = {}
                new_params.update(params)
                new_params['q'] = text
                new_context = context.clone(new_path=new_path, new_params=new_params)
                return self.on_search(text, new_context, re_match)
            pass
        elif command == 'remove':
            query = params['q']
            search_history.remove(query)
            context.get_ui().refresh_container()
            return True
        elif command == 'query':
            query = params['q']
            search_history.update(query)
            return self.on_search(query, context, re_match)
        else:
            result = []

            # 'New Search...'
            search_item = DirectoryItem('[B]' + context.localize(constants.localize.SEARCH_NEW) + '[/B]',
                                        context.create_uri([constants.paths.SEARCH, 'new']),
                                        image=context.create_resource_path('media/search.png'))
            search_item.set_fanart(context.get_fanart())
            result.append(search_item)

            for search in search_history.list():
                # little fallback for old history entries
                if isinstance(search, DirectoryItem):
                    search = search.get_name()
                    pass

                # we create a new instance of the SearchItem
                search_item = DirectoryItem(search,
                                            context.create_uri([constants.paths.SEARCH, 'query'], {'q': search}),
                                            image=context.create_resource_path('media/search.png'))
                search_item.set_fanart(context.get_fanart())
                context_menu = (context.localize(constants.localize.SEARCH_REMOVE),
                                build_in_functions.run_plugin_remove_from_search_history(context, search_item))
                search_item.set_context_menu(context_menu)
                result.append(search_item)
                pass
            return result, {self.RESULT_CACHE_TO_DISC: False}

        return False

    def handle_exception(self, exception_to_handle):
        return True

    pass