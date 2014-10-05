__author__ = 'bromix'

import unittest
from resources.lib.netzkino import Client

class TestClient(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_categories(self):
        client = Client()
        json_data = client.get_categories()

        # at least 1 ore more items
        self.assertGreater(len(json_data), 1)

        print "Found '%d' categories" % len(json_data)
        print '====================='
        for category in json_data:
            print "Title: %s" % category['title']
            print "Id   : %d" % category['id']
            print '---------------------'
            pass
        pass

    def test_get_home(self):
        client = Client()
        json_data = client.get_home()

        # at least 1 ore more items
        self.assertGreater(len(json_data), 1)
        pass

    pass
