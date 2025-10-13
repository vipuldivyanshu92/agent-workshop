# Weather Assistant Agents

This directory contains two weather assistant implementations:

## 1. weather.py - Simple Agent with Local Tool
A basic weather agent that uses a local function tool to simulate weather data.

**Usage:**
```bash
python weather.py
```

## 2. weather-with-mcp.py - Agent with Remote MCP Integration
An advanced weather agent that connects to a remote MCP (Model Context Protocol) server for real weather data.

**Setup:**

1. **Install dependencies:**
   ```bash
   pip install -r ../supporting-servers/requirements.txt
   ```

2. **Create .env file:**
   ```bash
   # From the project root directory
   cp env.template .env
   ```

3. **Edit .env with your credentials:**
   ```bash
   # Add your actual values to .env
   OPENAI_API_KEY=sk-your-actual-openai-key
   MCP_SERVER_URL=https://your-mcp-server.com/mcp
   MCP_AUTH_TOKEN=your-actual-auth-token
   ```

4. **Run the agent:**
   ```bash
   python weather-with-mcp.py
   ```

**Features:**
- ✅ Interactive loop - ask multiple questions
- ✅ Environment variable validation
- ✅ Graceful error handling
- ✅ Exit with 'quit', 'exit', or Ctrl+C
- ✅ Remote MCP tool integration

**Available MCP Tools:**
- `get_weather` - Get current weather for a city
- `get_forecast` - Get weather forecast
- `get_current_conditions` - Get current weather conditions

