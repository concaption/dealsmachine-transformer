# Property Data Transformer API

A FastAPI-based service that transforms and consolidates property data from Deal Machine into a standardized format, specifically designed to prevent duplicate opportunities in GoHighLevel (GHL) automations.

## Problem Context

This API was created to solve a specific issue in the Deal Machine to GHL automation workflow:

1. **Duplicate Opportunities Issue**: The Make.com automation was creating duplicate opportunities in GHL because:
   - Deal Machine provides "bundled" data with multiple contacts/owners per property
   - Different phone numbers and owner names for the same property were creating separate contacts
   - The standard Make.com module for GHL couldn't effectively search for existing opportunities

2. **Data Consolidation Solution**: This API transforms the Deal Machine data to:
   - Create a single, consolidated record per property address
   - Store all associated names and phone numbers in a structured format
   - Enable the automation to create one contact and one opportunity per property

## Features

- Transform Deal Machine property data into a standardized format
- Consolidate multiple contacts/owners into a single record
- Extract and organize phone numbers sequentially
- Identify and store the first contact name
- Process property flags and other metadata
- CORS enabled for cross-origin requests
- Docker support for easy deployment

## Setup and Installation

### Local Development

1. Create a virtual environment and install dependencies:
```bash
make setup
```

Or if you already have a virtual environment:
```bash
make install
```

2. Run the API server:
```bash
make run
```

The API will be available at `http://localhost:8000`

### Docker Deployment

1. Start the application with Docker Compose:
```bash
make run-docker
```

2. Stop the Docker containers:
```bash
make stop-docker
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoint

### POST /transform

Transforms Deal Machine property data into a consolidated format suitable for GHL automation.

#### Request Body

The request body should be a JSON array containing Deal Machine property data:

```json
[
  {
    "results": {
      "properties": [
        {
          "property_id": "123",
          "property_address_full": "123 Main St",
          "owner_name": "John Doe",
          "total_bedrooms": 3,
          "total_baths": 2.5,
          "building_square_feet": 2000,
          "EstimatedValue": 500000,
          "equity_percent": 75.5,
          "sale_date": "2023-01-01",
          "sale_price": 450000,
          "property_flags": [{"label": "Flag1"}, {"label": "Flag2"}],
          "phone_numbers": [
            {
              "contact": {
                "full_name": "John Smith",
                "phone_1": "123-456-7890",
                "phone_2": "987-654-3210",
                "phone_3": "555-123-4567"
              }
            }
          ]
        }
      ]
    }
  }
]
```

#### Response

The API returns a list of consolidated property data:

```json
[
  {
    "property_id": "123",
    "address": "123 Main St",
    "owner_name": "John Doe",
    "first_contact_name": "John Smith",
    "bedrooms": 3,
    "baths": 2.5,
    "sqft": 2000,
    "estimated_value": 500000,
    "equity_percent": 75.5,
    "last_sale_date": "2023-01-01",
    "last_sale_price": 450000,
    "flags": ["Flag1", "Flag2"],
    "phone_0": "123-456-7890",
    "phone_1": "555-123-4567",
    "phone_2": "987-654-3210"
  }
]
```

## Integration with Make.com/GHL

This API is designed to be integrated into your Make.com automation workflow:

1. Receive Deal Machine data
2. Send it to this API for transformation
3. Use the transformed data to:
   - Create a single contact in GHL
   - Store all phone numbers and names as custom fields
   - Create one opportunity per property

This approach prevents duplicate opportunities by ensuring each property address has exactly one contact and one opportunity in GHL.

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400 Bad Request: Invalid input data structure
- 500 Internal Server Error: Unexpected errors during processing

## Development

### Running Tests

```bash
make test
```

## Available Make Commands

- `make setup` - Create virtual environment and install dependencies
- `make install` - Install dependencies in existing virtual environment
- `make run` - Run the API server locally
- `make test` - Run the test suite
- `make run-docker` - Start the application with Docker Compose
- `make stop-docker` - Stop Docker containers

## License

MIT License
