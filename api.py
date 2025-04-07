import json
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
async def transform_property_data(data: Dict[str, Any] = Body(...)):
    """
    Transform property data by extracting basic info and creating sequentially numbered phone numbers.
    
    Args:
        data: Raw data from make.com HTTP module
        
    Returns:
        List of transformed property data with sequential phone numbers
    """
    try:
        logger.info(f"Received request with data: {data}")
        
        # Handle raw string data from make.com
        if isinstance(data, str) and data.startswith('IMTBuffer'):
            logger.info("Processing IMTBuffer data")
            try:
                buffer_data = data.split(': ')[1]
                decoded_data = bytes.fromhex(buffer_data).decode('utf-8')
                data = json.loads(decoded_data)
                logger.info(f"Successfully decoded buffer data: {data}")
            except (ValueError, json.JSONDecodeError, IndexError) as e:
                logger.error(f"Error decoding buffer data: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid data format. Expected valid JSON data")

        # Basic structure validation
        if not isinstance(data, list) or not data:
            logger.error("Invalid data structure: Expected non-empty list")
            raise HTTPException(status_code=400, detail="Expected data to be a non-empty list")

        # Extract properties from the nested structure
        results = data[0].get('results')
        if not results or 'properties' not in results:
            logger.error("Invalid data structure: 'results' or 'properties' key not found")
            raise HTTPException(status_code=400, detail="'results' or 'properties' key not found in data")

        properties_list = results['properties']
        extracted_properties = []
        logger.info(f"Processing {len(properties_list)} properties")

        for property_data in properties_list:
            logger.debug(f"Processing property: {property_data.get('property_id')}")
            # --- Basic Property Info ---
            prop_info = {
                "property_id": property_data.get('property_id'),
                "address": property_data.get('property_address_full'),
                "owner_name": property_data.get('owner_name'),
                "first_contact_name": None,
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
            first_contact_found = False

            phone_numbers_list = property_data.get('phone_numbers', [])
            if isinstance(phone_numbers_list, list):
                logger.debug(f"Processing {len(phone_numbers_list)} phone numbers for property {property_data.get('property_id')}")
                for phone_entry in phone_numbers_list:
                    contact_data = phone_entry.get('contact')
                    if contact_data and isinstance(contact_data, dict):
                        if not first_contact_found:
                            full_name = contact_data.get('full_name')
                            if full_name:
                                prop_info["first_contact_name"] = full_name
                                first_contact_found = True
                                logger.debug(f"Found first contact name: {full_name}")

                        for phone in [contact_data.get('phone_1'), contact_data.get('phone_2'), contact_data.get('phone_3')]:
                            if phone:
                                unique_phones_for_property.add(phone)

            sorted_unique_phones = sorted(list(unique_phones_for_property))
            logger.debug(f"Found {len(sorted_unique_phones)} unique phone numbers for property {property_data.get('property_id')}")
            
            for i, phone in enumerate(sorted_unique_phones):
                prop_info[f'phone_{i}'] = phone

            extracted_properties.append(prop_info)

        logger.info(f"Successfully processed {len(extracted_properties)} properties")
        return extracted_properties

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 