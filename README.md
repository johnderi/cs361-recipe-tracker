# cs361-recipe-tracker

## Prerequisites

- Python 3.7+
- pip package manager

## Installation

1. Clone this repository
2. Install required dependencies:
```bash
pip install fastapi uvicorn requests
```

## Running the Microservice

Start the server by running:
```bash
uvicorn MeasurementConverter:app --reload --host 127.0.0.1 --port 8000
```

The service will be available at `http://127.0.0.1:8000`

## Communication Contract

This microservice provides three RESTful endpoints that accept JSON requests and return JSON responses.

### 1. Convert Measurements Endpoint

**Endpoint:** `POST /convert_measurements`

**Purpose:** Convert a measurement value between compatible units (volume-to-volume or weight-to-weight)

#### Request Format
```json
{
    "value": float,
    "from_unit": string,
    "to_unit": string
}
```

**Supported Volume Units:** `tsp`, `tbsp`, `floz`, `cup`, `pt`, `qt`, `gal`, `ml`, `l`

**Supported Weight Units:** `mg`, `g`, `kg`, `oz`, `lb`

#### Example Request (Python)
```python
import requests

response = requests.post("http://127.0.0.1:8000/convert_measurements", 
    json={
        "value": 2,
        "from_unit": "cup",
        "to_unit": "ml"
    }
)
result = response.json()
```

#### Response Format
**Success:**
```json
{
    "success": true,
    "original": {
        "value": 2,
        "unit": "cup"
    },
    "converted": {
        "value": 473.18,
        "unit": "ml"
    }
}
```

**Error (incompatible units):**
```json
{
    "success": false,
    "error": "Invalid measurement conversion"
}
```

### 2. Scale Quantities Endpoint

**Endpoint:** `POST /scale_quantities`

**Purpose:** Scale multiple ingredient quantities by a specified factor

#### Request Format
```json
{
    "scale_factor": float,
    "ingredients": [
        {
            "name": string,
            "value": float,
            "unit": string
        }
    ]
}
```

#### Example Request (Python)
```python
import requests

response = requests.post("http://127.0.0.1:8000/scale_quantities",
    json={
        "scale_factor": 2,
        "ingredients": [
            {"name": "Flour", "value": 1, "unit": "cup"},
            {"name": "Sugar", "value": 100, "unit": "g"}
        ]
    }
)
result = response.json()
```

#### Response Format
**Success:**
```json
{
    "success": true,
    "scale_factor": 2,
    "original": [
        {"name": "Flour", "value": 1, "unit": "cup"},
        {"name": "Sugar", "value": 100, "unit": "g"}
    ],
    "scaled": [
        {
            "name": "Flour",
            "original": {"value": 1, "unit": "cup"},
            "scaled": {"value": 2, "unit": "cup"}
        },
        {
            "name": "Sugar",
            "original": {"value": 100, "unit": "g"},
            "scaled": {"value": 200, "unit": "g"}
        }
    ]
}
```

### 3. Convert Temperature Endpoint

**Endpoint:** `POST /convert_temperature`

**Purpose:** Convert temperature between Fahrenheit and Celsius

#### Request Format
```json
{
    "value": float,
    "from_unit": string,
    "to_unit": string
}
```

**Supported Units:** `fahrenheit`, `celsius`

#### Example Request (Python)
```python
import requests

response = requests.post("http://127.0.0.1:8000/convert_temperature",
    json={
        "value": 350,
        "from_unit": "fahrenheit",
        "to_unit": "celsius"
    }
)
result = response.json()
```

#### Response Format
**Success:**
```json
{
    "success": true,
    "original": {
        "value": 350,
        "unit": "fahrenheit"
    },
    "converted": {
        "value": 177,
        "unit": "celsius"
    }
}
```

**Error (below absolute zero):**
```json
{
    "success": false,
    "error": "Temperature cannot be below absolute zero"
}
```

## UML Sequence Diagram

```
┌─────────┐     ┌────────────────┐     ┌─────────────────┐
│ Client  │     │ Measurement    │     │ Conversion      │
│ Program │     │ Converter API  │     │ Logic           │
└────┬────┘     └───────┬────────┘     └────────┬────────┘
     │                  │                        │
     │   POST Request   │                        │
     │ ────────────────>│                        │
     │  {JSON Payload}  │                        │
     │                  │                        │
     │                  │  Validate Input        │
     │                  │ ──────────────────────>│
     │                  │                        │
     │                  │  Validation Result     │
     │                  │ <──────────────────────│
     │                  │                        │
     │                  │  Convert Values        │
     │                  │ ──────────────────────>│
     │                  │                        │
     │                  │  Converted Result      │
     │                  │ <──────────────────────│
     │                  │                        │
     │  JSON Response   │                        │
     │ <────────────────│                        │
     │   {success,      │                        │
     │    data/error}   │                        │
     │                  │                        │
```

## Testing the Microservice

Use the provided `MeasurementConverter_Test.py` script to test all endpoints:

```bash
python MeasurementConverter_Test.py
```

This will execute test cases for all three endpoints and display the responses.

## Error Handling

The microservice handles the following error cases:
- Incompatible unit conversions (e.g., volume to weight)
- Invalid unit names
- Temperatures below absolute zero
- Missing or malformed request data

## Notes

- All decimal values are rounded to 2 decimal places for readability
- Temperature conversions are rounded to the nearest whole number
- The scale_quantities endpoint automatically selects the most practical unit for scaled values
- The service currently does not support density-based conversions between volume and weight
