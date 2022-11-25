import unittest
import pytigris

class StateValidateTests(unittest.TestCase):

    def test_validate_state_fips_ak(self):
        self.assertEqual(pytigris.util.validate_state('01'), '01', "State FIPS validation failed for AL (FIPS value passed)")
    
    def test_validate_state_name_lower(self):
        self.assertEqual(pytigris.util.validate_state('alaska'), '02', "State FIPS validation failed for AK (Name)")

    def test_validate_state_name_camel(self):
        self.assertEqual(pytigris.util.validate_state('Oregon'), '41', "State FIPS validation failed for Oregon (Name)")

    def test_validate_state_name_lower_with_space(self):
        self.assertEqual(pytigris.util.validate_state('district of columbia'), '11', "State FIPS validation failed for DC (Name)")

    def test_validate_state_name_upper(self):
        self.assertEqual(pytigris.util.validate_state('WYOMING'), '56', "State FIPS validation failed for WY (Upper case name passed)")

    def test_validate_state_abb_upper(self):
        self.assertEqual(pytigris.util.validate_state('AK'), '02', "State FIPS validation failed for AK (Upper case abbreviation passed)")

    def test_validate_state_abb_lower(self):
        self.assertEqual(pytigris.util.validate_state('wy'), '56', "State FIPS validation failed for WY (Lower case abbreviation passed)")

    def test_valildate_state_invalid_fips(self):
        with self.assertRaises(ValueError):
            pytigris.util.validate_state('5')
        
    def test_valildate_state_invalid_name(self):
        with self.assertRaises(ValueError):
            pytigris.util.validate_state('Saskatchewan')
    
    def test_valildate_state_invalid_abb(self):
        with self.assertRaises(ValueError):
            pytigris.util.validate_state('SA')

class CountyValidateTests(unittest.TestCase):

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
            