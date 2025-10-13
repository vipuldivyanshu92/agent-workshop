"""
Dummy Payment Gateway
Simulates payment processing endpoint
"""
from fastapi import APIRouter, HTTPException, status, FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import random
import string
import os

# Get base URL from environment variable or use default
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Create separate FastAPI app for Payment Gateway with its own docs
payment_app = FastAPI(
    title="Payment Gateway API",
    description="Dummy Payment Gateway for processing payments and refunds",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    servers=[
        {
            "url": f"{BASE_URL}/payment",
            "description": "Payment Gateway Server"
        },
        {
            "url": "http://localhost:8000/payment",
            "description": "Local Development Server"
        }
    ]
)

router = APIRouter()

# In-memory storage
transactions_storage = []
transaction_id_counter = {"value": 1}


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    WALLET = "wallet"
    PAYPAL = "paypal"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    JPY = "JPY"


# Payment Models
class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount (must be positive)")
    currency: Currency
    payment_method: PaymentMethod
    card_number: Optional[str] = Field(None, min_length=13, max_length=19)
    card_holder_name: Optional[str] = None
    cvv: Optional[str] = Field(None, min_length=3, max_length=4)
    description: str
    customer_email: str
    customer_name: str


class Transaction(BaseModel):
    transaction_id: str
    id: int
    amount: float
    currency: Currency
    payment_method: PaymentMethod
    status: TransactionStatus
    description: str
    customer_email: str
    customer_name: str
    created_at: datetime
    updated_at: datetime
    failure_reason: Optional[str] = None


class RefundRequest(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="Partial refund amount (leave empty for full refund)")
    reason: str


class RefundResponse(BaseModel):
    transaction_id: str
    refund_id: str
    amount: float
    status: str
    message: str


