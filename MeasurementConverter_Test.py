# ----- README -----
"""
Required installations:
    pip install requests

Ensure MeasurementConverter.py is running, then run this file!
"""

import requests

base_url = "http://127.0.0.1:8000"

# ----- /convert_measurements -----
print("Testing /convert_measurements (volume)")
response = requests.post(f"{base_url}/convert_measurements", json={
    "value": 2,
    "from_unit": "cup",
    "to_unit": "ml"
})
print(response.json(), "\n")

print("Testing /convert_measurements (weight)")
response = requests.post(f"{base_url}/convert_measurements", json={
    "value": 1,
    "from_unit": "lb",
    "to_unit": "kg"
})
print(response.json(), "\n")

print("Testing /convert_measurements (invalid)")
response = requests.post(f"{base_url}/convert_measurements", json={
    "value": 1,
    "from_unit": "cup",
    "to_unit": "kg"
})
print(response.json(), "\n")

# ----- /scale_quantities -----
print("Testing /scale_quantities")
response = requests.post(f"{base_url}/scale_quantities", json={
    "scale_factor": 2,
    "ingredients": [
        {"name": "Flour", "value": 1, "unit": "cup"},
        {"name": "Sugar", "value": 100, "unit": "g"}
    ]
})
print(response.json(), "\n")

# ----- /convert_temperature -----
print("Testing /convert_temperature (C -> F)")
response = requests.post(f"{base_url}/convert_temperature", json={
    "value": 0,
    "from_unit": "celsius",
    "to_unit": "fahrenheit"
})
print(response.json(), "\n")

print("Testing /convert_temperature (F -> C)")
response = requests.post(f"{base_url}/convert_temperature", json={
    "value": 32,
    "from_unit": "fahrenheit",
    "to_unit": "celsius"
})
print(response.json(), "\n")

print("Testing /convert_temperature (below absolute zero)")
response = requests.post(f"{base_url}/convert_temperature", json={
    "value": -500,
    "from_unit": "fahrenheit",
    "to_unit": "celsius"
})
print(response.json(), "\n")
