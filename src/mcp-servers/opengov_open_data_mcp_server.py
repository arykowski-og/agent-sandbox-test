import os
import asyncio
import json
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
import aiohttp
from mcp.server.fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("CKAN Open Data")

# Default CKAN base URL
DEFAULT_CKAN_BASE_URL = os.environ.get('CKAN_BASE_URL', 'https://ckantesting.ogopendata.com')

@mcp.tool()
async def search_ckan_datasets(
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
    params = {
        'q': query,
        'rows': rows,
        'start': start
    }
    url = f"{effective_base_url}/api/3/action/package_search?{urlencode(params)}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if not response.ok:
                    error_text = await response.text()
                    raise Exception(f"CKAN API error: {response.status} {response.reason} - {error_text}")
                
                data = await response.json()
                
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
        raise Exception(f"Failed to search CKAN datasets: {str(e)}")

@mcp.tool()
async def get_ckan_dataset_details(
    id: str,
    base_url: Optional[str] = None
) -> str:
    """
    Get detailed information about a specific CKAN dataset.
    
    Args:
        id: Dataset name or ID
        base_url: CKAN instance base URL (optional, defaults to environment variable)
    
    Returns:
        JSON string containing detailed dataset information
    """
    resolved_base_url = base_url or DEFAULT_CKAN_BASE_URL
    url = f"{resolved_base_url}/api/3/action/package_show?id={urlencode({'': id})[1:]}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if not response.ok:
                    error_text = await response.text()
                    raise Exception(f"CKAN API error: {response.status} {response.reason} - {error_text}")
                
                full_response = await response.json()
                
                if not full_response.get('success') or not full_response.get('result'):
                    raise Exception('Failed to retrieve dataset details from CKAN API')
                
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
        raise Exception(f"Failed to get dataset details: {str(e)}")

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="stdio") 