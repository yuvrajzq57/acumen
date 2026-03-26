from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.customer import Customer
from services.ingestion import ingest_customers
from database import get_db, create_tables

# Pydantic Models
class CustomerResponse(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    account_balance: Optional[float] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class PaginatedCustomersResponse(BaseModel):
    data: List[CustomerResponse]
    total: int
    page: int
    limit: int

class IngestResponse(BaseModel):
    status: str
    records_processed: int

# FastAPI App
app = FastAPI(title="FastAPI Data Ingestion Pipeline", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Create database tables"""
    create_tables()

@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_data(db: Session = Depends(get_db)):
    """Fetch all data from Flask and upsert into PostgreSQL"""
    try:
        result = await ingest_customers(db)
        return IngestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers", response_model=PaginatedCustomersResponse)
async def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of customers from database"""
    try:
        # Get total count
        total = db.query(Customer).count()
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get paginated data
        customers = db.query(Customer).offset(offset).limit(limit).all()
        
        # Convert to response format
        customer_responses = []
        for customer in customers:
            customer_dict = customer.to_dict()
            # Convert date objects to strings for JSON response
            if customer_dict.get('date_of_birth'):
                customer_dict['date_of_birth'] = customer_dict['date_of_birth'].isoformat()
            if customer_dict.get('created_at'):
                customer_dict['created_at'] = customer_dict['created_at'].isoformat()
            customer_responses.append(CustomerResponse(**customer_dict))
        
        return PaginatedCustomersResponse(
            data=customer_responses,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get single customer by ID from database"""
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        customer_dict = customer.to_dict()
        # Convert date objects to strings for JSON response
        if customer_dict.get('date_of_birth'):
            customer_dict['date_of_birth'] = customer_dict['date_of_birth'].isoformat()
        if customer_dict.get('created_at'):
            customer_dict['created_at'] = customer_dict['created_at'].isoformat()
        
        return CustomerResponse(**customer_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "FastAPI Data Ingestion Pipeline"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
