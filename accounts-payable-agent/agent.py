import asyncio
import io
from multiprocessing import current_process
import re
import requests
from typing import Optional

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace, HostedMCPTool, ModelSettings, function_tool
import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel
try:
    import PyPDF2
except ImportError:
    print("Warning: PyPDF2 not installed. Install with: pip install PyPDF2")
    PyPDF2 = None

"""
This is a multi-agent system that processes the invoice from emails and updates the ERP system and makes payments.
"""
# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# Validate required environment variables
required_vars = ["OPENAI_API_KEY", "EMAIL_MCP", "PAYMENT_MCP", "ERP_MCP"]
missing_vars = [var for var in required_vars if not os.getenv(var)]


# Helper functions for PDF processing
def convert_google_drive_url(url: str) -> str:
    """
    Convert Google Drive share URL to direct download URL
    
    Args:
        url: Google Drive share URL (e.g., https://drive.google.com/file/d/FILE_ID/view?usp=sharing)
    
    Returns:
        Direct download URL
    """
    # Extract file ID from Google Drive URL
    patterns = [
        r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    return url


def download_pdf_from_url(url: str) -> Optional[bytes]:
    """
    Download PDF content from a URL
    
    Args:
        url: URL to download PDF from
    
    Returns:
        PDF content as bytes, or None if download fails
    """
    try:
        # Convert Google Drive URL if necessary
        if "drive.google.com" in url:
            url = convert_google_drive_url(url)
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Check if content is PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower() and not url.endswith('.pdf'):
            print(f"Warning: Content type is {content_type}, may not be a PDF")
        
        return response.content
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None


def parse_pdf_content(pdf_bytes: bytes) -> str:
    """
    Parse PDF content and extract text
    
    Args:
        pdf_bytes: PDF content as bytes
    
    Returns:
        Extracted text from PDF
    """
    if PyPDF2 is None:
        return "Error: PyPDF2 not installed. Please install it with: pip install PyPDF2"
    
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        
        return text.strip()
    except Exception as e:
        return f"Error parsing PDF: {e}"


@function_tool
def read_pdf_from_url(url: str) -> str:
    """
    Download and parse PDF from URL (including Google Drive links). Returns the extracted text content from the PDF.
    
    Args:
        url: URL of the PDF file. Supports direct URLs and Google Drive share links.
    
    Returns:
        Extracted text from the PDF
    """
    pdf_bytes = download_pdf_from_url(url)
    if pdf_bytes is None:
        return f"Failed to download PDF from URL: {url}"
    
    return parse_pdf_content(pdf_bytes)

# MCP Tools
email_mcp_tool = HostedMCPTool(tool_config={
    "type": "mcp",
    "server_label": "email-service",
    "require_approval": "never",
    "server_url": os.getenv("EMAIL_MCP")
})

payment_mcp_tool = HostedMCPTool(tool_config={
    "type": "mcp",
    "server_label": "payment-service",
    "require_approval": "never",
    "server_url": os.getenv("PAYMENT_MCP")
})

erp_mcp_tool = HostedMCPTool(tool_config={
    "type": "mcp",
    "server_label": "erp-service",
    "require_approval": "never",
    "server_url": os.getenv("ERP_MCP")
})

email_agent = Agent(
    name="email_agent",
    instructions="You read and send emails",
    handoff_description="An email agent that can read and send emails",
    tools=[email_mcp_tool],
    model="gpt-4o-mini",
    model_settings=ModelSettings(
        temperature=0.1,
        top_p=0.1,
        max_tokens=2048,
        store=True
    )
)

invoice_agent = Agent(
    name="invoice_agent",
    instructions=(
        "You read invoice PDFs and extract key information. "
        "You can read PDFs from URLs (including Google Drive links) using the read_pdf_from_url tool. "
        "Extract the following information from invoices: invoice number, amount, due date, and vendor name. "
        "If given a URL, use the tool to download and read the PDF first."
    ),
    handoff_description="An invoice agent that can read PDFs from URLs and extract invoice number, amount, due date, and vendor name",
    tools=[read_pdf_from_url],
    model="gpt-4o-mini",
    model_settings=ModelSettings(
        temperature=0.1,
        top_p=0.1,
        max_tokens=2048,
        store=True
    )
)

erp_agent = Agent(
    name="erp_agent",
    instructions="You check the invoice and update the ERP system, use invoice_type as supplier or vendor",
    handoff_description="An ERP agent that can check the invoice and update the ERP system",
    tools=[erp_mcp_tool],
    model="o3-mini",
    # model_settings=ModelSettings(
    #     temperature=0.1,
    #     top_p=0.1,
    #     max_tokens=2048,
    #     store=True
    # )
)

class Payment(BaseModel):
    amount: int
    currency: str
    invoice_id: str
    status: str

@function_tool
def make_payment(amount: int, currency: str, invoice_id: str) -> Payment:
    """Get the current weather information for a specified city."""
    return Payment(amount=amount, currency=currency, invoice_id=invoice_id,status="success")

payments_agent = Agent(
    name="payments_agent",
    instructions="You make payments to the external system and update the ERP system",
    handoff_description="An payments agent that can make payments to the external system and update the ERP system",
    tools=[make_payment],
    model="o3-mini",
    # model_settings=ModelSettings(
    #     temperature=0.1,
    #     top_p=0.1,
    #     max_tokens=2048,
    #     store=True
    # )
)

orchestrator_agent = Agent(
    model="o3-mini",
    name="orchestrator_agent",
    instructions=(
        "You are an orchestrator agent that processes invoices from emails and manages payments. "
        "Workflow: "
        "1. If given a PDF URL (including Google Drive links), use the invoice_agent to download and extract invoice details "
        "2. If given base64 attachment, convert to PDF and extract invoice details "
        "3. Extract: invoice number, amount, due date, vendor name "
        "4. Use erp_agent to check if invoice exists in ERP system "
        "5. If not found, create new invoice in ERP system "
        "6. If found or after creating, use payments_agent to make payment to vendor "
        "7. Update ERP system with payment status"
    ),
    tools=[
        email_agent.as_tool(
            tool_name="email_agent",
            tool_description="Email agent that can read and send emails",
        ),
        invoice_agent.as_tool(
            tool_name="invoice_agent",
            tool_description="Invoice agent that takes the email input and uses the url from the email and read and extract the invoice number, amount, due date, and vendor name",
        ),
        payments_agent.as_tool(
            tool_name="payments_agent",
            tool_description="Payments agent that can make payments to the external system and update the ERP system",
        ),
        erp_agent.as_tool(
            tool_name="erp_agent",
            tool_description="ERP agent that can check the invoice and update the ERP system",
        ),
    ],
)

synthesizer_agent = Agent(
    name="synthesizer_agent",
    instructions="You synthesize the response from the orchestrator agent",
    model="gpt-4o-mini",
    model_settings=ModelSettings(
        temperature=0.1,
        top_p=0.1,
        max_tokens=2048,
        store=True
    )
)


async def main():
    # 
    # Every minute, check the email and process the invoice
    while True:
        try:
            print("Checking the email for new invoices from the last the email to email address " + "recipient@example.com")
            # Run the email agent to check for new invoices
            email_result = await Runner.run(email_agent, "Get recipient@example.com email")

            # Get the final output from the email agent
            if email_result.final_output:
                print(f"  - Email agent: {email_result.final_output}")
                
                invoice_result = await Runner.run(invoice_agent, email_result.final_output)

                print(f"  - Invoice agent: {invoice_result.final_output}")

                erp_result = await Runner.run(erp_agent, invoice_result.final_output)

                print(f"  - ERP agent: {erp_result.final_output}")

                payments_result = await Runner.run(payments_agent, erp_result.final_output)

                print(f"  - Payments agent: {payments_result.final_output}")

                # synthesizer_result = await Runner.run(synthesizer_agent, payments_result.final_output)

                # print(f"  - Synthesizer agent: {synthesizer_result.final_output}")

                # Call the orchestrator agent to process the invoice
                # orchestrator_result = await Runner.run(starting_agent=orchestrator_agent, input=email_result.final_output)
                
                # # Get the final output from the orchestrator agent
                # if orchestrator_result.final_output:
                #     print(f"  - Orchestrator agent: {orchestrator_result.final_output}")
                    
                #     # Call the synthesizer agent to synthesize the response
                #     synthesizer_result = await Runner.run(synthesizer_agent, orchestrator_result.to_input_list())
                    
                #     # Print the final synthesized response
                #     if synthesizer_result.final_output:
                #         print(f"  - Synthesizer agent: {synthesizer_result.final_output}")
            await asyncio.sleep(30)
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            continue

    # msg = input("Hi! What would you like to process? ")

    # # Run the entire orchestration in a single trace
    # with trace("Orchestrator evaluator"):
    #     orchestrator_result = await Runner.run(orchestrator_agent, msg)

    #     for item in orchestrator_result.new_items:
    #         if isinstance(item, MessageOutputItem):
    #             text = ItemHelpers.text_message_output(item)
    #             if text:
    #                 print(f"  - Translation step: {text}")

    #     synthesizer_result = await Runner.run(
    #         synthesizer_agent, orchestrator_result.to_input_list()
    #     )

    # print(f"\n\nFinal response:\n{synthesizer_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())