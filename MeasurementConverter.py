# ----- README -----
"""
Required installations:
    pip install fastapi uvicorn

Run the server:
    uvicorn MeasurementConverter:app --reload
"""
# NOTE: I currently have not implemented the density-based conversions as I am unsure how you wish to approach that.

from fastapi import FastAPI, Request
from typing import Dict, List, Any, Union

app = FastAPI()

# Conversion factors relative to the base unit
volume_factors = {
    "tsp": 0.0049289249029, 
    "tbsp": 0.0147867747087,
    "floz": 0.0295735494174,
    "cup": 0.236588395339,
    "pt": 0.568262537292,
    "qt": 0.946351342399,
    "gal": 3.78541253426,
    "ml": 0.001,
    "l": 1.0 # Liter is base
}

weight_factors = {
    "mg": 0.000001,
    "g": 0.001,
    "kg": 1.0, # Kilogram is base
    "oz": 0.0283494925441,
    "lb": 0.453592909436
}

# ----- Routes -----
@app.post("/convert_measurements")
async def convert_measurements(request: Request) -> Dict[str, Any]:
    """
    Convert a measurement value from one unit to another. 

    Body:
        {
            "value": float,
            "from_unit": str,
            "to_unit": str,
        }
    Returns:
        A status and the original and converted values.
    """
    data = await request.json()
    value = data["value"]
    from_unit = data["from_unit"]
    to_unit = data["to_unit"]

    # Determine if the conversion is volume or weight
    if from_unit in volume_factors and to_unit in volume_factors:
        factors = volume_factors
    elif from_unit in weight_factors and to_unit in weight_factors:
        factors = weight_factors
    else:
        return {
            "success": False,
            "error": "Invalid measurement conversion"
        }
    
    # Convert original value to base unit, then to desired unit
    value_base = value * factors[from_unit]
    converted = round(value_base / factors[to_unit], 2)

    return {
        "success": True, 
        "original": {"value": value, "unit": from_unit},
        "converted": {"value": converted, "unit": to_unit},
    }

@app.post("/scale_quantities")
async def scale_quantities(request: Request) -> Dict[str, Any]:
    """
    Scale quantities of a list of ingredients by a given factor.

    Body:
        {
            "scale_factor": float,
            "ingredients": [
                {"name": str, "value": float, "unit": str},
                ...
            ]
        }
    Returns:
        A status and the original and scaled ingredient quantities.
    """
    data = await request.json()
    scale_factor = data["scale_factor"]
    ingredients = data["ingredients"]
    scaled_ingredients = []

    for ingredient in ingredients:
        name = ingredient["name"]
        value = ingredient["value"]
        unit = ingredient["unit"]

        # Determine measurement type
        if unit in volume_factors:
            factors = volume_factors
            priority = ["cup", "tbsp", "tsp"] # Conversion priority for readability in home cooking (Change as you wish, Derik)
        elif unit in weight_factors:
            factors = weight_factors
            priority = ["lb", "oz", "g"]
        else:
            return {
                "success": False,
                "error": "Invalid measurement unit"
            }

        # Convert original value to base unit, then scale
        scaled_value = value * factors[unit] * scale_factor

        # Select most practical unit for scaled value
        for unit in priority:
            converted = scaled_value / factors[unit]
            if converted >= 1:
                final_unit = unit
                final_value = round(converted, 2)
                break
        else:
            # If value is very small, use smallest unit in priority
            final_unit = priority[-1]
            final_value = round(scaled_value / factors[final_unit], 2)

        if final_value.is_integer():
            final_value = int(final_value)

        scaled_ingredients.append({
            "name": name,
            "original": {"value": value, "unit": unit},
            "scaled": {"value": final_value, "unit": final_unit}
        })

    return {
        "success": True,
        "scale_factor": scale_factor,
        "original": ingredients,
        "scaled": scaled_ingredients
    }

@app.post("/convert_temperature")
async def convert_temperature(request: Request) -> Dict[str, Any]:
    """
    Convert temperature between Fahrenheit and Celsius.

    Body:
        {
            "value": float,
            "from_unit": str,
            "to_unit": str
        }
    Returns:
        A status and the original and scaled termperature values.
    
    """
    data = await request.json()
    value = data["value"]
    from_unit = data["from_unit"]
    to_unit = data["to_unit"]

    # Check for temperatures below absolute zero
    if from_unit == "fahrenheit" and value < -459.67 or from_unit == "celsius" and value < -273.15:
        return {
            "success": False,
            "error": "Temperature cannot be below absolute zero"
        }

    # Conversion logic
    if from_unit == "fahrenheit":
        converted = round((value - 32) * 5 / 9, 0)
    elif from_unit == "celsius":
        converted = round((value * 9 / 5) + 32, 0)
    else:
        return {
            "success": False,
            "error": "Invalid temperature unit"
        }
    
    return {
        "success": True,
        "original": {"value": value, "unit": from_unit},
        "converted": {"value": converted, "unit": to_unit}
    }
  
