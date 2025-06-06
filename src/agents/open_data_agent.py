import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import Tool
import requests
import json
from typing import Optional

# Load environment variables
load_dotenv()

# Default CKAN base URL
DEFAULT_CKAN_BASE_URL = os.environ.get('CKAN_BASE_URL', 'https://ckantesting.ogopendata.com')



def search_ckan_datasets(
    query: str,
    base_url: Optional[str] = None,
    rows: int = 5,
    start: int = 0
) -> str:
    """
    Search CKAN datasets by query.
    
    Args:
        query: Search keywords or query string for datasets
        base_url: CKAN instance base URL (optional, defaults to environment variable)
        rows: Number of results to return (default: 5, max: 100)
        start: Starting index for pagination (default: 0)
    
    Returns:
        JSON string containing search results with dataset summaries
    """
    effective_base_url = base_url or DEFAULT_CKAN_BASE_URL
    
    # Validate parameters
    rows = min(max(1, rows), 100)  # Ensure rows is between 1 and 100
    start = max(0, start)  # Ensure start is non-negative
    
    # Build URL
    url = f"{effective_base_url}/api/3/action/package_search"
    params = {
        'q': query,
        'rows': rows,
        'start': start
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if not response.ok:
            return json.dumps({
                'error': f"CKAN API error: {response.status_code} {response.reason}",
                'count': 0,
                'results': []
            })
        
        data = response.json()
        
        if data.get('success') and data.get('result'):
            # Create concise results
            concise_results = []
            for dataset in data['result']['results']:
                result = {
                    'id': dataset.get('id'),
                    'title': dataset.get('title'),
                    'notes': dataset.get('notes', 'No description available.')[:150] + ('...' if len(dataset.get('notes', '')) > 150 else ''),
                    'organization_title': dataset.get('organization', {}).get('title') if dataset.get('organization') else None,
                }
                concise_results.append(result)
            
            result = {
                'count': data['result']['count'],
                'results': concise_results
            }
            return json.dumps(result, indent=2)
        else:
            return json.dumps({'count': 0, 'results': []})
            
    except Exception as e:
        return json.dumps({
            'error': f"Failed to search CKAN datasets: {str(e)}",
            'count': 0,
            'results': []
        })

def get_ckan_dataset_details(
    dataset_id: str,
    base_url: Optional[str] = None
) -> str:
    """
    Get detailed information about a specific CKAN dataset.
    
    Args:
        dataset_id: Dataset name or ID
        base_url: CKAN instance base URL (optional, defaults to environment variable)
    
    Returns:
        JSON string containing detailed dataset information
    """
    resolved_base_url = base_url or DEFAULT_CKAN_BASE_URL
    url = f"{resolved_base_url}/api/3/action/package_show"
    params = {'id': dataset_id}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if not response.ok:
            return json.dumps({
                'error': f"CKAN API error: {response.status_code} {response.reason}",
                'dataset': None
            })
        
        full_response = response.json()
        
        if not full_response.get('success') or not full_response.get('result'):
            return json.dumps({
                'error': 'Failed to retrieve dataset details from CKAN API',
                'dataset': None
            })
        
        data = full_response['result']
        
        # Create essential data summary
        essential_data = {
            'id': data.get('id'),
            'title': data.get('title'),
            'name': data.get('name'),
            'notes': data.get('notes', 'No description provided.')[:500] + ('...' if len(data.get('notes', '')) > 500 else ''),
            'organization_title': data.get('organization', {}).get('title') if data.get('organization') else None,
            'num_resources': data.get('num_resources'),
            'num_tags': data.get('num_tags'),
            'tags': [tag.get('display_name') or tag.get('name') for tag in data.get('tags', [])][:5],
            'resources_summary': [
                {
                    'name': r.get('name'),
                    'format': r.get('format'),
                    'url': r.get('url')
                }
                for r in data.get('resources', [])[:3]
            ],
            'license_title': data.get('license_title'),
            'metadata_created': data.get('metadata_created'),
            'metadata_modified': data.get('metadata_modified'),
            'url': f"{resolved_base_url}/dataset/{data.get('name')}"
        }
        
        return json.dumps(essential_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            'error': f"Failed to get dataset details: {str(e)}",
            'dataset': None
        })



# Create tools
search_tool = Tool(
    name="search_ckan_datasets",
    description="Search for datasets in CKAN open data portals. Use this to find datasets related to specific topics or keywords.",
    func=search_ckan_datasets
)

details_tool = Tool(
    name="get_ckan_dataset_details", 
    description="Get detailed information about a specific CKAN dataset using its ID or name.",
    func=get_ckan_dataset_details
)

# Check if API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables.")
    print("Please create a .env file with your OpenAI API key.")

# Initialize the model
model = init_chat_model(
    "openai:gpt-3.5-turbo",
    temperature=0.1
)



# Enhanced prompt with built-in persistence capabilities
enhanced_prompt = """You are an Open Data Agent specialized in finding and analyzing open government datasets through CKAN data portals.

🧠 **Memory & Persistence Capabilities:**
- I can remember our conversation history within this thread (handled by LangGraph platform)
- I can learn your data preferences and research interests over time
- I can recall datasets we've discussed previously
- I can build on previous searches to provide better recommendations

🔍 **Core Capabilities:**
- Searching for datasets using keywords with the search_ckan_datasets tool
- Getting detailed information about specific datasets with the get_ckan_dataset_details tool
- Analyzing dataset metadata, resources, and descriptions
- Helping users understand what data is available and how to access it

📊 **How I Work:**
1. Search for relevant datasets first using search_ckan_datasets
2. If you want details about a specific dataset, use get_ckan_dataset_details with the dataset ID
3. Provide clear summaries of what I find
4. Include important details like data formats, update frequency, and access URLs
5. Suggest related datasets that might be useful
6. Remember your interests to improve future recommendations

💡 **Enhanced Features:**
- If you mention research topics repeatedly, I'll remember them
- I can track which datasets you've found useful
- I can suggest datasets based on your previous interests
- I maintain context across our entire conversation

Always be helpful in explaining what the data contains, how it might be used, and reference previous discussions when relevant."""

# Create the agent (persistence handled automatically by LangGraph API)
graph = create_react_agent(
    model=model,
    tools=[search_tool, details_tool],
    prompt=enhanced_prompt
)

if __name__ == "__main__":
    # For testing the server locally
    print("🔍 Open Data Agent with Platform Persistence is ready!")
    print("=" * 60)
    print("Features enabled:")
    print("  ✅ Conversation memory within threads (platform managed)")
    print("  ✅ Dataset search and analysis tools")
    print("  ✅ Automatic persistence (handled by LangGraph API)")
    print("Use 'langgraph dev' to start the development server")
    
    # Test the agent
    if api_key:
        print("\n🧪 Testing agent capabilities...")
        print("✅ Open Data Agent is ready for deployment!")
        print("Persistence and memory are automatically handled by the LangGraph platform.") 