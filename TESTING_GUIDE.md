# Unit Testing Guide: Understanding Mocking

## What is Mocking?

**Mocking** is a testing technique where you replace real dependencies (like API calls, database queries, or external functions) with fake "mock" versions that you control. This lets you:

1. **Test in isolation** - Test only your code, not external services
2. **Control outputs** - Make the mock return exactly what you want
3. **Test error cases** - Simulate failures without actually breaking things
4. **Run tests fast** - No waiting for real network calls

## Why Mock METAR Data?

In our METAR app, we have three external dependencies:
- `fetch_metar()` - Makes a network call to NOAA API
- `parse_metar()` - Complex parsing logic
- `decode_to_english()` - Decoding logic

When testing `app.py`, we **don't want to**:
- ❌ Make real HTTP requests (slow, requires internet, might fail)
- ❌ Depend on NOAA's API being up
- ❌ Test the parsing logic again (that should have its own tests)

We **want to**:
- ✅ Test that our Flask routes work correctly
- ✅ Test input validation
- ✅ Test error handling
- ✅ Control exactly what data is returned

## How Mocking Works: Step-by-Step Example

### Example 1: Simple Mock

```python
@patch('app.fetch_metar')  # Replace fetch_metar with a mock
def test_successful_metar_fetch(mock_fetch):
    # 1. Control what the mock returns
    mock_fetch.return_value = "KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034"
    
    # 2. Make a request to your Flask app
    response = self.client.post('/', data={'icao_code': 'KJFK'})
    
    # 3. Verify it worked
    assert response.status_code == 200
    
    # 4. Verify the mock was called correctly
    mock_fetch.assert_called_once_with('KJFK')
```

**What happens:**
1. `@patch('app.fetch_metar')` - Python replaces the real `fetch_metar` function with a mock
2. `mock_fetch.return_value = ...` - We tell the mock what to return
3. When `app.py` calls `fetch_metar('KJFK')`, it gets our fake data instead of making a real API call
4. We verify the app behaved correctly with that data

### Example 2: Multiple Mocks (Chained Dependencies)

```python
@patch('app.fetch_metar')
@patch('app.parse_metar')
@patch('app.decode_to_english')
def test_full_flow(mock_decode, mock_parse, mock_fetch):
    # Mock the raw METAR
    mock_fetch.return_value = "KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034"
    
    # Mock the parsed data
    mock_parse.return_value = {
        'station': 'KJFK',
        'time': 'Day 24, 18:51 UTC',
        'temperature': -4,
        'dewpoint': -17
    }
    
    # Mock the decoded English
    mock_decode.return_value = [
        'Airport: KJFK | Observed: Day 24, 18:51 UTC',
        'Temperature: -4°C | Dewpoint: -17°C'
    ]
    
    response = self.client.post('/', data={'icao_code': 'KJFK'})
    
    # Verify all mocks were called in order
    mock_fetch.assert_called_once_with('KJFK')
    mock_parse.assert_called_once_with('KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034')
    mock_decode.assert_called_once()
```

**Flow:**
```
User submits 'KJFK'
    ↓
app.py calls fetch_metar('KJFK')
    ↓ (mock returns fake METAR string)
app.py calls parse_metar(raw_metar)
    ↓ (mock returns fake parsed dict)
app.py calls decode_to_english(parsed_data)
    ↓ (mock returns fake English list)
app.py renders template with results
    ↓
We verify the response
```

**Important:** Note the order of decorators vs parameters:
```python
@patch('app.fetch_metar')      # Last decorator
@patch('app.parse_metar')      # Middle decorator
@patch('app.decode_to_english') # First decorator
def test_full_flow(mock_decode, mock_parse, mock_fetch):  # Reverse order!
    #                ↑ first     ↑ middle    ↑ last
```

Decorators are applied **bottom-up**, but parameters are **left-to-right**.

### Example 3: Simulating Errors

```python
@patch('app.fetch_metar')
def test_network_error(mock_fetch):
    # Make the mock raise an exception instead of returning data
    mock_fetch.side_effect = Exception("Network timeout")
    
    response = self.client.post('/', data={'icao_code': 'KJFK'})
    
    # Verify the error is handled gracefully
    assert b'Error processing METAR data' in response.data
    assert b'Network timeout' in response.data
```

**What happens:**
- `side_effect = Exception(...)` - Mock raises an error instead of returning data
- We verify that `app.py` catches the error and shows it to the user

### Example 4: Return None (No Data Found)

```python
@patch('app.fetch_metar')
def test_no_metar_data_found(mock_fetch):
    # Simulate airport exists but has no current METAR
    mock_fetch.return_value = None
    
    response = self.client.post('/', data={'icao_code': 'ZZZZ'})
    
    assert b'No METAR data found' in response.data
```

