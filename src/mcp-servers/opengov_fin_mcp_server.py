#!/usr/bin/env python3
"""
OpenGov FIN GraphQL MCP Server

This MCP server provides tools to interact with the OpenGov FIN GraphQL API.
It supports JWT Bearer token authentication and provides GraphQL introspection and query execution.
Based on the mcp-graphql approach: https://github.com/blurrah/mcp-graphql
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from mcp.server import FastMCP
from dotenv import load_dotenv

# Import JSON normalizer for handling large responses
try:
    from .json_normalizer import normalize_graphql_response
    NORMALIZER_AVAILABLE = True
except ImportError:
    # Fallback if normalizer not available
    def normalize_graphql_response(response, context="graphql"):
        return response
    NORMALIZER_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Initialize MCP server
mcp = FastMCP("OpenGov FIN GraphQL")

class OpenGovFINGraphQLClient:
    """Client for OpenGov FIN GraphQL API"""
    
    def __init__(self):
        self.endpoint = os.getenv("OG_FIN_GRAPHQL_ENDPOINT", "https://opengovdemo.fms.opengov.com/oci/graphql")
        self.bearer_token = os.getenv("OG_FIN_BEARER_TOKEN")
        self.allow_mutations = os.getenv("OG_FIN_ALLOW_MUTATIONS", "false").lower() == "true"
        self.cached_schema = None
        
        if not self.bearer_token:
            raise ValueError("OG_FIN_BEARER_TOKEN environment variable is required")
    
    async def make_graphql_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Make GraphQL request to the endpoint"""
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        
        payload = {
            "query": query
        }
        
        if variables:
            payload["variables"] = variables
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.endpoint, headers=headers, json=payload) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    return {
                        "error": f"GraphQL request failed with status {response.status}",
                        "status": response.status,
                        "details": error_text,
                        "endpoint": self.endpoint
                    }
                
                result = await response.json()
                return result
    
    async def introspect_schema(self) -> Dict:
        """Introspect the GraphQL schema"""
        if self.cached_schema:
            return self.cached_schema
        
        introspection_query = """
        query IntrospectionQuery {
          __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
              ...FullType
            }
            directives {
              name
              description
              locations
              args {
                ...InputValue
              }
            }
          }
        }

        fragment FullType on __Type {
          kind
          name
          description
          fields(includeDeprecated: true) {
            name
            description
            args {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }

        fragment InputValue on __InputValue {
          name
          description
          type { ...TypeRef }
          defaultValue
        }

        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        result = await self.make_graphql_request(introspection_query)
        if "error" not in result:
            self.cached_schema = result
        
        return result
    
    def format_schema_as_sdl(self, schema_data: Dict) -> str:
        """Convert introspection result to SDL format for better readability"""
        if "error" in schema_data:
            return f"Error retrieving schema: {schema_data['error']}"
        
        if "data" not in schema_data or "__schema" not in schema_data["data"]:
            return "Invalid schema data received"
        
        schema = schema_data["data"]["__schema"]
        sdl_parts = []
        
        # Add schema definition
        schema_def_parts = []
        if schema.get("queryType"):
            schema_def_parts.append(f"query: {schema['queryType']['name']}")
        if schema.get("mutationType"):
            schema_def_parts.append(f"mutation: {schema['mutationType']['name']}")
        if schema.get("subscriptionType"):
            schema_def_parts.append(f"subscription: {schema['subscriptionType']['name']}")
        
        if schema_def_parts:
            sdl_parts.append(f"schema {{\n  {chr(10).join(schema_def_parts)}\n}}")
        
        # Process types
        for type_info in schema.get("types", []):
            if type_info["name"].startswith("__"):
                continue  # Skip introspection types
            
            type_sdl = self._format_type_as_sdl(type_info)
            if type_sdl:
                sdl_parts.append(type_sdl)
        
        return "\n\n".join(sdl_parts)
    
    def _format_type_as_sdl(self, type_info: Dict) -> str:
        """Format a single type as SDL"""
        kind = type_info["kind"]
        name = type_info["name"]
        description = type_info.get("description")
        
        sdl = ""
        if description:
            sdl += f'"""{description}"""\n'
        
        if kind == "OBJECT":
            interfaces = type_info.get("interfaces", [])
            implements = ""
            if interfaces:
                interface_names = [iface["name"] for iface in interfaces]
                implements = f" implements {' & '.join(interface_names)}"
            
            sdl += f"type {name}{implements} {{\n"
            for field in type_info.get("fields", []):
                field_sdl = self._format_field_as_sdl(field)
                sdl += f"  {field_sdl}\n"
            sdl += "}"
        
        elif kind == "INPUT_OBJECT":
            sdl += f"input {name} {{\n"
            for field in type_info.get("inputFields", []):
                field_sdl = self._format_input_field_as_sdl(field)
                sdl += f"  {field_sdl}\n"
            sdl += "}"
        
        elif kind == "ENUM":
            sdl += f"enum {name} {{\n"
            for value in type_info.get("enumValues", []):
                value_sdl = value["name"]
                if value.get("description"):
                    sdl += f'  """{value["description"]}"""\n'
                sdl += f"  {value_sdl}\n"
            sdl += "}"
        
        elif kind == "INTERFACE":
            sdl += f"interface {name} {{\n"
            for field in type_info.get("fields", []):
                field_sdl = self._format_field_as_sdl(field)
                sdl += f"  {field_sdl}\n"
            sdl += "}"
        
        elif kind == "UNION":
            possible_types = type_info.get("possibleTypes", [])
            if possible_types:
                type_names = [t["name"] for t in possible_types]
                sdl += f"union {name} = {' | '.join(type_names)}"
        
        elif kind == "SCALAR":
            sdl += f"scalar {name}"
        
        return sdl
    
    def _format_field_as_sdl(self, field: Dict) -> str:
        """Format a field as SDL"""
        name = field["name"]
        type_str = self._format_type_ref(field["type"])
        args = field.get("args", [])
        
        if args:
            arg_strs = []
            for arg in args:
                arg_str = f"{arg['name']}: {self._format_type_ref(arg['type'])}"
                if arg.get("defaultValue"):
                    arg_str += f" = {arg['defaultValue']}"
                arg_strs.append(arg_str)
            return f"{name}({', '.join(arg_strs)}): {type_str}"
        else:
            return f"{name}: {type_str}"
    
    def _format_input_field_as_sdl(self, field: Dict) -> str:
        """Format an input field as SDL"""
        name = field["name"]
        type_str = self._format_type_ref(field["type"])
        
        result = f"{name}: {type_str}"
        if field.get("defaultValue"):
            result += f" = {field['defaultValue']}"
        
        return result
    
    def _format_type_ref(self, type_ref: Dict) -> str:
        """Format a type reference as SDL"""
        if type_ref["kind"] == "NON_NULL":
            return f"{self._format_type_ref(type_ref['ofType'])}!"
        elif type_ref["kind"] == "LIST":
            return f"[{self._format_type_ref(type_ref['ofType'])}]"
        else:
            return type_ref["name"]

# Global client instance - initialized lazily
client = None

def get_client():
    """Get or create the OpenGov FIN GraphQL client instance"""
    global client
    if client is None:
        client = OpenGovFINGraphQLClient()
    return client

@mcp.tool()
async def introspect_schema(include_full_sdl: bool = False) -> Dict:
    """
    Introspect the OpenGov FIN GraphQL schema to discover available types and operations.
    
    Args:
        include_full_sdl (bool): Whether to include the full SDL schema (can be very large)
    
    Returns:
        Dict: Schema summary with type counts and available operations
    """
    client = get_client()
    schema_data = await client.introspect_schema()
    
    if "error" in schema_data:
        return schema_data
    
    # Create a summary instead of returning the full schema
    if "data" in schema_data and "__schema" in schema_data["data"]:
        schema = schema_data["data"]["__schema"]
        
        # Count types by kind
        type_counts = {}
        custom_types = []
        for type_info in schema.get("types", []):
            if not type_info["name"].startswith("__"):
                kind = type_info["kind"]
                type_counts[kind] = type_counts.get(kind, 0) + 1
                custom_types.append({
                    "name": type_info["name"],
                    "kind": kind,
                    "description": (type_info.get("description", "")[:100] + "...") if type_info.get("description") and len(type_info.get("description", "")) > 100 else type_info.get("description", "No description")
                })
        
        # Get query operations count
        query_type = schema.get("queryType")
        query_ops_count = 0
        if query_type:
            for type_info in schema["types"]:
                if type_info["name"] == query_type["name"]:
                    query_ops_count = len(type_info.get("fields", []))
                    break
        
        # Get mutation operations count
        mutation_type = schema.get("mutationType")
        mutation_ops_count = 0
        if mutation_type:
            for type_info in schema["types"]:
                if type_info["name"] == mutation_type["name"]:
                    mutation_ops_count = len(type_info.get("fields", []))
                    break
        
        result = {
            "schema_summary": {
                "total_custom_types": len(custom_types),
                "type_counts_by_kind": type_counts,
                "query_operations_count": query_ops_count,
                "mutation_operations_count": mutation_ops_count,
                "mutations_allowed": client.allow_mutations
            },
            "sample_types": custom_types[:20],  # Show first 20 types as examples
            "endpoint": client.endpoint
        }
        
        # Only include full SDL if explicitly requested
        if include_full_sdl:
            sdl_schema = client.format_schema_as_sdl(schema_data)
            result["schema_sdl"] = sdl_schema
            result["warning"] = "Full SDL included - this may consume significant context space"
        
        # Apply normalization to prevent context overflow
        if NORMALIZER_AVAILABLE:
            result = normalize_graphql_response(result, "schema_introspection")
        
        return result
    
    return {
        "error": "Invalid schema data structure",
        "endpoint": client.endpoint
    }

@mcp.tool()
async def query_graphql(query: str, variables: Optional[Dict] = None) -> Dict:
    """
    Execute a GraphQL query against the OpenGov FIN GraphQL endpoint.
    
    Args:
        query (str): The GraphQL query string to execute
        variables (Optional[Dict]): Variables to pass to the GraphQL query
    
    Returns:
        Dict: The GraphQL query result including data and any errors
    """
    client = get_client()
    
    # Input validation
    if not query or not query.strip():
        return {"error": "Empty query provided"}
    
    # Check if this is a mutation and if mutations are allowed
    query_stripped = query.strip().lower()
    if query_stripped.startswith("mutation") and not client.allow_mutations:
        return {"error": "Mutations are disabled"}
    
    # Basic syntax validation
    if not any(keyword in query_stripped for keyword in ['query', 'mutation', '{']):
        return {"error": "Invalid GraphQL syntax"}
    
    result = await client.make_graphql_request(query, variables)
    
    # Apply normalization to prevent context overflow
    if NORMALIZER_AVAILABLE:
        result = normalize_graphql_response(result, "query_execution")
    
    return result

@mcp.tool()
async def get_schema_types(limit: int = 50, category: str = None) -> Dict:
    """
    Get a simplified list of available types in the GraphQL schema.
    
    Args:
        limit (int): Maximum number of types to return (default: 50, max: 200)
        category (str): Filter by type category (OBJECT, INPUT_OBJECT, ENUM, etc.)
    
    Returns:
        Dict: Simplified list of types with their kinds and descriptions
    """
    client = get_client()
    schema_data = await client.introspect_schema()
    
    if "error" in schema_data:
        return schema_data
    
    if "data" not in schema_data or "__schema" not in schema_data["data"]:
        return {"error": "Invalid schema data"}
    
    # Validate and constrain limit
    limit = min(max(1, limit), 200)
    
    types_info = []
    for type_info in schema_data["data"]["__schema"]["types"]:
        if type_info["name"].startswith("__"):
            continue  # Skip introspection types
        
        # Filter by category if specified
        if category and type_info["kind"] != category.upper():
            continue
        
        # Truncate description to prevent context overflow
        description = type_info.get("description", "No description available")
        if description and len(description) > 150:
            description = description[:150] + "..."
        
        types_info.append({
            "name": type_info["name"],
            "kind": type_info["kind"],
            "description": description,
            "fields_count": len(type_info.get("fields", [])) if type_info.get("fields") else 0
        })
    
    # Sort by kind then name
    types_info.sort(key=lambda x: (x["kind"], x["name"]))
    
    # Apply limit
    total_available = len(types_info)
    limited_types = types_info[:limit]
    
    result = {
        "types": limited_types,
        "total_types_available": total_available,
        "types_returned": len(limited_types),
        "limit_applied": limit,
        "category_filter": category
    }
    
    # Apply normalization to prevent context overflow
    if NORMALIZER_AVAILABLE:
        result = normalize_graphql_response(result, "schema_types")
    
    return result

@mcp.tool()
async def get_query_operations() -> Dict:
    """
    Get all available query operations from the GraphQL schema.
    
    Returns:
        Dict: List of available query operations with their signatures
    """
    client = get_client()
    schema_data = await client.introspect_schema()
    
    if "error" in schema_data:
        return schema_data
    
    if "data" not in schema_data or "__schema" not in schema_data["data"]:
        return {"error": "Invalid schema data"}
    
    schema = schema_data["data"]["__schema"]
    query_type = schema.get("queryType")
    
    if not query_type:
        return {"error": "No query type found in schema"}
    
    # Find the Query type definition
    query_type_def = None
    for type_info in schema["types"]:
        if type_info["name"] == query_type["name"]:
            query_type_def = type_info
            break
    
    if not query_type_def:
        return {"error": "Query type definition not found"}
    
    operations = []
    for field in query_type_def.get("fields", []):
        operation = {
            "name": field["name"],
            "description": field.get("description"),
            "return_type": client._format_type_ref(field["type"]),
            "arguments": []
        }
        
        for arg in field.get("args", []):
            operation["arguments"].append({
                "name": arg["name"],
                "type": client._format_type_ref(arg["type"]),
                "description": arg.get("description"),
                "default_value": arg.get("defaultValue")
            })
        
        operations.append(operation)
    
    return {
        "query_operations": operations,
        "total_operations": len(operations),
        "endpoint": client.endpoint
    }

@mcp.tool()
async def get_mutation_operations() -> Dict:
    """
    Get all available mutation operations from the GraphQL schema.
    
    Returns:
        Dict: List of available mutation operations with their signatures
    """
    client = get_client()
    schema_data = await client.introspect_schema()
    
    if "error" in schema_data:
        return schema_data
    
    if "data" not in schema_data or "__schema" not in schema_data["data"]:
        return {"error": "Invalid schema data"}
    
    schema = schema_data["data"]["__schema"]
    mutation_type = schema.get("mutationType")
    
    if not mutation_type:
        return {
            "mutation_operations": [],
            "total_operations": 0,
            "message": "No mutation type found in schema",
            "mutations_allowed": client.allow_mutations
        }
    
    # Find the Mutation type definition
    mutation_type_def = None
    for type_info in schema["types"]:
        if type_info["name"] == mutation_type["name"]:
            mutation_type_def = type_info
            break
    
    if not mutation_type_def:
        return {"error": "Mutation type definition not found"}
    
    operations = []
    for field in mutation_type_def.get("fields", []):
        operation = {
            "name": field["name"],
            "description": field.get("description"),
            "return_type": client._format_type_ref(field["type"]),
            "arguments": []
        }
        
        for arg in field.get("args", []):
            operation["arguments"].append({
                "name": arg["name"],
                "type": client._format_type_ref(arg["type"]),
                "description": arg.get("description"),
                "default_value": arg.get("defaultValue")
            })
        
        operations.append(operation)
    
    return {
        "mutation_operations": operations,
        "total_operations": len(operations),
        "mutations_allowed": client.allow_mutations,
        "endpoint": client.endpoint
    }

if __name__ == "__main__":
    mcp.run(transport="stdio") 