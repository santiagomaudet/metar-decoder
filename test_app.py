"""
Unit tests for the METAR decoder Flask application.

These tests use mocking to isolate app.py from external dependencies
(network calls, METAR parsing logic) and test the Flask routes in isolation.
"""

import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestMetarApp(unittest.TestCase):
    """Test cases for the METAR decoder Flask application."""

    def setUp(self):
        """Set up test client before each test."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    # ========================================================================
    # GET Request Tests
    # ========================================================================

    def test_get_request_shows_form(self):
        """Test that GET request displays the empty form."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'METAR', response.data)

    # ========================================================================
    # Input Validation Tests
    # ========================================================================

    def test_empty_airport_code(self):
        """Test that submitting an empty code shows an error."""
        response = self.client.post('/', data={'icao_code': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter an airport code', response.data)

    def test_whitespace_only_code(self):
        """Test that submitting only whitespace shows an error."""
        response = self.client.post('/', data={'icao_code': '   '})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter an airport code', response.data)

    def test_code_too_short(self):
        """Test that codes with fewer than 4 characters are rejected."""
        response = self.client.post('/', data={'icao_code': 'JFK'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'must be 4 characters', response.data)

    def test_code_too_long(self):
        """Test that codes with more than 4 characters are rejected."""
        response = self.client.post('/', data={'icao_code': 'KJFKX'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'must be 4 characters', response.data)

    def test_lowercase_code_normalized(self):
        """Test that lowercase codes are converted to uppercase."""
        with patch('app.fetch_metar') as mock_fetch:
            mock_fetch.return_value = "KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034"

            with patch('app.parse_metar') as mock_parse:
                mock_parse.return_value = {'station': 'KJFK'}

                with patch('app.decode_to_english') as mock_decode:
                    mock_decode.return_value = ['Test output']

                    response = self.client.post('/', data={'icao_code': 'kjfk'})
                    # Verify that fetch_metar was called with uppercase
                    mock_fetch.assert_called_once_with('KJFK')

    # ========================================================================
    # Successful METAR Fetch Tests (with Mock Data)
    # ========================================================================

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    @patch('app.decode_to_english')
    def test_successful_metar_fetch_kjfk(self, mock_decode, mock_parse, mock_fetch):
        """
        Test successful METAR fetch for JFK airport with mock data.

        This test simulates a complete successful flow:
        1. User submits 'KJFK'
        2. fetch_metar returns raw METAR string
        3. parse_metar returns structured data
        4. decode_to_english returns human-readable text
        5. Page displays results
        """
        # Mock raw METAR data from NOAA (what fetch_metar would return)
        mock_fetch.return_value = "KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034"

        # Mock parsed data (what parse_metar would return)
        mock_parse.return_value = {
            'raw': 'KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034',
            'station': 'KJFK',
            'time': 'Day 24, 18:51 UTC',
            'wind': {'direction': '310', 'speed_kmh': 14.8, 'gust_kmh': None},
            'visibility': 16.1,
            'weather': [],
            'clouds': [{'coverage': 'Few clouds', 'altitude_m': 7620}],
            'temperature': -4,
            'dewpoint': -17,
            'pressure': 1027.6
        }

        # Mock decoded human-readable text (what decode_to_english would return)
        mock_decode.return_value = [
            'Airport: KJFK | Observed: Day 24, 18:51 UTC',
            'Wind: From 310° at 14.8 km/h',
            'Visibility: 16.1 km',
            'Clouds: Few clouds at 7,620 meters',
            'Temperature: -4°C | Dewpoint: -17°C',
            'Pressure: 1027.6 hPa'
        ]

        # Make request
        response = self.client.post('/', data={'icao_code': 'KJFK'})

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'KJFK', response.data)
        self.assertIn(b'Airport: KJFK', response.data)
        self.assertIn(b'Wind: From 310', response.data)

        # Verify mocks were called correctly
        mock_fetch.assert_called_once_with('KJFK')
        mock_parse.assert_called_once_with('KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034')
        mock_decode.assert_called_once()

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    @patch('app.decode_to_english')
    def test_successful_metar_with_weather(self, mock_decode, mock_parse, mock_fetch):
        """Test METAR with weather phenomena (rain, thunderstorms)."""
        # EGLL (London Heathrow) with rain
        mock_fetch.return_value = "EGLL 241820Z 25015KT 5SM -RA BKN020 OVC040 12/10 Q1015"

        mock_parse.return_value = {
            'raw': 'EGLL 241820Z 25015KT 5SM -RA BKN020 OVC040 12/10 Q1015',
            'station': 'EGLL',
            'time': 'Day 24, 18:20 UTC',
            'wind': {'direction': '250', 'speed_kmh': 27.8, 'gust_kmh': None},
            'visibility': 8.0,
            'weather': ['light rain'],
            'clouds': [
                {'coverage': 'Broken clouds', 'altitude_m': 610},
                {'coverage': 'Overcast', 'altitude_m': 1219}
            ],
            'temperature': 12,
            'dewpoint': 10,
            'pressure': 1015
        }

        mock_decode.return_value = [
            'Airport: EGLL | Observed: Day 24, 18:20 UTC',
            'Wind: From 250° at 27.8 km/h',
            'Visibility: 8.0 km',
            'Weather: Light rain',
            'Clouds: Broken clouds at 610 meters, Overcast at 1,219 meters',
            'Temperature: 12°C | Dewpoint: 10°C',
            'Pressure: 1015 hPa'
        ]

        response = self.client.post('/', data={'icao_code': 'EGLL'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EGLL', response.data)
        self.assertIn(b'Light rain', response.data)

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    @patch('app.decode_to_english')
    def test_successful_metar_with_gusts(self, mock_decode, mock_parse, mock_fetch):
        """Test METAR with wind gusts."""
        mock_fetch.return_value = "YSSY 242030Z 18025G40KT 9999 FEW030 22/18 Q1008"

        mock_parse.return_value = {
            'raw': 'YSSY 242030Z 18025G40KT 9999 FEW030 22/18 Q1008',
            'station': 'YSSY',
            'time': 'Day 24, 20:30 UTC',
            'wind': {'direction': '180', 'speed_kmh': 46.3, 'gust_kmh': 74.1},
            'visibility': 9.999,
            'weather': [],
            'clouds': [{'coverage': 'Few clouds', 'altitude_m': 914}],
            'temperature': 22,
            'dewpoint': 18,
            'pressure': 1008
        }

        mock_decode.return_value = [
            'Airport: YSSY | Observed: Day 24, 20:30 UTC',
            'Wind: From 180° at 46.3 km/h, gusting to 74.1 km/h',
            'Visibility: 9.999 km',
            'Clouds: Few clouds at 914 meters',
            'Temperature: 22°C | Dewpoint: 18°C',
            'Pressure: 1008 hPa'
        ]

        response = self.client.post('/', data={'icao_code': 'YSSY'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'gusting', response.data)

    # ========================================================================
    # Error Handling Tests
    # ========================================================================

    @patch('app.fetch_metar')
    def test_no_metar_data_found(self, mock_fetch):
        """Test when the airport code is valid but no METAR data exists."""
        # fetch_metar returns None when no data found
        mock_fetch.return_value = None

        response = self.client.post('/', data={'icao_code': 'ZZZZ'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No METAR data found for airport code: ZZZZ', response.data)
        mock_fetch.assert_called_once_with('ZZZZ')

    @patch('app.fetch_metar')
    def test_network_error(self, mock_fetch):
        """Test handling of network errors when fetching METAR."""
        # Simulate a network error
        mock_fetch.side_effect = Exception("Network timeout")

        response = self.client.post('/', data={'icao_code': 'KJFK'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error processing METAR data', response.data)
        self.assertIn(b'Network timeout', response.data)

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    def test_parsing_error(self, mock_parse, mock_fetch):
        """Test handling of METAR parsing errors."""
        mock_fetch.return_value = "INVALID METAR FORMAT"
        # Simulate a parsing error
        mock_parse.side_effect = Exception("Unable to parse METAR")

        response = self.client.post('/', data={'icao_code': 'KJFK'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error processing METAR data', response.data)
        self.assertIn(b'Unable to parse METAR', response.data)

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    @patch('app.decode_to_english')
    def test_decoding_error(self, mock_decode, mock_parse, mock_fetch):
        """Test handling of errors during decoding."""
        mock_fetch.return_value = "KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034"
        mock_parse.return_value = {'station': 'KJFK'}
        # Simulate a decoding error
        mock_decode.side_effect = Exception("Decoding failed")

        response = self.client.post('/', data={'icao_code': 'KJFK'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error processing METAR data', response.data)
        self.assertIn(b'Decoding failed', response.data)

    # ========================================================================
    # Edge Cases
    # ========================================================================

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    @patch('app.decode_to_english')
    def test_metar_with_special_characters(self, mock_decode, mock_parse, mock_fetch):
        """Test that special characters in input are handled."""
        # Input has spaces and special chars that should be stripped
        mock_fetch.return_value = "KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034"
        mock_parse.return_value = {'station': 'KJFK'}
        mock_decode.return_value = ['Test output']

        response = self.client.post('/', data={'icao_code': '  kjfk  '})

        self.assertEqual(response.status_code, 200)
        # Should normalize to uppercase KJFK
        mock_fetch.assert_called_once_with('KJFK')


# ========================================================================
# Sample Mock Data Reference
# ========================================================================
# You can use these as templates for creating more test cases

MOCK_METAR_SAMPLES = {
    'KJFK_CLEAR': {
        'raw': 'KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034',
        'description': 'Clear conditions at JFK, cold temperature',
    },
    'EGLL_RAIN': {
        'raw': 'EGLL 241820Z 25015KT 5SM -RA BKN020 OVC040 12/10 Q1015',
        'description': 'Light rain at London Heathrow',
    },
    'YSSY_WINDY': {
        'raw': 'YSSY 242030Z 18025G40KT 9999 FEW030 22/18 Q1008',
        'description': 'Gusty winds at Sydney',
    },
    'EDDF_FOG': {
        'raw': 'EDDF 240620Z 00000KT 0200 FG VV002 04/04 Q1022',
        'description': 'Heavy fog at Frankfurt, calm winds',
    },
    'KSFO_CLEAR': {
        'raw': 'KSFO 241856Z 30012KT 10SM CLR 18/12 A3012',
        'description': 'Clear skies at San Francisco',
    }
}


if __name__ == '__main__':
    unittest.main()
