from flask import Flask, render_template, request
from metar_decoder import fetch_metar, parse_metar, decode_to_english

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        icao_code = request.form.get('icao_code', '').strip().upper()

        if not icao_code:
            return render_template('index.html', error="Please enter an airport code")

        if len(icao_code) != 4:
            return render_template('index.html', error="Airport code must be 4 characters (ICAO format)")

        try:
            # Fetch METAR data
            raw_metar = fetch_metar(icao_code)

            if not raw_metar:
                return render_template('index.html',
                                       error=f"No METAR data found for airport code: {icao_code}")

            # Parse and decode
            parsed_data = parse_metar(raw_metar)
            decoded_lines = decode_to_english(parsed_data)

            return render_template('index.html',
                                   icao_code=icao_code,
                                   raw_metar=raw_metar,
                                   decoded_lines=decoded_lines)

        except Exception as e:
            return render_template('index.html',
                                   error=f"Error processing METAR data: {str(e)}")

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
