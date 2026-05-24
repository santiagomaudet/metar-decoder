import requests
import re
from datetime import datetime


def fetch_metar(icao_code):
    """Fetch METAR data from NOAA Aviation Weather Center."""
    url = f"https://aviationweather.gov/api/data/metar?ids={icao_code.upper()}&format=raw"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        metar_text = response.text.strip()

        if not metar_text or "No METAR" in metar_text or metar_text == "":
            return None

        return metar_text
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch METAR data: {str(e)}")


def parse_metar(raw_metar):
    """Parse raw METAR string into structured data."""
    parts = raw_metar.split()
    data = {
        'raw': raw_metar,
        'station': None,
        'time': None,
        'wind': None,
        'visibility': None,
        'weather': [],
        'clouds': [],
        'temperature': None,
        'dewpoint': None,
        'pressure': None
    }

    if not parts:
        return data

    idx = 0

    # Skip "METAR" keyword if present
    if parts[idx] == 'METAR':
        idx += 1

    # Station identifier (4 letters)
    if idx < len(parts) and len(parts[idx]) == 4 and parts[idx].isalpha():
        data['station'] = parts[idx]
        idx += 1

    # Time (DDHHmmZ)
    if idx < len(parts) and re.match(r'\d{6}Z', parts[idx]):
        time_str = parts[idx]
        day = time_str[0:2]
        hour = time_str[2:4]
        minute = time_str[4:6]
        data['time'] = f"Day {day}, {hour}:{minute} UTC"
        idx += 1

    # AUTO indicator (skip if present)
    if idx < len(parts) and parts[idx] == 'AUTO':
        idx += 1

    # Wind (e.g., 31008KT, 00000KT, VRB03KT)
    if idx < len(parts) and re.match(r'(VRB|\d{3})\d{2}(G\d{2})?KT', parts[idx]):
        wind_str = parts[idx]
        direction = wind_str[0:3]
        speed_match = re.search(r'(\d{2})(G(\d{2}))?KT', wind_str)
        if speed_match:
            speed_kt = int(speed_match.group(1))
            gust_kt = int(speed_match.group(3)) if speed_match.group(3) else None

            speed_kmh = round(speed_kt * 1.852, 1)
            gust_kmh = round(gust_kt * 1.852, 1) if gust_kt else None

            data['wind'] = {
                'direction': direction,
                'speed_kmh': speed_kmh,
                'gust_kmh': gust_kmh
            }
        idx += 1

    # Variable wind direction (e.g., 280V350)
    if idx < len(parts) and re.match(r'\d{3}V\d{3}', parts[idx]):
        idx += 1

    # Visibility
    if idx < len(parts):
        vis = parts[idx]
        # Statute miles (e.g., 10SM)
        if re.match(r'\d+SM', vis):
            miles = int(re.search(r'(\d+)SM', vis).group(1))
            data['visibility'] = round(miles * 1.60934, 1)
            idx += 1
        # Fractional miles (e.g., 1/2SM)
        elif re.match(r'\d+/\d+SM', vis):
            fraction = re.search(r'(\d+)/(\d+)SM', vis)
            miles = int(fraction.group(1)) / int(fraction.group(2))
            data['visibility'] = round(miles * 1.60934, 1)
            idx += 1
        # Meters (e.g., 9999)
        elif vis.isdigit() and len(vis) == 4:
            data['visibility'] = int(vis) / 1000
            idx += 1

    # Weather phenomena (e.g., -RA, TSRA, BR, FG)
    weather_codes = {
        'RA': 'rain', 'SN': 'snow', 'FG': 'fog', 'BR': 'mist',
        'HZ': 'haze', 'DZ': 'drizzle', 'TS': 'thunderstorm',
        'GR': 'hail', 'GS': 'small hail', 'SH': 'showers',
        'FZ': 'freezing', 'MI': 'shallow', 'BC': 'patches',
        'PR': 'partial', 'BL': 'blowing', 'DR': 'drifting'
    }

    while idx < len(parts):
        part = parts[idx]
        # Check if it's a weather phenomenon
        if re.match(r'^[+-]?(TS|SH|FZ|MI|BC|PR|BL|DR)?(RA|SN|FG|BR|HZ|DZ|GR|GS|PL|SG|IC|UP|VA|FC|SS|DS)+$', part):
            intensity = ''
            if part[0] == '+':
                intensity = 'heavy '
                part = part[1:]
            elif part[0] == '-':
                intensity = 'light '
                part = part[1:]

            # Decode weather codes
            decoded = []
            for code, meaning in weather_codes.items():
                if code in part:
                    decoded.append(meaning)

            if decoded:
                data['weather'].append(intensity + ' '.join(decoded))
            idx += 1
        else:
            break

    # Sky conditions (e.g., FEW250, SCT040, BKN015, OVC010)
    cloud_coverage = {
        'FEW': 'Few clouds',
        'SCT': 'Scattered clouds',
        'BKN': 'Broken clouds',
        'OVC': 'Overcast',
        'CLR': 'Clear',
        'SKC': 'Sky clear'
    }

    while idx < len(parts):
        part = parts[idx]
        if re.match(r'(FEW|SCT|BKN|OVC|CLR|SKC)(\d{3})?', part):
            coverage_match = re.search(r'(FEW|SCT|BKN|OVC|CLR|SKC)(\d{3})?', part)
            coverage = coverage_match.group(1)
            altitude_ft = int(coverage_match.group(2)) * 100 if coverage_match.group(2) else None
            altitude_m = round(altitude_ft * 0.3048) if altitude_ft else None

            data['clouds'].append({
                'coverage': cloud_coverage.get(coverage, coverage),
                'altitude_m': altitude_m
            })
            idx += 1
        else:
            break

    # Temperature and dewpoint (e.g., 18/14, M04/M17)
    if idx < len(parts):
        temp_match = re.match(r'(M?\d{2})/(M?\d{2})', parts[idx])
        if temp_match:
            temp_str = temp_match.group(1)
            dewpoint_str = temp_match.group(2)

            # M prefix means minus (negative)
            temp = int(temp_str.replace('M', '-'))
            dewpoint = int(dewpoint_str.replace('M', '-'))

            data['temperature'] = temp
            data['dewpoint'] = dewpoint
            idx += 1

    # Altimeter setting (e.g., A3034, Q1013)
    if idx < len(parts):
        pressure_match = re.match(r'A(\d{4})', parts[idx])
        if pressure_match:
            # Inches of mercury to hPa
            inches = int(pressure_match.group(1)) / 100
            data['pressure'] = round(inches * 33.8639, 1)
            idx += 1
        else:
            # QNH in hPa (e.g., Q1013)
            pressure_match = re.match(r'Q(\d{4})', parts[idx])
            if pressure_match:
                data['pressure'] = int(pressure_match.group(1))
                idx += 1

    return data


