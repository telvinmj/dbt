# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Optional
# import uuid
# from datetime import datetime

# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Models ---
# class Column(BaseModel):
#     name: str
#     type: str
#     description: Optional[str] = None
#     isPrimaryKey: bool = False
#     isForeignKey: bool = False

# class Model(BaseModel):
#     id: str
#     name: str
#     project: str
#     description: Optional[str] = None
#     columns: List[Column] = []
#     sql: Optional[str] = None

# class ModelLineage(BaseModel):
#     source: str
#     target: str

# # --- Sample Data ---
# projects = [
#     {"id": "ecommerce", "name": "ecommerce", "description": "E-commerce dbt project"},
#     {"id": "finance", "name": "finance", "description": "Finance dbt project"},
#     {"id": "marketing", "name": "marketing", "description": "Marketing dbt project"}
# ]

# models = [
#     # Ecommerce models
#     {
#         "id": "e1", 
#         "name": "stg_orders", 
#         "project": "ecommerce", 
#         "description": "Staging orders data",
#         "columns": [
#             {"name": "order_id", "type": "integer", "description": "Unique order identifier", "isPrimaryKey": True, "isForeignKey": False},
#             {"name": "customer_id", "type": "integer", "description": "Customer identifier", "isPrimaryKey": False, "isForeignKey": True},
#             {"name": "order_date", "type": "timestamp", "description": "Date when order was placed", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "status", "type": "string", "description": "Order status", "isPrimaryKey": False, "isForeignKey": False}
#         ],
#         "sql": "SELECT * FROM raw_orders"
#     },
#     {
#         "id": "e2", 
#         "name": "stg_customers", 
#         "project": "ecommerce", 
#         "description": "Staging customers data",
#         "columns": [
#             {"name": "customer_id", "type": "integer", "description": "Unique customer identifier", "isPrimaryKey": True, "isForeignKey": False},
#             {"name": "name", "type": "string", "description": "Customer name", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "email", "type": "string", "description": "Customer email", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "signup_date", "type": "timestamp", "description": "Date when customer signed up", "isPrimaryKey": False, "isForeignKey": False}
#         ],
#         "sql": "SELECT * FROM raw_customers"
#     },
#     {
#         "id": "e3", 
#         "name": "customer_orders", 
#         "project": "ecommerce", 
#         "description": "Combined customer and order data",
#         "columns": [
#             {"name": "order_id", "type": "integer", "description": "Unique order identifier", "isPrimaryKey": True, "isForeignKey": False},
#             {"name": "customer_id", "type": "integer", "description": "Customer identifier", "isPrimaryKey": False, "isForeignKey": True},
#             {"name": "customer_name", "type": "string", "description": "Customer name", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "order_date", "type": "timestamp", "description": "Date when order was placed", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "status", "type": "string", "description": "Order status", "isPrimaryKey": False, "isForeignKey": False}
#         ],
#         "sql": "SELECT o.order_id, o.customer_id, c.name as customer_name, o.order_date, o.status FROM stg_orders o JOIN stg_customers c ON o.customer_id = c.customer_id"
#     },
    
#     # Finance models
#     {
#         "id": "f1", 
#         "name": "stg_transactions", 
#         "project": "finance", 
#         "description": "Staging transactions data",
#         "columns": [
#             {"name": "transaction_id", "type": "integer", "description": "Unique transaction identifier", "isPrimaryKey": True, "isForeignKey": False},
#             {"name": "order_id", "type": "integer", "description": "Order identifier", "isPrimaryKey": False, "isForeignKey": True},
#             {"name": "amount", "type": "decimal", "description": "Transaction amount", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "transaction_date", "type": "timestamp", "description": "Date of transaction", "isPrimaryKey": False, "isForeignKey": False}
#         ],
#         "sql": "SELECT * FROM raw_transactions"
#     },
#     {
#         "id": "f2", 
#         "name": "order_revenue", 
#         "project": "finance", 
#         "description": "Order revenue from transactions",
#         "columns": [
#             {"name": "order_id", "type": "integer", "description": "Order identifier", "isPrimaryKey": True, "isForeignKey": True},
#             {"name": "customer_id", "type": "integer", "description": "Customer identifier", "isPrimaryKey": False, "isForeignKey": True},
#             {"name": "total_amount", "type": "decimal", "description": "Total order amount", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "transaction_count", "type": "integer", "description": "Number of transactions", "isPrimaryKey": False, "isForeignKey": False}
#         ],
#         "sql": "SELECT co.order_id, co.customer_id, SUM(t.amount) as total_amount, COUNT(*) as transaction_count FROM customer_orders co JOIN stg_transactions t ON co.order_id = t.order_id GROUP BY co.order_id, co.customer_id"
#     },
    
