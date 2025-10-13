"""
Main server that hosts all three dummy applications:
- Email Server
- ERP System
- Payment Gateway

Each application has its own separate Swagger documentation.
"""
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from email_server import email_app
from erp_system import erp_app
from payment_gateway import payment_app

app = FastAPI(
    title="Supporting Services - Main Server",
    description="Main server hosting Email, ERP, and Payment services",
    version="1.0.0"
)

# Mount each application at different paths
app.mount("/email", email_app)
app.mount("/erp", erp_app)
app.mount("/payment", payment_app)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with links to all service documentation"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supporting Services</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .services {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .service-card {
                background: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .service-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .service-card h2 {
                color: #007bff;
                margin-top: 0;
            }
            .service-card p {
                color: #666;
                margin: 10px 0;
            }
            .service-card a {
                display: inline-block;
                margin-top: 10px;
                padding: 8px 16px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-size: 14px;
            }
            .service-card a:hover {
                background-color: #0056b3;
            }
            .health {
                text-align: center;
                margin-top: 30px;
                padding: 15px;
                background: white;
                border-radius: 8px;
            }
            .health a {
                color: #28a745;
                text-decoration: none;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>🚀 Supporting Services</h1>
        <p style="text-align: center; color: #666;">
            Three dummy applications for development and testing
        </p>
        
        <div class="services">
            <div class="service-card">
                <h2>📧 Email Server</h2>
                <p>Manage inbox and outbox, send and receive emails</p>
                <a href="/email/docs">View Swagger Docs</a>
                <a href="/email/redoc" style="background-color: #6c757d;">View ReDoc</a>
            </div>
            
            <div class="service-card">
                <h2>💼 ERP System</h2>
                <p>Manage customers, invoices, and payments</p>
                <a href="/erp/docs">View Swagger Docs</a>
                <a href="/erp/redoc" style="background-color: #6c757d;">View ReDoc</a>
            </div>
            
            <div class="service-card">
                <h2>💳 Payment Gateway</h2>
                <p>Process payments, refunds, and transactions</p>
                <a href="/payment/docs">View Swagger Docs</a>
                <a href="/payment/redoc" style="background-color: #6c757d;">View ReDoc</a>
            </div>
        </div>
        
        <div class="health">
            <p>✅ All services are running | <a href="/health">Health Check</a></p>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/health")
async def health_check():
    """Health check endpoint for all services"""
    return {
        "status": "healthy",
        "services": {
            "email": {
                "status": "running",
                "docs": "/email/docs"
            },
            "erp": {
                "status": "running",
                "docs": "/erp/docs"
            },
            "payment": {
                "status": "running",
                "docs": "/payment/docs"
            }
        }
    }


if __name__ == "__main__":
    # Get port from environment variable (for Railway/cloud deployments) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print("=" * 60)
    print("🚀 Starting Supporting Services Server")
    print("=" * 60)
    print(f"\n📍 Server: http://localhost:{port}")
    print("\n📚 Swagger Documentation:")
    print(f"   • Email Server:    http://localhost:{port}/email/docs")
    print(f"   • ERP System:      http://localhost:{port}/erp/docs")
    print(f"   • Payment Gateway: http://localhost:{port}/payment/docs")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
