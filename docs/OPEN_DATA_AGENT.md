# Open Data Agent

This project now includes an **Open Data Agent** that can search and analyze open government datasets through CKAN data portals.

## Features

The Open Data Agent can:
- 🔍 Search for datasets using keywords
- 📊 Get detailed information about specific datasets  
- 📈 Analyze dataset metadata, resources, and descriptions
- 🔗 Help users understand what data is available and how to access it

## Available Tools

### search_ckan_datasets
Search for datasets in CKAN open data portals using keywords.

**Parameters:**
- `query` (required): Search keywords or query string
- `base_url` (optional): CKAN instance URL (defaults to environment variable)
- `rows` (optional): Number of results to return (default: 5, max: 100)
- `start` (optional): Starting index for pagination (default: 0)

### get_ckan_dataset_details
Get detailed information about a specific CKAN dataset.

**Parameters:**
- `dataset_id` (required): Dataset name or ID
- `base_url` (optional): CKAN instance URL (defaults to environment variable)

## How to Use

### 1. Start the Servers

Run the startup script:
```bash
./run.sh
```

This will start both:
- LangGraph API server on http://localhost:2024
- Agent Chat UI on http://localhost:3000

### 2. Access the Open Data Agent

1. Open your browser to http://localhost:3000
2. In the configuration form:
   - **Deployment URL**: `http://localhost:2024` (should be pre-filled)
   - **Assistant / Graph ID**: Enter `open_data_agent` (instead of the default "agent")
   - **API Key**: Leave blank for local usage
3. Click "Continue"

### 3. Start Chatting with Open Data

Try these example queries:

**Basic Search:**
```
Search for datasets about climate change
```

**Specific Topics:**
```
Find transportation datasets in the portal
```

**Getting Details:**
```
Tell me more about dataset ID: abc123
```

**Analysis Requests:**
```
What environmental datasets are available and what formats do they come in?
```

## Configuration

### Environment Variables

You can configure the default CKAN portal by setting:
```bash
export CKAN_BASE_URL="https://your-ckan-portal.com"
```

The default portal is: `https://ckantesting.ogopendata.com`

### Switching Between Agents

This project includes two agents:

1. **Weather Agent** (default): Assistant ID = `agent`
   - Simple weather information agent
   
2. **Open Data Agent**: Assistant ID = `open_data_agent`
   - CKAN dataset search and analysis

To switch agents, change the "Assistant / Graph ID" in the Chat UI settings.

## Example Interactions

### Finding Climate Data
```
User: I need datasets about climate change and global warming

Open Data Agent: I'll search for climate-related datasets for you.

[Agent uses search_ckan_datasets with query "climate change global warming"]

I found 15 datasets related to climate change. Here are the top 5:

1. **Global Temperature Anomalies** (ID: temp-anomalies-2023)
   - Organization: National Weather Service
   - Description: Monthly global temperature anomalies from 1880 to present...
   - Formats: CSV, JSON
   - Last updated: 2023-12-01

2. **CO2 Emissions by Country** (ID: co2-emissions-country)
   - Organization: Environmental Protection Agency
   - Description: Annual CO2 emissions data by country from 1990-2022...
   
[continues with more results]

Would you like me to get more details about any specific dataset?
```

### Getting Dataset Details
```
User: Tell me more about the Global Temperature Anomalies dataset

Open Data Agent: Let me get the detailed information for that dataset.

[Agent uses get_ckan_dataset_details with ID "temp-anomalies-2023"]

Here are the complete details for the Global Temperature Anomalies dataset:

**Dataset Information:**
- Title: Global Temperature Anomalies
- Organization: National Weather Service  
- License: Creative Commons Attribution
- Created: 2020-01-15
- Last Modified: 2023-12-01

**Description:**
This dataset contains monthly global temperature anomalies relative to the 20th century average. Data is collected from weather stations worldwide and processed to show deviations from long-term averages...

**Available Resources:**
1. Monthly Data (CSV) - 2.3MB
   - URL: https://portal.com/temp-data.csv
2. Annual Summaries (JSON) - 150KB  
   - URL: https://portal.com/temp-annual.json
3. Methodology Document (PDF) - 850KB
   - URL: https://portal.com/methodology.pdf

**Tags:** climate, temperature, weather, global warming, anomalies

You can access this dataset directly at: https://ckantesting.ogopendata.com/dataset/temp-anomalies-2023
```

## Technical Implementation

The Open Data Agent is built using:
- **LangGraph**: For agent orchestration
- **LangChain**: For tool integration and LLM interaction  
- **CKAN API**: For accessing open data portals
- **OpenAI GPT**: For natural language understanding and generation

Key files:
- `open_data_server.py`: Main agent implementation
- `langgraph.json`: Graph configuration
- `src/mcp/opengov_open_data_mcp_server.py`: MCP server implementation (alternative approach)

## Troubleshooting

### Agent Not Found
If you get "assistant ID not found", make sure:
1. You entered `open_data_agent` exactly (case-sensitive)
2. The LangGraph server is running
3. Check the langgraph.json file includes the open_data_agent graph

### API Errors
If you get CKAN API errors:
1. Check your internet connection
2. The default CKAN portal might be temporarily unavailable
3. Try setting a different CKAN_BASE_URL environment variable

### No Results
If searches return no results:
1. Try broader search terms
2. The CKAN portal might have limited data
3. Check if the portal URL is correct

## Contributing

To add support for additional data portals or enhance the agent:
1. Modify the `search_ckan_datasets` and `get_ckan_dataset_details` functions
2. Update the agent prompt to include new capabilities
3. Test with different CKAN portals 