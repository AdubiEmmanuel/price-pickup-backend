# Competitor Price API Reference

Audience: Frontend developers integrating with the Lagos Region Price Pickup backend.

Base Path
- Local: http://localhost:8000/
- API base: /api/

Interactive Docs
- Swagger UI: /api/docs/
- ReDoc: /api/docs/redoc/
- OpenAPI JSON: /api/docs/swagger.json
- OpenAPI YAML: /api/docs/swagger.yaml

Authentication and CORS
- Authentication: Not required (AllowAny). You can call endpoints without a token.
- CORS: Allowed from http://localhost:3000, http://127.0.0.1:3000, and https://price-pickup.vercel.app.
- Note: Swagger UI shows a Bearer auth option but it is not required in current configuration.

Pagination, Filtering, Search, Ordering
- Pagination: Page-number style.
  - Query param: page (integer, 1-based)
  - Page size: 100 (fixed)
  - Response shape: { count, next, previous, results: [...] }
- Filters (on list endpoints): sku_category, sku_size, brand, is_unilever, location.
  - Example: /api/competitor-prices/?sku_category=NUTRITION&is_unilever=true
- Search: ?search=... across sku_name and brand.
  - Example: /api/competitor-prices/?search=vaseline
- Ordering: ?ordering=..., supports created_at, sku_name, kd_case, kd_unit. Prefix with - for descending.
  - Example: /api/competitor-prices/?ordering=-created_at

Data Model
- Resource: CompetitorPrice
- Fields
  - id: integer
  - sku_code: string | null
  - sku_category: enum | null (see choices below)
  - sku_size: enum | null (see choices below)
  - sku_name: string | null
  - brand: enum | null (see choices below)
  - kd_case: number | null (decimal)
  - kd_unit: number | null (decimal)
  - kd_price_gram: number | null (decimal)
  - wholesale_price: number | null (decimal)
  - open_market_price: number | null (decimal)
  - ng_price: number | null (decimal)
  - small_supermarket_price: number | null (decimal)
  - is_unilever: boolean (default false)
  - location: string | null
  - source: enum ('CSV' | 'FORM')
  - created_at: datetime (read-only)
  - updated_at: datetime (read-only)

- Enumerations
  - sku_category: [NUTRITION, ORAL CARE, DEODORANT, SKIN CARE, SALVORY]
  - sku_size: [BULK PACK, MID PACK, REGULAR PACK, SMALL PACK, POWDERS]
  - brand: [PEARS, VASELINE, CLOSE UP, PEPSODENT, KNORR, ROYCO, REXONA]
  - market_type (for create_price_entry): [OPEN_MARKET, NG, SMALL_SUPERMARKET, WHOLESALE]


Endpoints

1) List competitor prices
- GET /api/competitor-prices/
- Query params: page, search, ordering, sku_category, sku_size, brand, is_unilever, location
- Response: paginated list
Example response
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 12,
      "sku_category": "NUTRITION",
      "sku_size": "BULK PACK",
      "sku_name": "Example Product",
      "brand": "VASELINE",
      "kd_case": 1000.0,
      "kd_unit": 100.0,
      "kd_price_gram": 0.5,
      "wholesale_price": 900.0,
      "open_market_price": 950.0,
      "ng_price": 980.0,
      "small_supermarket_price": 970.0,
      "is_unilever": true,
      "location": "Lagos",
      "source": "FORM",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    }
  ]
}

2) Retrieve a single competitor price
- GET /api/competitor-prices/{id}/
- Response: CompetitorPrice object

3) Create a competitor price (standard CRUD)
- POST /api/competitor-prices/
- Body: JSON with any subset of fields; on creation, sku_category, sku_size, and sku_name are required.
Example request
{
  "sku_category": "SKIN CARE",
  "sku_size": "REGULAR PACK",
  "sku_name": "Hydrating Lotion",
  "brand": "VASELINE",
  "wholesale_price": 1200,
  "location": "Abuja",
  "is_unilever": true,
  "source": "FORM"
}
- Response: 201 with created object or 400 with validation errors

4) Update a competitor price
- PUT /api/competitor-prices/{id}/
- PATCH /api/competitor-prices/{id}/
- Note: If the existing record has source == 'CSV', updating it will create a new record with source set to 'FORM' instead of modifying the original.

5) Delete a competitor price
- DELETE /api/competitor-prices/{id}/
- Response: 204 No Content

6) Get available choices (categories, sizes, market types)
- GET /api/competitor-prices/get_category_choices/
- Response
{
  "sku_categories": {
    "NUTRITION": "NUTRITION",
    "ORAL CARE": "ORAL CARE",
    "DEODORANT": "DEODORANT",
    "SKIN CARE": "SKIN CARE",
    "SALVORY": "SALVORY"
  },
  "sku_sizes": {
    "BULK PACK": "BULK PACK",
    "MID PACK": "MID PACK",
    "REGULAR PACK": "REGULAR PACK",
    "SMALL PACK": "SMALL PACK",
    "POWDERS": "POWDERS"
  },
  "market_types": {
    "OPEN_MARKET": "Open Market",
    "NG": "NG Market",
    "SMALL_SUPERMARKET": "Small Supermarket",
    "WHOLESALE": "Wholesale"
  }
}

