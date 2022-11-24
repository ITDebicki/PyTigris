import unittest
import pytigris
import time

class CacheTests(unittest.TestCase):

    def test_cache_state(self):
        start = time.time()
        df_orig = pytigris.get_states(year = 2020, use_cache = True, refresh = True)
        no_cache_time = time.time() - start
        start = time.time()
        df_cached = pytigris.get_states(year = 2020, use_cache = True)
        cache_time = time.time() - start
        self.assertLess(cache_time, no_cache_time, "Cached copy took longer than downloading new copy")

        self.assertTrue(all(df_orig == df_cached), "Cached copy and downloaded copy are not the same")

    def test_cache_wipe(self):
        pytigris.get_states(year = 2020, use_cache = True)
        start = time.time()
        df_cached = pytigris.get_states(year = 2020, use_cache = True)
        cache_time = time.time() - start
        pytigris.util.clear_cache()
        start = time.time()
        df_not_cached = pytigris.get_states(year = 2020, use_cache = True)
        clear_cache_time = time.time() - start
        self.assertLess(cache_time, clear_cache_time, "Cache was not cleared")

        self.assertTrue(all(df_cached == df_not_cached), "Cached copy and downloaded copy are not the same")

    def test_cache_multiple(self):
        start = time.time()
        df_2020_orig = pytigris.get_states(year = 2020, use_cache = True, refresh = True)
        end_2020_no_cache = time.time() - start

        start = time.time()
        df_2019_orig = pytigris.get_states(year = 2019, use_cache = True, refresh = True)
        end_2019_no_cache = time.time() - start

        start = time.time()
        df_2020_cached = pytigris.get_states(year = 2020, use_cache = True)
        end_2020_cached = time.time() - start

        start = time.time()
        df_2019_cached = pytigris.get_states(year = 2019, use_cache = True, refresh = True)
        end_2019_cached = time.time() - start

        with self.subTest():
            self.assertLess(end_2020_cached, end_2020_no_cache, "2020 was not cached")

        with self.subTest():
            self.assertLess(end_2019_cached, end_2019_no_cache, "2019 was not cached")

        with self.subTest():
            self.assertTrue(all(df_2020_orig == df_2020_cached), "2020 cached copy and downloaded copy are not the same")

        with self.subTest():
            self.assertTrue(all(df_2019_orig == df_2019_cached), "2019 cached copy and downloaded copy are not the same")



        

