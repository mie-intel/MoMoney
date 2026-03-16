Proposal: Invoice Entity Implementation for MoMoney
This proposal outlines the architectural addition of the Invoice entity to the MoMoney backend. Based on the existing ARCHITECTURE.md, the goal is to support dynamic receipt data while maintaining a clean relational structure.

1. Recommended Approach: Normalized Hybrid Table
   We will use a dedicated Invoice table with a JSONB data column. This combines the structural benefits of SQL relationships with the flexibility needed for user-defined group columns.

Why this wins:
Query Performance: Fetching a group and its invoices is a single, indexed relationship lookup.

Data Integrity: Deleting a Group can automatically cascade-delete its Invoices.

Flexibility: The data field allows each invoice to have different keys (Date, Merchant, Amount) based on the parent Group.columns definition.

2. Proposed Data Model
   The new Invoice entity will be added to a new domain folder domain/invoices/.

Code snippet
erDiagram
GROUP ||--o{ INVOICE : contains
INVOICE {
int id PK
int group_id FK
jsonb data
string image_url
datetime created_at
}
Updated Schema (SQLModel)
Python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, List
from datetime import datetime

class InvoiceBase(SQLModel): # Flexible field to match Group.columns
data: Dict = Field(default={}, sa_column=Column(JSONB))
image_url: Optional[str] = None

class Invoice(InvoiceBase, table=True):
id: Optional[int] = Field(default=None, primary_key=True)
group_id: int = Field(foreign_key="group.id", index=True)
created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship back to Group
    group: "Group" = Relationship(back_populates="invoices")

class Group(SQLModel, table=True): # Existing fields from ARCHITECTURE.md
id: Optional[int] = Field(default=None, primary_key=True)
name: str
owner_id: int = Field(foreign_key="user.id")
columns: List[str] = Field(sa_column=Column(JSONB))

    # New relationship
    invoices: List[Invoice] = Relationship(back_populates="group", cascade_delete=True)

3. API Design Changes
   GET /groups/{id}
   To meet the requirement of getting group info and all related invoices in one call, we will use a joined query.

Response Structure:

JSON
{
"id": 1,
"name": "Business Trip 2025",
"columns": ["date", "vendor", "total"],
"invoices": [
{
"id": 101,
"data": {
"date": "2025-10-01",
"vendor": "Starbucks",
"total": 5.50
}
}
]
}
New Invoice Endpoints
POST /groups/{id}/invoices: Create a new invoice entry for a specific group.

PATCH /invoices/{id}: Update specific data points within an invoice.

DELETE /invoices/{id}: Remove a specific receipt entry.

4. Implementation Steps
   Create Domain: Add domain/invoices/ with entity.py, schemas.py, and routes.py.

Update Group Entity: Add the Relationship to domain/groups/entity.py.

Migration: Update app.py to ensure the new Invoice table is created on startup.

Service Integration: Link image_services.py to allow uploading an image and saving the resulting URL in the Invoice.image_url field.

Would you like me to write the specific FastAPI route code for the POST /groups/{id}/invoices endpoint next?