#     # Marketing models
#     {
#         "id": "m1", 
#         "name": "stg_campaigns", 
#         "project": "marketing", 
#         "description": "Staging campaign data",
#         "columns": [
#             {"name": "campaign_id", "type": "integer", "description": "Unique campaign identifier", "isPrimaryKey": True, "isForeignKey": False},
#             {"name": "name", "type": "string", "description": "Campaign name", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "start_date", "type": "timestamp", "description": "Campaign start date", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "end_date", "type": "timestamp", "description": "Campaign end date", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "budget", "type": "decimal", "description": "Campaign budget", "isPrimaryKey": False, "isForeignKey": False}
#         ],
#         "sql": "SELECT * FROM raw_campaigns"
#     },
#     {
#         "id": "m2", 
#         "name": "stg_interactions", 
#         "project": "marketing", 
#         "description": "Staging customer interactions",
#         "columns": [
#             {"name": "interaction_id", "type": "integer", "description": "Unique interaction identifier", "isPrimaryKey": True, "isForeignKey": False},
#             {"name": "customer_id", "type": "integer", "description": "Customer identifier", "isPrimaryKey": False, "isForeignKey": True},
#             {"name": "campaign_id", "type": "integer", "description": "Campaign identifier", "isPrimaryKey": False, "isForeignKey": True},
#             {"name": "interaction_date", "type": "timestamp", "description": "Date of interaction", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "channel", "type": "string", "description": "Interaction channel", "isPrimaryKey": False, "isForeignKey": False}
#         ],
#         "sql": "SELECT * FROM raw_interactions"
#     },
#     {
#         "id": "m3", 
#         "name": "campaign_performance", 
#         "project": "marketing", 
#         "description": "Campaign performance metrics",
#         "columns": [
#             {"name": "campaign_id", "type": "integer", "description": "Campaign identifier", "isPrimaryKey": True, "isForeignKey": True},
#             {"name": "interaction_count", "type": "integer", "description": "Number of interactions", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "unique_customers", "type": "integer", "description": "Number of unique customers", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "revenue", "type": "decimal", "description": "Total revenue attributed to campaign", "isPrimaryKey": False, "isForeignKey": False},
#             {"name": "roi", "type": "decimal", "description": "Return on investment", "isPrimaryKey": False, "isForeignKey": False}
#         ],
#         "sql": "SELECT c.campaign_id, COUNT(i.interaction_id) as interaction_count, COUNT(DISTINCT i.customer_id) as unique_customers, SUM(r.total_amount) as revenue, SUM(r.total_amount) / c.budget as roi FROM stg_campaigns c JOIN stg_interactions i ON c.campaign_id = i.campaign_id JOIN order_revenue r ON i.customer_id = r.customer_id GROUP BY c.campaign_id, c.budget"
#     }
# ]

# # Define lineage relationships
# lineage_data = [
#     # customer_orders depends on stg_orders and stg_customers
#     {"source": "e1", "target": "e3"},
#     {"source": "e2", "target": "e3"},
    
#     # order_revenue depends on stg_transactions and customer_orders
#     {"source": "f1", "target": "f2"},
#     {"source": "e3", "target": "f2"},
    
#     # campaign_performance depends on stg_campaigns, stg_interactions, and order_revenue
#     {"source": "m1", "target": "m3"},
#     {"source": "m2", "target": "m3"},
#     {"source": "f2", "target": "m3"}
# ]

# # --- API Routes ---
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to dbt Metadata Explorer API"}

# @app.get("/api/health")
# async def health_check():
#     return {"status": "ok", "timestamp": datetime.now().isoformat()}

# @app.get("/api/models", response_model=List[Model])
# async def get_models(search: Optional[str] = None):
#     if search:
#         filtered_models = [m for m in models if search.lower() in m["name"].lower()]
#     else:
#         filtered_models = models
    
#     return filtered_models

# @app.get("/api/projects")
# async def get_projects():
#     return projects

# @app.get("/api/lineage")
# async def get_lineage():
#     return lineage_data

# @app.get("/api/models/{model_id}")
# async def get_model(model_id: str):
#     for model in models:
#         if model["id"] == model_id:
#             return model
#     return {"error": "Model not found"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("simple_app:app", host="0.0.0.0", port=8000, reload=True) 