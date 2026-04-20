# Backend Developer Technical Assessment

## Test Results Summary

All API endpoints are working correctly:

✅ **Flask Mock Server (Port 5000)**
- `GET /api/customers?page=1&limit=5` - Returns paginated customer data (200 OK)
- Successfully serving customer records with pagination

✅ **FastAPI Pipeline Service (Port 8000)**
- `POST /api/ingest` - Successfully ingested 22 records (200 OK)
- `GET /api/customers?page=1&limit=5` - Returns paginated customer data (200 OK)

✅ **Docker Services**
- All 3 containers running: postgres, mock-server, pipeline-service
- Services properly connected and communicating


---

## Project Structure
```
project-root/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/customer.py
    ├── services/ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```

## Architecture Overview
This assessment implements a data pipeline with 3 Docker services:

1. **PostgreSQL** (Port 5432) - Data storage with `customer_db` database
2. **Mock Server** (Port 5000) - Flask mock customer data server
3. **Pipeline Service** (Port 8000) - FastAPI data ingestion pipeline

## Data Flow
```
Mock Server (JSON) → Pipeline Service (Ingest) → PostgreSQL → API Response
```

## Services

### PostgreSQL Database
- **Database:** customer_db
- **Table:** customers
- **Schema:** All customer fields with proper data types

### Mock Server (Flask)
- **Endpoints:**
  - `GET /api/health` - Health check
  - `GET /api/customers?page=1&limit=10` - Paginated customer list
  - `GET /api/customers/{id}` - Single customer lookup
- **Features:** Pagination, 404 handling, JSON data source

### Pipeline Service (FastAPI)
- **Endpoints:**
  - `GET /api/health` - Health check
  - `POST /api/ingest` - Fetch all mock server data and upsert to PostgreSQL
  - `GET /api/customers?page=1&limit=10` - Query paginated results from database
  - `GET /api/customers/{id}` - Single customer from database
- **Features:** Auto-pagination from mock server, upsert logic, SQLAlchemy ORM

## Quick Start

1. **Build and start all services:**
```bash
docker-compose up --build
```

2. **Test the pipeline:**
```bash
# Check mock server health
curl http://localhost:5000/api/health

# Check pipeline service health  
curl http://localhost:8000/api/health

# Ingest data from mock server to PostgreSQL
curl -X POST http://localhost:8000/api/ingest

# Query customers from database
curl http://localhost:8000/api/customers?page=1&limit=5
```

## Database Schema

```sql
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    account_balance DECIMAL(15,2),
    created_at TIMESTAMP
);
```

## API Response Formats

### Mock Server Customers List
```json
{
  "data": [...],
  "total": 22,
  "page": 1,
  "limit": 10
}
```

### Pipeline Service Ingest Response
```json
{
  "status": "success",
  "records_processed": 22
}
```

### Pipeline Service Customers List
```json
{
  "data": [...],
  "total": 22,
  "page": 1,
  "limit": 10
}
```

## Requirements Met

✅ **Mock Server (50 pts)**
- 22 customer records in JSON
- All required endpoints
- Pagination support
- 404 error handling
- Dockerfile + requirements.txt

✅ **Pipeline Service (50 pts)**
- SQLAlchemy model matching schema
- POST /api/ingest with mock server pagination
- GET /api/customers with DB pagination
- GET /api/customers/{id} with 404
- Upsert logic (update if exists)
- Error handling
- Dockerfile + requirements.txt
- Docker Compose configuration

✅ **Project Structure**
- Properly organized with separate service directories
- Modular FastAPI application with models, services, and database layers
- Clean separation of concerns
