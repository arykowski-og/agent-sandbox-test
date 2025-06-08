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
async def introspect_schema() -> Dict:
    """
    Introspect the OpenGov FIN GraphQL schema to discover available types, queries, and mutations.
    
    This tool retrieves the complete GraphQL schema definition, including:
    - Available query operations
    - Available mutation operations (if any)
    - All custom types and their fields
    - Input types for mutations
    - Enums and scalars
    
    Use this tool first to understand what data and operations are available
    before executing specific GraphQL queries.
    
    Returns:
        Dict: The complete GraphQL schema introspection result
    """
    client = get_client()
    schema_data = await client.introspect_schema()
    
    if "error" in schema_data:
        return schema_data
    
    # Also provide a formatted SDL version for better readability
    sdl_schema = client.format_schema_as_sdl(schema_data)
    
    return {
        "introspection_result": schema_data,
        "schema_sdl": sdl_schema,
        "endpoint": client.endpoint,
        "mutations_allowed": client.allow_mutations
    }

@mcp.tool()
async def query_graphql(query: str, variables: Optional[Dict] = None) -> Dict:
    """
    Execute a GraphQL query against the OpenGov FIN GraphQL endpoint.
    
    This tool allows you to run GraphQL queries to fetch financial data from OpenGov.
    You can query for budgets, expenditures, revenues, accounts, and other financial information.
    
    Args:
        query (str): The GraphQL query string to execute
        variables (Optional[Dict]): Variables to pass to the GraphQL query
    
    Returns:
        Dict: The GraphQL query result including data and any errors
    
    Examples:
        # Simple query to get basic information
        query_graphql("{ __typename }")
        
        # Query with variables
        query_graphql(
            "query GetBudget($year: Int!) { budget(year: $year) { total amount } }",
            {"year": 2024}
        )
    
    Note: Mutations are disabled by default for security. Set OG_FIN_ALLOW_MUTATIONS=true
    to enable mutation operations.
    """
    client = get_client()
    
    # Enhanced input validation
    if not query or not query.strip():
        return {
            "error": "Empty query provided",
            "message": "GraphQL query cannot be empty. Please provide a valid GraphQL query string.",
            "troubleshooting": {
                "issue": "No query provided",
                "solution": "Provide a valid GraphQL query",
                "example": "{ __typename }",
                "next_steps": [
                    "Use introspect_schema() to discover available queries",
                    "Use get_query_operations() to see available operations",
                    "Start with a simple query like '{ __typename }'"
                ]
            }
        }
    
    # Check if this is a mutation and if mutations are allowed
    query_stripped = query.strip().lower()
    if query_stripped.startswith("mutation") and not client.allow_mutations:
        return {
            "error": "Mutations are disabled",
            "message": "Mutation operations are disabled by default for security. Set OG_FIN_ALLOW_MUTATIONS=true to enable mutations.",
            "query": query,
            "troubleshooting": {
                "issue": "Mutations not allowed",
                "solution": "Use query operations instead of mutations",
                "alternative_approaches": [
                    "Use query operations to read financial data",
                    "Contact administrator to enable mutations if needed",
                    "Use get_query_operations() to see available read operations"
                ],
                "prevention": "Check if operation is a query before executing"
            }
        }
    
    # Basic syntax validation
    if not any(keyword in query_stripped for keyword in ['query', 'mutation', '{']):
        return {
            "error": "Invalid GraphQL syntax",
            "message": "The provided string does not appear to be a valid GraphQL query.",
            "query": query,
            "troubleshooting": {
                "issue": "Invalid GraphQL syntax",
                "solution": "Ensure query follows GraphQL syntax rules",
                "corrected_examples": [
                    "{ __typename }",
                    "query { __typename }",
                    "query GetData { fieldName }"
                ],
                "common_mistakes": [
                    "Missing curly braces { }",
                    "Missing 'query' keyword for named queries",
                    "Incorrect field names or structure"
                ],
                "next_steps": [
                    "Use introspect_schema() to see valid field names",
                    "Start with simple queries and build complexity gradually",
                    "Validate syntax against GraphQL specification"
                ]
            }
        }
    
    result = await client.make_graphql_request(query, variables)
    
    # Enhanced error processing
    if "error" in result:
        # Add troubleshooting information to errors
        enhanced_result = result.copy()
        error_msg = result.get("error", "").lower()
        
        # Provide specific troubleshooting based on error type
        troubleshooting = {
            "issue": result.get("error", "Unknown error"),
            "query_attempted": query,
            "variables_used": variables
        }
        
        if "authentication" in error_msg or "unauthorized" in error_msg:
            troubleshooting.update({
                "likely_cause": "Authentication or authorization issue",
                "solutions": [
                    "Verify OG_FIN_BEARER_TOKEN is correctly set",
                    "Check if token has expired",
                    "Ensure token has proper permissions for this operation"
                ],
                "prevention": "Regularly refresh authentication tokens"
            })
        elif "field" in error_msg and "exist" in error_msg:
            troubleshooting.update({
                "likely_cause": "Querying non-existent field or type",
                "solutions": [
                    "Use introspect_schema() to see available fields",
                    "Check field spelling and capitalization",
                    "Verify the field exists on the queried type"
                ],
                "prevention": "Always validate field names against schema before querying"
            })
        elif "syntax" in error_msg or "parse" in error_msg:
            troubleshooting.update({
                "likely_cause": "GraphQL syntax error",
                "solutions": [
                    "Check for missing or extra braces, parentheses, or quotes",
                    "Validate query structure against GraphQL syntax",
                    "Use a GraphQL validator or IDE for syntax checking"
                ],
                "prevention": "Use proper GraphQL syntax and validate before executing"
            })
        elif "timeout" in error_msg or "network" in error_msg:
            troubleshooting.update({
                "likely_cause": "Network connectivity or timeout issue",
                "solutions": [
                    "Check internet connectivity",
                    "Verify OpenGov FIN endpoint is accessible",
                    "Try a simpler query to test connectivity",
                    "Contact system administrator if issue persists"
                ],
                "prevention": "Monitor network connectivity and endpoint availability"
            })
        else:
            troubleshooting.update({
                "likely_cause": "Unknown error - see error message for details",
                "solutions": [
                    "Review the specific error message",
                    "Try a simpler query to isolate the issue",
                    "Use introspect_schema() to verify available operations",
                    "Contact support if error persists"
                ],
                "prevention": "Test queries incrementally and validate against schema"
            })
        
        enhanced_result["troubleshooting"] = troubleshooting
        return enhanced_result
    
    # Add success metadata for better user understanding
    if "data" in result:
        result["query_info"] = {
            "query_executed": query,
            "variables_used": variables,
            "success": True,
            "data_returned": bool(result["data"]),
            "next_steps": [
                "Analyze the returned data",
                "Use the data for financial analysis",
                "Execute additional queries if needed",
                "Consider saving results for reporting"
            ]
        }
    
    return result

