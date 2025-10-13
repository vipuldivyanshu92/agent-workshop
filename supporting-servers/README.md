# Supporting Servers

A Python server that hosts three dummy applications for development and testing:
- **Email Server**: Inbox/Outbox management
- **ERP System**: Customers, invoices, and payments management
- **Payment Gateway**: Payment processing simulation

Each application has its **own separate Swagger documentation**.

## Features

### 1. Email Server (`/email`)
- Send and receive emails
- Inbox management (view, delete, mark as read)
- Outbox management
- Filter emails by sender/recipient

### 2. ERP System (`/erp`)
- Customer management (CRUD operations)
- Invoice management (vendor/supplier invoices)
- Payment tracking
- Outstanding invoices tracking
- ERP statistics and analytics

### 3. Payment Gateway (`/payment`)
- Process payments with multiple payment methods (credit card, debit card, bank transfer, UPI, wallet, PayPal)
- Transaction history
- Refund processing (full or partial)
- Payment validation
- Transaction statistics

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

### Local Development

Start the server:
```bash
python main.py
```

The server will start at `http://localhost:8000`

### Deploy to Railway

Railway is a deployment platform that makes it easy to deploy your application to the cloud.

#### Option 1: Deploy from GitHub (Recommended)

1. Push your code to a GitHub repository
2. Go to [Railway](https://railway.app/)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect the configuration from `railway.json` and `Procfile`
6. Click "Deploy"

#### Option 2: Deploy using Railway CLI

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize a new Railway project (from the `supporting-servers` directory):
```bash
railway init
```

4. Deploy:
```bash
railway up
```

5. Open your deployed application:
```bash
railway open
```

#### Configuration

The application is configured for Railway with:
- **Procfile**: Defines how to start the application
- **railway.json**: Railway-specific configuration with health checks
- **runtime.txt**: Specifies Python version
- **Environment Variables**: The app automatically uses Railway's `PORT` environment variable

#### Railway Environment Variables

The application automatically uses Railway's `PORT` environment variable. 

**Optional Environment Variables:**

- **`BASE_URL`**: The base URL of your deployed application for Swagger documentation
  - **Example**: `https://your-app.railway.app`
  - **Default**: `http://localhost:8000` (for local development)
  - **Purpose**: Updates the Swagger/OpenAPI server URLs to show the correct hosting domain instead of just relative paths
  - **How to set**: In Railway dashboard → Your Project → Variables → Add Variable

If not set, the Swagger docs will default to localhost URLs. For production deployments, it's recommended to set this to your Railway URL.

**Setting BASE_URL in Railway:**
1. Go to your Railway project
2. Click on your service
3. Navigate to "Variables" tab
4. Add: `BASE_URL` = `https://your-app.railway.app` (replace with your actual Railway URL)
5. Redeploy the service

## API Documentation

Each application has its **own separate Swagger documentation**:

### Separate Service Documentation

- **Email Server Swagger**: http://localhost:8000/email/docs
- **Email Server ReDoc**: http://localhost:8000/email/redoc

- **ERP System Swagger**: http://localhost:8000/erp/docs
- **ERP System ReDoc**: http://localhost:8000/erp/redoc

- **Payment Gateway Swagger**: http://localhost:8000/payment/docs
- **Payment Gateway ReDoc**: http://localhost:8000/payment/redoc

### Landing Page

Visit http://localhost:8000 for a beautiful landing page with links to all service documentation.

## API Endpoints

### Email Server Endpoints

Base URL: `/email`

- `GET /email/inbox` - Get all inbox emails
- `GET /email/inbox/{email_id}` - Get specific inbox email
- `DELETE /email/inbox/{email_id}` - Delete inbox email
- `GET /email/outbox` - Get all outbox emails
- `GET /email/outbox/{email_id}` - Get specific outbox email
- `POST /email/send` - Send an email
- `POST /email/inbox/mark-read/{email_id}` - Mark email as read
- `DELETE /email/inbox/clear` - Clear inbox
- `DELETE /email/outbox/clear` - Clear outbox

### ERP System Endpoints

Base URL: `/erp`

**Customers:**
- `GET /erp/customers` - Get all customers
- `GET /erp/customers/{customer_id}` - Get specific customer
- `POST /erp/customers` - Create new customer
- `PUT /erp/customers/{customer_id}` - Update customer
- `DELETE /erp/customers/{customer_id}` - Delete customer

**Invoices:**
- `GET /erp/invoices` - Get all invoices (with filters)
- `GET /erp/invoices/outstanding` - Get outstanding invoices
- `GET /erp/invoices/{invoice_id}` - Get specific invoice
- `POST /erp/invoices` - Create new invoice
- `DELETE /erp/invoices/{invoice_id}` - Delete invoice

**Payments:**
- `GET /erp/payments` - Get all payments
- `GET /erp/payments/{payment_id}` - Get specific payment
- `POST /erp/payments` - Create new payment

**Statistics:**
- `GET /erp/statistics` - Get ERP system statistics

### Payment Gateway Endpoints

Base URL: `/payment`

- `POST /payment/process` - Process a payment
- `GET /payment/transactions` - Get all transactions (with filters)
- `GET /payment/transactions/{transaction_id}` - Get specific transaction
- `POST /payment/transactions/{transaction_id}/refund` - Refund a transaction
- `GET /payment/transactions/{transaction_id}/status` - Get transaction status
- `POST /payment/validate` - Validate payment details
- `GET /payment/statistics` - Get payment statistics
- `DELETE /payment/transactions/clear` - Clear all transactions (testing)

## Example Usage

### Send an Email
```bash
curl -X POST "http://localhost:8000/email/send" \
  -H "Content-Type: application/json" \
  -d '{
    "from_email": "sender@example.com",
    "to_email": "recipient@example.com",
    "subject": "Test Email",
    "body": "This is a test email"
  }'
```

### Create a Customer
```bash
curl -X POST "http://localhost:8000/erp/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "company": "Acme Corp"
  }'
```

### Process a Payment
```bash
curl -X POST "http://localhost:8000/payment/process" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "currency": "USD",
    "payment_method": "credit_card",
    "card_number": "4532015112830366",
    "card_holder_name": "John Doe",
    "cvv": "123",
    "description": "Product purchase",
    "customer_email": "john@example.com",
    "customer_name": "John Doe"
  }'
```

## Data Models

### Email Server
- **Email**: id, from_email, to_email, subject, body, timestamp, status
- **EmailStatus**: sent, delivered, pending, failed

### ERP System
- **Customer**: id, name, email, phone, address, company, created_at
- **Invoice**: id, customer_id, invoice_type, amount, amount_paid, amount_outstanding, due_date, description, vendor_supplier_name, status, created_at
- **InvoiceStatus**: outstanding, partially_paid, paid, overdue, cancelled
- **InvoiceType**: vendor, supplier
- **Payment**: id, invoice_id, amount, payment_method, notes, status, created_at

### Payment Gateway
- **Transaction**: transaction_id, id, amount, currency, payment_method, status, description, customer_email, customer_name, created_at, updated_at, failure_reason
- **TransactionStatus**: pending, processing, success, failed, refunded
- **PaymentMethod**: credit_card, debit_card, bank_transfer, upi, wallet, paypal
- **Currency**: USD, EUR, GBP, INR, JPY

## Architecture

The server uses FastAPI's sub-application mounting feature to provide **three completely separate applications**, each with:
- Its own Swagger UI documentation
- Its own ReDoc documentation
- Independent API endpoints
- Isolated business logic

This architecture allows each service to be:
- Documented separately
- Tested independently
- Potentially extracted into separate microservices later

## Notes

- All data is stored in memory and will be lost when the server restarts
- The payment gateway simulates a ~90% success rate for transactions
- All timestamps are in UTC
- This is a dummy server for development/testing purposes only
- Each service has its own complete OpenAPI specification
