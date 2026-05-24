# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask web application that fetches and decodes METAR (Meteorological Aerodrome Report) weather data from airports worldwide. The application converts cryptic METAR format into human-readable English using metric units.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run Flask development server
python app.py

# The application will be available at http://localhost:5000
```

### Testing the Application
Test with these sample airport codes:
- **KJFK** - New York JFK
- **EGLL** - London Heathrow
- **YSSY** - Sydney Airport
- **EDDF** - Frankfurt Airport

## Architecture

### File Structure
```
.
├── app.py                  # Flask application with single route
├── metar_decoder.py        # METAR fetching, parsing, and decoding
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Single-page UI
└── static/
    └── style.css          # Styling
```

### Core Components

**app.py**
- Single route `/` handles both GET (display form) and POST (process request)
- Error handling for invalid codes, network issues, and parsing failures
- Renders results using Flask templates

**metar_decoder.py**
- `fetch_metar(icao_code)` - Fetches METAR from NOAA Aviation Weather Center API
- `parse_metar(raw_metar)` - Parses raw METAR string into structured data
- `decode_to_english(parsed_data)` - Converts parsed data to human-readable format

### METAR Data Source

Uses NOAA Aviation Weather Center public API:
- Endpoint: `https://aviationweather.gov/api/data/metar?ids={ICAO_CODE}&format=raw`
- No API key required
- Returns raw METAR text

### METAR Parsing Logic

The parser extracts these components in order:
1. **Station identifier** (4-letter ICAO code)
2. **Time** (DDHHmmZ format)
3. **Wind** (direction, speed, gusts)
4. **Visibility** (statute miles or meters)
5. **Weather phenomena** (rain, snow, fog, etc.)
6. **Sky conditions** (cloud coverage and altitude)
7. **Temperature/Dewpoint** (°C)
8. **Pressure** (altimeter setting)

### Metric Conversions

All measurements are converted to metric:
- **Temperature**: Already in °C (METAR standard)
- **Pressure**: inches Hg → hPa (×33.8639)
- **Visibility**: statute miles → km (×1.60934)
- **Wind speed**: knots → km/h (×1.852)
- **Altitude**: feet → meters (×0.3048)

### METAR Format Reference

Example: `KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034`

Decoded:
- **KJFK** - Airport code (JFK)
- **241851Z** - 24th day, 18:51 UTC
- **31008KT** - Wind from 310° at 8 knots
- **10SM** - 10 statute miles visibility
- **FEW250** - Few clouds at 25,000 feet
- **M04/M17** - Temperature -4°C, Dewpoint -17°C
- **A3034** - Altimeter 30.34 inches Hg

## Adding Features

### Adding New Weather Phenomena
Update the `weather_codes` dictionary in `metar_decoder.py:parse_metar()` with new codes and their meanings.

### Adding New Cloud Types
Update the `cloud_coverage` dictionary in `metar_decoder.py:parse_metar()` with new coverage types.

### Improving Parsing
The METAR parser processes tokens sequentially. To add new fields, insert parsing logic at the appropriate position in the token sequence within `parse_metar()`.