7) Simplified price entry (recommended for frontend)
- POST /api/competitor-prices/create_price_entry/
- Purpose: Create a new record by specifying market_type and a single price; backend maps price to the correct field.
- Required fields: sku_category, sku_size, sku_name, market_type, price
- Optional fields: brand, is_unilever, location
- Mapping
  - OPEN_MARKET -> open_market_price
  - NG -> ng_price
  - SMALL_SUPERMARKET -> small_supermarket_price
  - WHOLESALE -> wholesale_price
- Behavior
  - Ignores incoming price and market_type fields after mapping.
  - Sets source to 'FORM' automatically.
- Example request
{
  "sku_category": "NUTRITION",
  "sku_size": "BULK PACK",
  "sku_name": "Example Product",
  "brand": "KNORR",
  "market_type": "OPEN_MARKET",
  "price": 150.0,
  "is_unilever": false,
  "location": "Lagos"
}
- Response: 201 with created object or 400 with validation details (e.g., missing fields or invalid market_type)

8) Upload price data (CSV or Excel)
- POST /api/competitor-prices/upload/
- Content-Type: multipart/form-data
- Form field: file (required) — must be a .csv or .xlsx file
- CSV expectations
  - Required header presence: SKU Category
  - Header mapping used by backend:
    - SKU Category -> sku_category
    - SKU Size -> sku_size
    - SKU Name/Brand -> splits into sku_name (all but last word) and brand (last word)
    - KD Case -> kd_case
    - KD Unit -> kd_unit
    - KD Price/Gram -> kd_price_gram
    - Wholesales price -> wholesale_price
    - Open Market Price -> open_market_price
    - NG Price -> ng_price
    - Small Supermarket Price -> small_supermarket_price
  - Numeric values: commas are stripped, then parsed as float.
  - Source set to 'CSV'.
- Excel (.xlsx) expectations
  - Required header presence: SKU Category
  - Header mapping used by backend:
    - SKU Category, SKU Size, SKU Name, Brand, KD Case, KD Unit, KD Price/Gram, Wholesales price, Open Market Price, NG Price, Small Supermarket Price
  - Numeric values: converted to string, commas stripped, parsed as float if possible.
  - Source set to 'EXCEL'.
- Response
{
  "message": "Successfully created <N> records",
  "errors": [
    { "row": 3, "errors": { "sku_category": ["Invalid category..."] } }
  ]
}
- Notes
  - The CSV path splits SKU Name/Brand by spaces and assumes the last token is the brand; adjust your exports accordingly.
  - For Excel uploads, the backend marks source as 'EXCEL' while the database field only accepts 'CSV' or 'FORM'. This may produce validation errors depending on data; if you encounter issues, prefer CSV uploads or create via create_price_entry.

9) Export data (CSV)
- GET /api/competitor-prices/export/?format=csv&<filters>
- Filters: same as list (sku_category, sku_size, brand, is_unilever, location) plus search/ordering are ignored for export.
- Response: text/csv attachment named competitor_prices.csv with the following columns:
  - SKU Category, SKU Size, SKU Name/Brand, KD Case, KD Unit, KD Price/Gram,
    Wholesales price, Open Market Price, NG Price, Small Supermarket Price,
    Is Unilever, Location, Created At


Validation Rules
- On creation (standard POST and create_price_entry): sku_category, sku_size, sku_name are required.
- sku_category must be one of the enumerated choices.
- sku_size must be one of the enumerated choices.
- create_price_entry additionally requires market_type and price.
- Updating a record originally created from CSV (source == 'CSV') will create a new record instead of modifying the old one (the new record will have source == 'FORM').

Examples

List with filters and search
GET /api/competitor-prices/?sku_category=NUTRITION&is_unilever=true&search=pepsodent&ordering=-created_at&page=1

Create with simplified endpoint
POST /api/competitor-prices/create_price_entry/
Content-Type: application/json
{
  "sku_category": "ORAL CARE",
  "sku_size": "SMALL PACK",
  "sku_name": "Pepsodent Mint",
  "brand": "PEPSODENT",
  "market_type": "SMALL_SUPERMARKET",
  "price": 250.0,
  "is_unilever": true,
  "location": "Ikeja"
}

CSV upload (curl)
curl -X POST "http://localhost:8000/api/competitor-prices/upload/" \
  -H "Accept: application/json" \
  -F "file=@/path/to/data.csv"

Export CSV (filtered)
GET /api/competitor-prices/export/?format=csv&sku_category=SKIN%20CARE&brand=VASELINE

Error Responses
- 400 Bad Request: Validation errors on create/update or upload. Example
{
  "sku_category": ["Invalid category. Must be one of: NUTRITION, ORAL CARE, DEODORANT, SKIN CARE, SALVORY"]
}
- 404 Not Found: Resource id not found

Operational Notes
- Default page size is 100 and cannot be changed via query string.
- Numeric fields are decimals in the backend; send numbers (not strings) in JSON for prices and KD fields.
- The backend currently does not enforce authentication. If that changes, the Swagger UI will reflect it.

Quick Start Checklist
- Browse docs at /api/docs/ (Swagger) or /api/docs/redoc/
- For new entries, prefer POST /api/competitor-prices/create_price_entry/
- For bulk imports, prefer CSV format with the expected headers.
- Use filters, search, and ordering on list endpoints to build UIs efficiently.

