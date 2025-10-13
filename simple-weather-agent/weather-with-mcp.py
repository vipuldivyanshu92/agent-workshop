"""
Weather Assistant with Remote MCP Integration

This agent connects to a remote MCP (Model Context Protocol) server to fetch weather data.

Configuration:
1. Copy env.template to .env: cp env.template .env
2. Edit .env and add your actual API keys and MCP server URL
3. Run the agent: python weather-with-mcp.py

Required environment variables in .env:
- OPENAI_API_KEY: Your OpenAI API key
- MCP_SERVER_URL: Your MCP server endpoint
- MCP_AUTH_TOKEN: Authentication token for MCP server
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from agents import Agent, Runner, Usage, HostedMCPTool, ModelSettings

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Validate required environment variables
required_vars = ["OPENAI_API_KEY", "WEATHER_MCP", "MCP_AUTH_TOKEN"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
    print(f"\nPlease create a .env file in the project root with:")
    print(f"  cp env.template .env")
    print(f"\nThen edit .env and add your actual values.")
    exit(1)


# Configure the remote MCP tool for weather services
weather_mcp_tool = HostedMCPTool(tool_config={
    "type": "mcp",
    "server_label": "weather-service",
    # "allowed_tools": [
    #     "get_weather",
    #     "get_forecast",
    #     "get_current_conditions"
    # ],
    # "authorization": os.getenv("MCP_AUTH_TOKEN"),
    "require_approval": "never",
    "server_url": os.getenv("WEATHER_MCP")
})


def print_usage(usage: Usage) -> None:
    print("\n=== Usage ===")
    print(f"Requests: {usage.requests}")
    print(f"Input tokens: {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
    print(f"Total tokens: {usage.total_tokens}")


# Main code entrypoint
async def main() -> None:
    agent = Agent(
        name="Weather Assistant",
        instructions="You are a helpful assistant that can check weather information using the remote MCP weather service. Use the available tools to get weather data for cities.",
        tools=[weather_mcp_tool],
        model="gpt-4o-mini",
        model_settings=ModelSettings(
            temperature=0.1,
            top_p=0.1,
            max_tokens=2048,
            store=True
        )
    )

    print("=== Weather Assistant with Remote MCP ===")
    print(f"MCP Server: {os.getenv('MCP_SERVER_URL')}")
    print(f"OpenAI API: {'✓ Configured' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}")
    print("\nAsk me about the weather! (Type 'quit' or 'exit' to stop)\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Run the agent with user input
            result = await Runner.run(agent, user_input)
            
            # Print the response
            print(f"\nAssistant: {result}\n")
            
            # Optionally print usage for each interaction
            # print_usage(result.context_wrapper.usage)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            continue


if __name__ == "__main__":
    asyncio.run(main())