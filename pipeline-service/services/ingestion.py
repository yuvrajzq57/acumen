import httpx
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from models.customer import Customer

async def fetch_all_flask_data():
    """Fetch all data from Flask API handling pagination"""
    flask_url = "http://mock-server:5000"
    all_customers = []
    page = 1
    limit = 10
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(
                    f"{flask_url}/api/customers",
                    params={"page": page, "limit": limit}
                )
                response.raise_for_status()
                
                data = response.json()
                customers = data.get("data", [])
                
                if not customers:
                    break
                    
                all_customers.extend(customers)
                
                # Check if we have more pages
                total = data.get("total", 0)
                if len(all_customers) >= total:
                    break
                    
                page += 1
                
            except httpx.RequestError as e:
                raise Exception(f"Error fetching from Flask: {str(e)}")
    
    return all_customers

async def ingest_customers(db: Session):
    """Fetch all data from Flask and upsert into PostgreSQL"""
    try:
        # Fetch all data from Flask
        flask_data = await fetch_all_flask_data()
        
        records_processed = 0
        
        for customer_data in flask_data:
            # Convert string dates to proper date objects
            dob = None
            if customer_data.get("date_of_birth"):
                dob = datetime.strptime(customer_data["date_of_birth"], "%Y-%m-%d").date()
            
            created_at = None
            if customer_data.get("created_at"):
                created_at = datetime.fromisoformat(customer_data["created_at"].replace('Z', '+00:00'))
            
            # Prepare data for upsert
            customer_dict = {
                "customer_id": customer_data["customer_id"],
                "first_name": customer_data["first_name"],
                "last_name": customer_data["last_name"],
                "email": customer_data["email"],
                "phone": customer_data.get("phone"),
                "address": customer_data.get("address"),
                "date_of_birth": dob,
                "account_balance": Decimal(str(customer_data.get("account_balance", 0))),
                "created_at": created_at
            }
            
            # Upsert using PostgreSQL ON CONFLICT
            stmt = insert(Customer).values(**customer_dict)
            stmt = stmt.on_conflict_do_update(
                index_elements=['customer_id'],
                set_=customer_dict
            )
            
            db.execute(stmt)
            records_processed += 1
        
        db.commit()
        
        return {
            "status": "success",
            "records_processed": records_processed
        }
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Ingestion failed: {str(e)}")