@mcp.tool()
async def get_schema_types() -> Dict:
    """
    Get a simplified list of all available types in the GraphQL schema.
    
    This is a convenience tool that provides a quick overview of available types
    without the full introspection details. Useful for getting a high-level view
    of what data structures are available.
    
    Returns:
        Dict: Simplified list of types with their kinds and descriptions
    """
    client = get_client()
    schema_data = await client.introspect_schema()
    
    if "error" in schema_data:
        return schema_data
    
    if "data" not in schema_data or "__schema" not in schema_data["data"]:
        return {"error": "Invalid schema data"}
    
    types_info = []
    for type_info in schema_data["data"]["__schema"]["types"]:
        if type_info["name"].startswith("__"):
            continue  # Skip introspection types
        
        types_info.append({
            "name": type_info["name"],
            "kind": type_info["kind"],
            "description": type_info.get("description"),
            "fields_count": len(type_info.get("fields", [])) if type_info.get("fields") else 0
        })
    
    # Sort by kind then name
    types_info.sort(key=lambda x: (x["kind"], x["name"]))
    
    return {
        "types": types_info,
        "total_types": len(types_info),
        "endpoint": client.endpoint
    }

@mcp.tool()
async def get_query_operations() -> Dict:
    """
    Get all available query operations from the GraphQL schema.
    
    This tool extracts and lists all the query operations available in the schema,
    including their arguments and return types. This is helpful for understanding
    what data you can fetch from the API.
    
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
    
    This tool extracts and lists all the mutation operations available in the schema,
    including their arguments and return types. Note that mutations are disabled
    by default for security.
    
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