## Running the Tests

### Run all tests:
```bash
python -m pytest test_app.py -v
```

### Run a specific test:
```bash
python -m pytest test_app.py::TestMetarApp::test_successful_metar_fetch_kjfk -v
```

### Run with coverage:
```bash
python -m pytest test_app.py --cov=app --cov-report=html
```

### Run using unittest (alternative):
```bash
python -m unittest test_app.py
```

## Key Concepts

### 1. `@patch` Decorator
- **Location:** `@patch('app.fetch_metar')` - patches the function where it's used, not where it's defined
- Since `app.py` imports `from metar_decoder import fetch_metar`, we patch `app.fetch_metar`

### 2. `return_value` vs `side_effect`
- **`return_value`** - What the mock returns when called
  ```python
  mock_fetch.return_value = "METAR DATA"
  ```
- **`side_effect`** - Make the mock raise an error or do something custom
  ```python
  mock_fetch.side_effect = Exception("Error!")
  ```

### 3. Assertions on Mocks
- **`assert_called_once()`** - Verify it was called exactly once
- **`assert_called_once_with('KJFK')`** - Verify it was called with specific arguments
- **`assert_called()`** - Verify it was called at least once
- **`assert_not_called()`** - Verify it was never called

### 4. Flask Test Client
```python
self.client = app.test_client()
response = self.client.get('/')      # GET request
response = self.client.post('/', data={'key': 'value'})  # POST request
```

## Creating Your Own Test Cases

### Template for a New Test:

```python
@patch('app.fetch_metar')
@patch('app.parse_metar')
@patch('app.decode_to_english')
def test_your_scenario(self, mock_decode, mock_parse, mock_fetch):
    """Test description here."""
    
    # 1. Set up your mocks
    mock_fetch.return_value = "YOUR RAW METAR STRING"
    mock_parse.return_value = {
        'station': 'XXXX',
        # ... your parsed data
    }
    mock_decode.return_value = [
        'Line 1 of decoded output',
        'Line 2 of decoded output'
    ]
    
    # 2. Make the request
    response = self.client.post('/', data={'icao_code': 'XXXX'})
    
    # 3. Assert the results
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'Expected text', response.data)
    
    # 4. Verify mocks were called
    mock_fetch.assert_called_once_with('XXXX')
```

## Real METAR Examples for Testing

Here are some real METAR strings you can use in your tests:

### Clear Weather
```python
"KJFK 241851Z 31008KT 10SM FEW250 M04/M17 A3034"
# JFK, clear with few clouds, cold
```

### Rain
```python
"EGLL 241820Z 25015KT 5SM -RA BKN020 OVC040 12/10 Q1015"
# London Heathrow, light rain, broken clouds
```

### Heavy Rain and Thunderstorms
```python
"KATL 241852Z 18012KT 3SM +TSRA BKN015CB OVC025 24/22 A2990"
# Atlanta, heavy thunderstorm with rain
```

### Fog
```python
"EDDF 240620Z 00000KT 0200 FG VV002 04/04 Q1022"
# Frankfurt, heavy fog, calm winds, very low visibility
```

### Snow
```python
"CYYZ 241900Z 36015G25KT 1SM -SN BKN008 OVC015 M08/M10 A2980"
# Toronto, light snow, gusty winds
```

### Calm and Clear
```python
"KSFO 241856Z 30012KT 10SM CLR 18/12 A3012"
# San Francisco, clear skies
```

## What Gets Tested vs What Doesn't

### ✅ We Test in `test_app.py`:
- Flask routing (`/` endpoint)
- Input validation (empty, too short, too long)
- Error handling (network errors, parsing errors)
- Response rendering
- HTTP status codes

### ❌ We DON'T Test in `test_app.py`:
- Real METAR parsing (that's for `test_metar_decoder.py`)
- Real API calls to NOAA
- Actual network behavior
- The correctness of decoding logic

## Next Steps

1. **Run the tests**: `python -m pytest test_app.py -v`
2. **Add more test cases** for edge cases you think of
3. **Create `test_metar_decoder.py`** to test the parsing logic separately (without mocks!)
4. **Check coverage**: `pytest --cov=app test_app.py`

## Common Questions

**Q: Why mock if we need to test the real thing eventually?**
A: You test the real thing in integration tests. Unit tests focus on one piece at a time.

**Q: What if my mock data is wrong?**
A: That's why you also have integration tests with real data. Unit tests verify logic, integration tests verify the system works together.

**Q: When should I NOT use mocks?**
A: When testing the thing itself (e.g., testing `parse_metar` should use real METAR strings, not mocks).

**Q: How do I know what to return from the mock?**
A: Look at what the real function returns. For `fetch_metar`, it returns a string. For `parse_metar`, it returns a dict.
