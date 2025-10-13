import asyncio

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace, HostedMCPTool, ModelSettings
import os

"""
This is a multi-agent system that processes the invoice from emails and updates the ERP system and makes payments.
"""

# Validate required environment variables
required_vars = ["OPENAI_API_KEY", "WEATHER_MCP", "MCP_AUTH_TOKEN"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

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
    instructions="Your read the invoice pdf and extract the invoice number, amount, due date, and vendor name",
    handoff_description="An invoice agent that can read and extract the invoice number, amount, due date, and vendor name",
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
    instructions="You check the invoice and update the ERP system",
    handoff_description="An ERP agent that can check the invoice and update the ERP system",
    tools=[erp_mcp_tool],
    model="gpt-4o-mini",
    model_settings=ModelSettings(
        temperature=0.1,
        top_p=0.1,
        max_tokens=2048,
        store=True
    )
)

payments_agent = Agent(
    name="payments_agent",
    instructions="You make payments to the external system and update the ERP system",
    handoff_description="An payments agent that can make payments to the external system and update the ERP system",
    tools=[payment_mcp_tool],
    model="gpt-4o-mini",
    model_settings=ModelSettings(
        temperature=0.1,
        top_p=0.1,
        max_tokens=2048,
        store=True
    )
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools in order."
        "You never translate on your own, you always use the provided tools."
    ),
    tools=[
        email_agent.as_tool(
            tool_name="email_agent",
            tool_description="Email agent that can read and send emails",
        ),
        invoice_agent.as_tool(
            tool_name="invoice_agent",
            tool_description="Invoice agent that can read and extract the invoice number, amount, due date, and vendor name",
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
            await asyncio.sleep(10)
            await Runner.run(email_agent, "Check the email for new invoices")
            # get the last message from the email agent
            last_message = email_agent.get_last_message()
            if last_message:
                # call the orchestrator agent to process the invoice
                await Runner.run(orchestrator_agent, last_message.content)
                # get the last message from the orchestrator agent
                last_message = orchestrator_agent.get_last_message()
                if last_message:
                    # call the synthesizer agent to synthesize the response
                    await Runner.run(synthesizer_agent, last_message.content)
                    # get the last message from the synthesizer agent
                    last_message = synthesizer_agent.get_last_message()
                    if last_message:
                        # print the response
                        print(f"  - Synthesizer step: {last_message.content}")
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