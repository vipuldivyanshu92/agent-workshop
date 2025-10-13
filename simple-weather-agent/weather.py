import asyncio

from pydantic import BaseModel

from agents import Agent, Runner, Usage, function_tool


class Weather(BaseModel):
    city: str
    temperature_range: str
    conditions: str


@function_tool
def get_weather(city: str) -> Weather:
    """Get the current weather information for a specified city."""
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")


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
        instructions="You are a helpful assistant that can check weather information. Use tools if needed.",
        tools=[get_weather],
    )

    print("=== Weather Assistant ===")
    print("Ask me about the weather! (Type 'quit' or 'exit' to stop)\n")

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
            print(f"\nAssistant: {result.final_output}\n")
            
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