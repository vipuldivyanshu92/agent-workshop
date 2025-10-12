"""
Dummy ERP System
Manages customers, vendor/supplier invoices, and payments
"""
from fastapi import APIRouter, HTTPException, status, FastAPI
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date
from enum import Enum

# Create separate FastAPI app for ERP System with its own docs
erp_app = FastAPI(
    title="ERP System API",
    description="Dummy ERP System for managing customers, invoices, and payments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

router = APIRouter()

# In-memory storage
customers_storage = []
invoices_storage = []
payments_storage = []
customer_id_counter = {"value": 1}
invoice_id_counter = {"value": 1}
payment_id_counter = {"value": 1}


class InvoiceStatus(str, Enum):
    OUTSTANDING = "outstanding"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceType(str, Enum):
    VENDOR = "vendor"
    SUPPLIER = "supplier"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# Customer Models
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None


class Customer(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    created_at: datetime


# Invoice Models
class InvoiceCreate(BaseModel):
    customer_id: int
    invoice_type: InvoiceType
    amount: float
    due_date: date
    description: str
    vendor_supplier_name: str


class Invoice(BaseModel):
    id: int
    customer_id: int
    invoice_type: InvoiceType
    amount: float
    amount_paid: float = 0.0
    amount_outstanding: float
    due_date: date
    description: str
    vendor_supplier_name: str
    status: InvoiceStatus
    created_at: datetime


# Payment Models
class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float
    payment_method: str
    notes: Optional[str] = None


class Payment(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_method: str
    notes: Optional[str] = None
    status: PaymentStatus
    created_at: datetime


# Customer Endpoints
@router.get("/customers", response_model=List[Customer])
async def get_customers():
    """
    Get all customers
    """
    return customers_storage


@router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: int):
    """
    Get a specific customer by ID
    """
    for customer in customers_storage:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")


@router.post("/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate):
    """
    Create a new customer
    """
    customer_data = {
        "id": customer_id_counter["value"],
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "company": customer.company,
        "created_at": datetime.now()
    }
    
    customer_id_counter["value"] += 1
    customers_storage.append(customer_data)
    
    return customer_data


@router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: int, customer: CustomerCreate):
    """
    Update a customer
    """
    for i, cust in enumerate(customers_storage):
        if cust["id"] == customer_id:
            customer_data = {
                "id": customer_id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "address": customer.address,
                "company": customer.company,
                "created_at": cust["created_at"]
            }
            customers_storage[i] = customer_data
            return customer_data
    raise HTTPException(status_code=404, detail="Customer not found")


@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int):
    """
    Delete a customer
    """
    global customers_storage
    for i, customer in enumerate(customers_storage):
        if customer["id"] == customer_id:
            customers_storage.pop(i)
            return {"message": "Customer deleted successfully"}
    raise HTTPException(status_code=404, detail="Customer not found")


# Invoice Endpoints
@router.get("/invoices", response_model=List[Invoice])
async def get_invoices(
    status: Optional[InvoiceStatus] = None,
    invoice_type: Optional[InvoiceType] = None,
    customer_id: Optional[int] = None
):
    """
    Get all invoices with optional filters
    """
    result = invoices_storage
    
    if status:
        result = [inv for inv in result if inv["status"] == status]
    if invoice_type:
        result = [inv for inv in result if inv["invoice_type"] == invoice_type]
    if customer_id:
        result = [inv for inv in result if inv["customer_id"] == customer_id]
    
    return result


@router.get("/invoices/outstanding", response_model=List[Invoice])
async def get_outstanding_invoices():
    """
    Get all outstanding invoices (vendor and supplier)
    """
    return [
        inv for inv in invoices_storage 
        if inv["status"] in [InvoiceStatus.OUTSTANDING, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE]
    ]


@router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: int):
    """
    Get a specific invoice by ID
    """
    for invoice in invoices_storage:
        if invoice["id"] == invoice_id:
            return invoice
    raise HTTPException(status_code=404, detail="Invoice not found")


