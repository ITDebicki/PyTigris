import unittest
import pytigris

class TractTests(unittest.TestCase):

    def tract(self, year = None, cb = False, state = None):
        df = pytigris.get_tracts(state = state, year = year, cb = cb)
        self.assertTrue(len(df) > 0, f"state(year = {year}, cb = {cb}) does not return full dataframe")

    def test_cb_tract_all(self):
        self.tract(year = 2019, cb = True)

    def test_cb_tract(self):
        for year in [1990, 2000, 2010, 2013, 2015, None]:
            with self.subTest(f"Year = {year}"):
                self.tract(state = 'ma', year = year, cb = True)

    def test_tract(self):
        for year in [2000, 2008, 2009, 2010, 2014, None]:
            with self.subTest(f"Year = {year}"):
                self.tract(state = 'ma', year = year)
    
    def test_tract_filtering_list(self):
        df_orig = pytigris.get_tracts(year = 2020, state = 'az')
        df_filtered = pytigris.get_tracts(state = 'az', counties = ['Coconino County', '007'], year = 2020)
        self.assertGreater(len(df_filtered), 0, "Filtering failed: removed all tracts (county list)")
        self.assertLess(len(df_filtered), len(df_orig), "filtering counties by counties failed (county list)")

    def test_tract_filtering_single(self):
        df_orig = pytigris.get_tracts(year = 2020, state = 'az')
        df_filtered = pytigris.get_tracts(state = 'az', counties = 'Coconino', year = 2020)
        self.assertGreater(len(df_filtered), 0, "Filtering failed: removed all tracts (county name)")
        self.assertLess(len(df_filtered), len(df_orig), "Filtering counties by counties failed (county name)")

    def test_value_errors(self):
        with self.assertRaises(ValueError):
            for year in [1990, 1995, 2002, 2005]:
                pytigris.get_tracts(year = year)

    def test_value_errors_cb(self):
        with self.assertRaises(ValueError):
            for year in [1995, 2002, 2005, 2012]:
                pytigris.get_tracts(year = year)

    def test_validate_county_fips_ak(self):
        self.assertEqual(pytigris.util.validate_county('01', '007'), '007', "County FIPS validation failed for FIPS value")
    
    def test_validate_county_name_exact_camel(self):
        self.assertEqual(pytigris.util.validate_county('GA', 'Haralson County'), '143', "County FIPS validation failed for camel case name")

    def test_validate_county_name_exact_lower(self):
        self.assertEqual(pytigris.util.validate_county('ID', 'power county'), '077', "County FIPS validation failed for lower case name")

    def test_validate_county_name_exact_upper(self):
        self.assertEqual(pytigris.util.validate_county('IL', "CRAWFORD COUNTY"), '033', "County FIPS validation failed for upper case name")

    def test_validate_county_name_approx_camel(self):
        self.assertEqual(pytigris.util.validate_county('GA', 'Haralson'), '143', "County FIPS validation failed for camel case name")

    def test_validate_county_name_approx_lower(self):
        self.assertEqual(pytigris.util.validate_county('ID', 'power'), '077', "County FIPS validation failed for lower case name")

    def test_validate_county_name_approx_upper(self):
        self.assertEqual(pytigris.util.validate_county('IL', "CRAWFORD"), '033', "County FIPS validation failed for upper case name")

    def test_valildate_county_invalid_fips(self):
        with self.assertRaises(ValueError):
            pytigris.util.validate_county('CA', '16')
        
    def test_valildate_county_invalid_name(self):
        with self.assertRaises(ValueError):
            pytigris.util.validate_county('KY', 'Berkshire')

    def test_valildate_county_name_too_many(self):
        with self.assertRaises(ValueError):
            pytigris.util.validate_county('LA', 'St.')
            