def generate_transaction_id() -> str:
    """Generate a random transaction ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


def simulate_payment_processing() -> tuple[bool, Optional[str]]:
    """
    Simulate payment processing with 90% success rate
    Returns (success, failure_reason)
    """
    # 90% success rate
    if random.random() < 0.9:
        return True, None
    else:
        # Random failure reasons
        failure_reasons = [
            "Insufficient funds",
            "Card declined",
            "Invalid card details",
            "Payment gateway timeout",
            "Bank authorization failed"
        ]
        return False, random.choice(failure_reasons)


# Payment Endpoints
@router.post("/process", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def process_payment(payment: PaymentRequest):
    """
    Process a payment transaction
    
    Simulates payment processing with ~90% success rate
    """
    # Validate card details for card payments
    if payment.payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
        if not payment.card_number or not payment.cvv or not payment.card_holder_name:
            raise HTTPException(
                status_code=400, 
                detail="Card number, CVV, and card holder name are required for card payments"
            )
    
    # Simulate payment processing
    success, failure_reason = simulate_payment_processing()
    
    transaction_status = TransactionStatus.SUCCESS if success else TransactionStatus.FAILED
    transaction_id = generate_transaction_id()
    
    transaction_data = {
        "transaction_id": transaction_id,
        "id": transaction_id_counter["value"],
        "amount": payment.amount,
        "currency": payment.currency,
        "payment_method": payment.payment_method,
        "status": transaction_status,
        "description": payment.description,
        "customer_email": payment.customer_email,
        "customer_name": payment.customer_name,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "failure_reason": failure_reason
    }
    
    transaction_id_counter["value"] += 1
    transactions_storage.append(transaction_data)
    
    return transaction_data


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    status: Optional[TransactionStatus] = None,
    customer_email: Optional[str] = None
):
    """
    Get all transactions with optional filters
    """
    result = transactions_storage
    
    if status:
        result = [t for t in result if t["status"] == status]
    if customer_email:
        result = [t for t in result if t["customer_email"] == customer_email]
    
    return result


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    """
    Get a specific transaction by ID
    """
    for transaction in transactions_storage:
        if transaction["transaction_id"] == transaction_id:
            return transaction
    raise HTTPException(status_code=404, detail="Transaction not found")


@router.post("/transactions/{transaction_id}/refund", response_model=RefundResponse)
async def refund_transaction(transaction_id: str, refund: RefundRequest):
    """
    Refund a transaction (full or partial)
    """
    # Find the transaction
    transaction = None
    transaction_index = None
    for i, txn in enumerate(transactions_storage):
        if txn["transaction_id"] == transaction_id:
            transaction = txn
            transaction_index = i
            break
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if transaction can be refunded
    if transaction["status"] != TransactionStatus.SUCCESS:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot refund transaction with status: {transaction['status']}"
        )
    
    # Determine refund amount
    refund_amount = refund.amount if refund.amount else transaction["amount"]
    
    if refund_amount > transaction["amount"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Refund amount cannot exceed original transaction amount of {transaction['amount']}"
        )
    
    # Update transaction status
    transaction["status"] = TransactionStatus.REFUNDED
    transaction["updated_at"] = datetime.now()
    transactions_storage[transaction_index] = transaction
    
    refund_id = generate_transaction_id()
    
    return RefundResponse(
        transaction_id=transaction_id,
        refund_id=refund_id,
        amount=refund_amount,
        status="completed",
        message=f"Refund of {refund_amount} {transaction['currency']} processed successfully"
    )


@router.get("/transactions/{transaction_id}/status")
async def get_transaction_status(transaction_id: str):
    """
    Get the status of a transaction
    """
    for transaction in transactions_storage:
        if transaction["transaction_id"] == transaction_id:
            return {
                "transaction_id": transaction_id,
                "status": transaction["status"],
                "amount": transaction["amount"],
                "currency": transaction["currency"],
                "updated_at": transaction["updated_at"]
            }
    raise HTTPException(status_code=404, detail="Transaction not found")


@router.post("/validate")
async def validate_payment_details(payment: PaymentRequest):
    """
    Validate payment details without processing
    """
    errors = []
    
    # Validate card details for card payments
    if payment.payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
        if not payment.card_number:
            errors.append("Card number is required")
        elif len(payment.card_number) < 13 or len(payment.card_number) > 19:
            errors.append("Invalid card number length")
        
        if not payment.cvv:
            errors.append("CVV is required")
        elif len(payment.cvv) < 3 or len(payment.cvv) > 4:
            errors.append("Invalid CVV length")
        
        if not payment.card_holder_name:
            errors.append("Card holder name is required")
    
    if payment.amount <= 0:
        errors.append("Amount must be positive")
    
    if errors:
        return {
            "valid": False,
            "errors": errors
        }
    
    return {
        "valid": True,
        "message": "Payment details are valid"
    }


@router.get("/statistics")
async def get_payment_statistics():
    """
    Get payment gateway statistics
    """
    total_transactions = len(transactions_storage)
    
    successful_transactions = [t for t in transactions_storage if t["status"] == TransactionStatus.SUCCESS]
    failed_transactions = [t for t in transactions_storage if t["status"] == TransactionStatus.FAILED]
    refunded_transactions = [t for t in transactions_storage if t["status"] == TransactionStatus.REFUNDED]
    
    total_amount = sum(t["amount"] for t in successful_transactions)
    refunded_amount = sum(t["amount"] for t in refunded_transactions)
    
    return {
        "total_transactions": total_transactions,
        "successful_count": len(successful_transactions),
        "failed_count": len(failed_transactions),
        "refunded_count": len(refunded_transactions),
        "total_amount_processed": total_amount,
        "total_amount_refunded": refunded_amount,
        "success_rate": len(successful_transactions) / total_transactions * 100 if total_transactions > 0 else 0
    }


@router.delete("/transactions/clear")
async def clear_all_transactions():
    """
    Clear all transaction history (for testing)
    """
    global transactions_storage
    count = len(transactions_storage)
    transactions_storage = []
    return {"message": f"Cleared {count} transactions"}


# Include router in the payment app
payment_app.include_router(router)
