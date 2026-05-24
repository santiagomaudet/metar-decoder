# METAR Weather Decoder

A Flask web application that fetches and decodes METAR (Meteorological Aerodrome Report) weather data from airports worldwide. METAR reports use a cryptic standardized format that can be difficult to understand. This app translates them into plain English with metric units.

## Features

- ✈️ **Live METAR Data** - Fetches current weather reports from NOAA Aviation Weather Center
- 🌍 **Worldwide Coverage** - Supports any airport with an ICAO code
- 📊 **Metric Units** - All measurements in °C, km, km/h, hPa, and meters
- 🎯 **Complete Decoding** - Parses wind, visibility, weather phenomena, clouds, temperature, and pressure
- 🖥️ **Clean Interface** - Simple, responsive web interface
- 📖 **Human-Readable** - Converts cryptic codes into plain English

## Example

**Input:** `SAEZ` (Ezeiza International Airport, Buenos Aires)

**Raw METAR:**
```
METAR SAEZ 241300Z 09004KT 5000 BR OVC011 11/10 Q1024 NOSIG
```

**Decoded Output:**
- Airport: SAEZ | Observed: Day 24, 13:00 UTC
- Wind: From 090° at 7.4 km/h
- Visibility: 5.0 km
- Weather: Mist
- Clouds: Overcast at 335 meters
- Temperature: 11°C | Dewpoint: 10°C
- Pressure: 1024 hPa

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/metar-reader.git
   cd metar-reader
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   
   Navigate to `http://localhost:5000`

## Usage

1. Enter a 4-letter ICAO airport code (e.g., `KJFK`, `EGLL`, `SAEZ`)
2. Click "Get Weather"
3. View the raw METAR and decoded weather information

### ICAO Code Examples

| Airport | ICAO Code | City |
|---------|-----------|------|
| John F. Kennedy International | `KJFK` | New York, USA |
| London Heathrow | `EGLL` | London, UK |
| Ezeiza International | `SAEZ` | Buenos Aires, Argentina |
| Sydney Airport | `YSSY` | Sydney, Australia |
| Frankfurt Airport | `EDDF` | Frankfurt, Germany |
| Tokyo Haneda | `RJTT` | Tokyo, Japan |

**Note:** Use ICAO codes (4 letters), not IATA codes (3 letters). For example, use `SAEZ` instead of `EZE`.

## How It Works

1. **Fetch** - Retrieves current METAR data from the NOAA Aviation Weather Center API
2. **Parse** - Breaks down the METAR string into components (wind, visibility, clouds, etc.)
3. **Convert** - Translates measurements to metric units
4. **Decode** - Converts cryptic codes into human-readable English

## Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS
- **API:** NOAA Aviation Weather Center
- **Parsing:** Custom regex-based METAR parser

## Project Structure

```
.
├── app.py                  # Flask application
├── metar_decoder.py        # METAR fetching and parsing logic
├── test_app.py             # Unit tests for Flask app
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface template
├── static/
│   └── style.css          # Styling
├── TESTING_GUIDE.md       # Detailed testing documentation
├── CLAUDE.md              # Project instructions for Claude Code
└── README.md              # This file
```

## Testing

This project includes comprehensive unit tests to ensure reliability and correctness.

### Running Tests

1. **Install testing dependencies** (if not already installed)
   ```bash
   pip install -r requirements.txt
   ```

2. **Run all tests**
   ```bash
   pytest test_app.py -v
   ```

3. **Run with coverage report**
   ```bash
   pytest test_app.py --cov=app --cov-report=html
   ```
   Then open `htmlcov/index.html` in your browser to see detailed coverage.

4. **Run a specific test**
   ```bash
   pytest test_app.py::TestMetarApp::test_successful_metar_fetch_kjfk -v
   ```

### Test Coverage

The test suite includes **15 test cases** covering:

- ✅ **Input Validation** - Empty codes, incorrect lengths, whitespace handling
- ✅ **Successful METAR Fetches** - Multiple airport scenarios with different weather conditions
- ✅ **Error Handling** - Network errors, parsing failures, missing data
- ✅ **Weather Scenarios** - Clear skies, rain, wind gusts, fog, thunderstorms
- ✅ **Edge Cases** - Special characters, case normalization

### Understanding the Tests

The tests use **mocking** to isolate the Flask application from external dependencies. This means:

- 🎭 **No real API calls** - Tests run instantly without internet
- 🎯 **Controlled scenarios** - We control exactly what data is returned
- 🛡️ **Safe error testing** - Can simulate failures without breaking anything
- ⚡ **Fast execution** - Complete test suite runs in seconds

**Example test with mock data:**
```python
@patch('app.fetch_metar')
def test_successful_metar_fetch(mock_fetch):
    # Control what the mock returns
    mock_fetch.return_value = "KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034"
    
    # Make request
    response = client.post('/', data={'icao_code': 'KJFK'})
    
    # Verify results
    assert response.status_code == 200
    assert b'KJFK' in response.data
```

For a detailed explanation of how mocking works and how to write your own tests, see **[TESTING_GUIDE.md](TESTING_GUIDE.md)**.

## METAR Format Reference

METAR reports follow a standardized format:

```
METAR KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034
```

- `METAR` - Report type
- `KJFK` - Station identifier (ICAO code)
- `241851Z` - Date/time (24th day, 18:51 UTC)
- `31008KT` - Wind (from 310°, 8 knots)
- `10SM` - Visibility (10 statute miles)
- `FEW250` - Clouds (few at 25,000 feet)
- `M04/M17` - Temperature/Dewpoint (-4°C / -17°C)
- `A3034` - Altimeter setting (30.34 inches Hg)

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- METAR data provided by [NOAA Aviation Weather Center](https://aviationweather.gov/)
- Built with [Flask](https://flask.palletsprojects.com/)

## Contact

For questions or feedback, please open an issue on GitHub.

---

**Disclaimer:** This application is for informational purposes only. Always consult official aviation weather sources for flight planning and operations.