def decode_to_english(parsed_data):
    """Convert parsed METAR data to human-readable English."""
    lines = []

    # Station and time
    if parsed_data['station']:
        header = f"Airport: {parsed_data['station']}"
        if parsed_data['time']:
            header += f" | Observed: {parsed_data['time']}"
        lines.append(header)

    # Wind
    if parsed_data['wind']:
        wind = parsed_data['wind']
        if wind['direction'] == 'VRB':
            wind_desc = f"Wind: Variable at {wind['speed_kmh']} km/h"
        elif wind['direction'] == '000':
            wind_desc = "Wind: Calm"
        else:
            wind_desc = f"Wind: From {wind['direction']}° at {wind['speed_kmh']} km/h"

        if wind['gust_kmh']:
            wind_desc += f", gusting to {wind['gust_kmh']} km/h"

        lines.append(wind_desc)

    # Visibility
    if parsed_data['visibility'] is not None:
        lines.append(f"Visibility: {parsed_data['visibility']} km")

    # Weather
    if parsed_data['weather']:
        weather_desc = "Weather: " + ", ".join(parsed_data['weather']).capitalize()
        lines.append(weather_desc)

    # Clouds
    if parsed_data['clouds']:
        cloud_lines = []
        for cloud in parsed_data['clouds']:
            if cloud['altitude_m']:
                cloud_lines.append(f"{cloud['coverage']} at {cloud['altitude_m']:,} meters")
            else:
                cloud_lines.append(cloud['coverage'])
        lines.append("Clouds: " + ", ".join(cloud_lines))

    # Temperature and dewpoint
    if parsed_data['temperature'] is not None:
        temp_desc = f"Temperature: {parsed_data['temperature']}°C"
        if parsed_data['dewpoint'] is not None:
            temp_desc += f" | Dewpoint: {parsed_data['dewpoint']}°C"
        lines.append(temp_desc)

    # Pressure
    if parsed_data['pressure']:
        lines.append(f"Pressure: {parsed_data['pressure']} hPa")

    return lines