@router.post("/invoices", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice: InvoiceCreate):
    """
    Create a new invoice
    """
    # Check if customer exists
    customer_exists = any(c["id"] == invoice.customer_id for c in customers_storage)
    if not customer_exists:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Determine initial status
    initial_status = InvoiceStatus.OUTSTANDING
    if invoice.due_date < date.today():
        initial_status = InvoiceStatus.OVERDUE
    
    invoice_data = {
        "id": invoice_id_counter["value"],
        "customer_id": invoice.customer_id,
        "invoice_type": invoice.invoice_type,
        "amount": invoice.amount,
        "amount_paid": 0.0,
        "amount_outstanding": invoice.amount,
        "due_date": invoice.due_date,
        "description": invoice.description,
        "vendor_supplier_name": invoice.vendor_supplier_name,
        "status": initial_status,
        "created_at": datetime.now()
    }
    
    invoice_id_counter["value"] += 1
    invoices_storage.append(invoice_data)
    
    return invoice_data


@router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: int):
    """
    Delete an invoice
    """
    global invoices_storage
    for i, invoice in enumerate(invoices_storage):
        if invoice["id"] == invoice_id:
            invoices_storage.pop(i)
            return {"message": "Invoice deleted successfully"}
    raise HTTPException(status_code=404, detail="Invoice not found")


# Payment Endpoints
@router.get("/payments", response_model=List[Payment])
async def get_payments(invoice_id: Optional[int] = None):
    """
    Get all payments with optional invoice filter
    """
    if invoice_id:
        return [p for p in payments_storage if p["invoice_id"] == invoice_id]
    return payments_storage


@router.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: int):
    """
    Get a specific payment by ID
    """
    for payment in payments_storage:
        if payment["id"] == payment_id:
            return payment
    raise HTTPException(status_code=404, detail="Payment not found")


@router.post("/payments", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate):
    """
    Create a new payment and update invoice status
    """
    # Find the invoice
    invoice = None
    invoice_index = None
    for i, inv in enumerate(invoices_storage):
        if inv["id"] == payment.invoice_id:
            invoice = inv
            invoice_index = i
            break
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Check if payment amount is valid
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")
    
    if payment.amount > invoice["amount_outstanding"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Payment amount exceeds outstanding amount of {invoice['amount_outstanding']}"
        )
    
    # Create payment
    payment_data = {
        "id": payment_id_counter["value"],
        "invoice_id": payment.invoice_id,
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "notes": payment.notes,
        "status": PaymentStatus.COMPLETED,
        "created_at": datetime.now()
    }
    
    payment_id_counter["value"] += 1
    payments_storage.append(payment_data)
    
    # Update invoice
    invoice["amount_paid"] += payment.amount
    invoice["amount_outstanding"] -= payment.amount
    
    if invoice["amount_outstanding"] == 0:
        invoice["status"] = InvoiceStatus.PAID
    elif invoice["amount_paid"] > 0:
        invoice["status"] = InvoiceStatus.PARTIALLY_PAID
    
    invoices_storage[invoice_index] = invoice
    
    return payment_data


@router.get("/statistics")
async def get_erp_statistics():
    """
    Get ERP system statistics
    """
    total_customers = len(customers_storage)
    total_invoices = len(invoices_storage)
    total_payments = len(payments_storage)
    
    outstanding_amount = sum(inv["amount_outstanding"] for inv in invoices_storage)
    paid_amount = sum(inv["amount_paid"] for inv in invoices_storage)
    
    outstanding_count = len([
        inv for inv in invoices_storage 
        if inv["status"] in [InvoiceStatus.OUTSTANDING, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE]
    ])
    
    return {
        "total_customers": total_customers,
        "total_invoices": total_invoices,
        "total_payments": total_payments,
        "outstanding_invoices_count": outstanding_count,
        "total_outstanding_amount": outstanding_amount,
        "total_paid_amount": paid_amount
    }


# Include router in the ERP app
erp_app.include_router(router)
