import unittest
import pytigris

class BlockGroupTests(unittest.TestCase):

    def block_groups(self, year = None, cb = False, state = None):
        df = pytigris.get_block_groups(state = state, year = year, cb = cb)
        self.assertTrue(len(df) > 0, f"get_block_groups(state = {state}, year = {year}, cb = {cb}) does not return full dataframe")

    def test_cb_tract_all(self):
        self.block_groups(year = 2019, cb = True)

    def test_cb_tract(self):
        for year in [1990, 2000, 2010, 2013, 2015, None]:
            with self.subTest(f"Year = {year}"):
                self.block_groups(state = 'nm', year = year, cb = True)

    def test_tract(self):
        for year in [2000, 2008, 2009, 2010, 2014, None]:
            with self.subTest(f"Year = {year}"):
                self.block_groups(state = 'nm', year = year)
    
    def test_tract_filtering_list(self):
        df_orig = pytigris.get_block_groups(year = 2020, state = 'az')
        df_filtered = pytigris.get_block_groups(state = 'az', counties = ['Coconino County', '007'], year = 2020)
        self.assertGreater(len(df_filtered), 0, "Filtering failed: removed all block groups (county list)")
        self.assertLess(len(df_filtered), len(df_orig), "filtering counties by block groups failed (county list)")

    def test_tract_filtering_single(self):
        df_orig = pytigris.get_block_groups(year = 2020, state = 'az')
        df_filtered = pytigris.get_block_groups(state = 'az', counties = 'Coconino', year = 2020)
        self.assertGreater(len(df_filtered), 0, "Filtering failed: removed all block groups (county name)")
        self.assertLess(len(df_filtered), len(df_orig), "Filtering counties by block groups failed (county name)")

    def test_value_errors(self):
        for year in [1990, 1995, 2002, 2005]:
            with self.subTest():
                with self.assertRaises(ValueError):
                    pytigris.get_block_groups(year = year)

    def test_value_errors_cb(self):
        for year in [1995, 2002, 2005, 2012]:
            with self.subTest():
                with self.assertRaises(ValueError):
                    pytigris.get_block_groups(year = year, cb = True)

