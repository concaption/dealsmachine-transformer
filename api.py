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
                raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")

        # Basic structure validation
        if not isinstance(data, list):
            logger.error(f"Data is not a list. Type: {type(data)}")
            raise HTTPException(status_code=400, detail="Expected data to be a list")
            
        if not data:
            logger.error("Data list is empty")
            raise HTTPException(status_code=400, detail="Expected data to be a non-empty list")

        try:
            # Extract properties from the nested structure
            first_item = data[0]
            if not isinstance(first_item, dict):
                logger.error(f"First item is not a dictionary. Type: {type(first_item)}")
                raise HTTPException(status_code=400, detail="First item in data must be a dictionary")

            results = first_item.get('results')
            if not results:
                logger.error("'results' key not found in first item")
                raise HTTPException(status_code=400, detail="'results' key not found in data")

            if not isinstance(results, dict):
                logger.error(f"'results' is not a dictionary. Type: {type(results)}")
                raise HTTPException(status_code=400, detail="'results' must be a dictionary")

            properties_list = results.get('properties')
            if not properties_list:
                logger.error("'properties' key not found in results")
                raise HTTPException(status_code=400, detail="'properties' key not found in results")

            if not isinstance(properties_list, list):
                logger.error(f"'properties' is not a list. Type: {type(properties_list)}")
                raise HTTPException(status_code=400, detail="'properties' must be a list")

            extracted_properties = []
            logger.info(f"Processing {len(properties_list)} properties")

            for property_data in properties_list:
                try:
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
                        "flags": [flag.get('label') for flag in property_data.get('property_flags', []) if flag and isinstance(flag, dict) and flag.get('label')],
                    }

                    # --- Process Phone Numbers and Find First Contact Name ---
                    unique_phones_for_property = set()
                    first_contact_found = False

                    phone_numbers_list = property_data.get('phone_numbers', [])
                    if isinstance(phone_numbers_list, list):
                        logger.debug(f"Processing {len(phone_numbers_list)} phone numbers for property {property_data.get('property_id')}")
                        for phone_entry in phone_numbers_list:
                            if not isinstance(phone_entry, dict):
                                logger.warning(f"Skipping invalid phone entry: {phone_entry}")
                                continue
                                
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
                except Exception as prop_error:
                    logger.error(f"Error processing property {property_data.get('property_id')}: {str(prop_error)}", exc_info=True)
                    continue  # Skip this property and continue with others

            logger.info(f"Successfully processed {len(extracted_properties)} properties")
            return extracted_properties

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing data structure: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Error processing data structure: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 