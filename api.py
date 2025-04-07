import json
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Property Data Transformer API",
    description="API for transforming property data with sequential phone numbers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transform")
async def transform_property_data(data: Any):
    """
    Transform property data by extracting basic info and creating sequentially numbered phone numbers.
    
    Args:
        data: Raw data from make.com HTTP module
        
    Returns:
        List of transformed property data with sequential phone numbers
    """
    try:
        # Handle raw string data from make.com
        if isinstance(data, str) and data.startswith('IMTBuffer'):
            # Extract the binary data from the buffer string
            try:
                buffer_data = data.split(': ')[1]
                # Convert hex string to bytes and decode
                decoded_data = bytes.fromhex(buffer_data).decode('utf-8')
                data = json.loads(decoded_data)
            except (ValueError, json.JSONDecodeError, IndexError):
                raise HTTPException(status_code=400, detail="Invalid data format. Expected valid JSON data")

        # Basic structure validation
        if not isinstance(data, list) or not data:
            raise HTTPException(status_code=400, detail="Expected data to be a non-empty list")
 
        # if not data or 'properties' not in data:
        #     raise HTTPException(status_code=400, detail="'results' or 'properties' key not found in data")

        properties_list = data
        extracted_properties = []

        for property_data in properties_list:
            # --- Basic Property Info ---
            prop_info = {
                "property_id": property_data.get('property_id'),
                "address": property_data.get('property_address_full'),
                "owner_name": property_data.get('owner_name'),  # This is the assessor owner name
                "first_contact_name": None,  # Initialize field for first contact name
                "bedrooms": property_data.get('total_bedrooms'),
                "baths": property_data.get('total_baths'),
                "sqft": property_data.get('building_square_feet'),
                "estimated_value": property_data.get('EstimatedValue'),
                "equity_percent": property_data.get('equity_percent'),
                "last_sale_date": property_data.get('sale_date'),
                "last_sale_price": property_data.get('sale_price'),
                "flags": [flag.get('label') for flag in property_data.get('property_flags', []) if flag.get('label')],
            }

            # --- Process Phone Numbers and Find First Contact Name ---
            unique_phones_for_property = set()
            first_contact_found = False  # Flag to track if we've captured the first contact name

            phone_numbers_list = property_data.get('phone_numbers', [])
            if isinstance(phone_numbers_list, list):
                for phone_entry in phone_numbers_list:
                    contact_data = phone_entry.get('contact')
                    if contact_data and isinstance(contact_data, dict):
                        # Capture the name of the first contact encountered
                        if not first_contact_found:
                            full_name = contact_data.get('full_name')
                            if full_name:
                                prop_info["first_contact_name"] = full_name
                                first_contact_found = True  # Stop looking for the first contact name

                        # Extract unencrypted phones from the nested contact object
                        phone1 = contact_data.get('phone_1')
                        phone2 = contact_data.get('phone_2')
                        phone3 = contact_data.get('phone_3')

                        if phone1:
                            unique_phones_for_property.add(phone1)
                        if phone2:
                            unique_phones_for_property.add(phone2)
                        if phone3:
                            unique_phones_for_property.add(phone3)

            # Convert the set to a sorted list for consistent ordering
            # and add sequentially numbered keys to the prop_info dictionary
            sorted_unique_phones = sorted(list(unique_phones_for_property))
            for i, phone in enumerate(sorted_unique_phones):
                prop_info[f'phone_{i}'] = phone  # Add phone_0, phone_1, etc.

            extracted_properties.append(prop_info)

        return extracted_properties

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 