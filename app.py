"""
METAR Weather Decoder Web Application.

A Flask web application that fetches and decodes METAR (Meteorological Aerodrome
Report) weather data from airports worldwide, converting the cryptic standardized
format into human-readable English with metric units.
"""

from flask import Flask, render_template, request
from metar_decoder import fetch_metar, parse_metar, decode_to_english

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handle the main page route for METAR lookup.

    GET: Display the empty form for entering an airport code.
    POST: Process the submitted ICAO code, fetch METAR data, decode it,
          and display the results.

    Returns:
        Rendered HTML template with form and optional results or error messages.
    """
    if request.method == 'POST':
        # Normalize input: strip whitespace and convert to uppercase
        icao_code = request.form.get('icao_code', '').strip().upper()

        # Validate input
        if not icao_code:
            return render_template('index.html', error="Please enter an airport code")

        # ICAO codes are always 4 characters (e.g., KJFK, SAEZ)
        if len(icao_code) != 4:
            return render_template('index.html', error="Airport code must be 4 characters (ICAO format)")

        try:
            # Fetch raw METAR data from NOAA API
            raw_metar = fetch_metar(icao_code)

            if not raw_metar:
                return render_template('index.html',
                                       error=f"No METAR data found for airport code: {icao_code}")

            # Parse the raw METAR string into structured data
            parsed_data = parse_metar(raw_metar)

            # Convert parsed data to human-readable format
            decoded_lines = decode_to_english(parsed_data)

            return render_template('index.html',
                                   icao_code=icao_code,
                                   raw_metar=raw_metar,
                                   decoded_lines=decoded_lines)

        except Exception as e:
            # Handle any errors during fetching or parsing
            return render_template('index.html',
                                   error=f"Error processing METAR data: {str(e)}")

    # GET request: show empty form
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
