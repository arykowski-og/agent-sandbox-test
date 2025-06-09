#!/usr/bin/env python3
"""
JSON Normalizer for GraphQL Responses

This module provides utilities to normalize and truncate large JSON responses
from GraphQL queries to prevent context length overflow while preserving
important information.
"""

import json
from typing import Dict, Any, List, Optional, Union
import pandas as pd

class GraphQLResponseNormalizer:
    """
    Normalizes GraphQL responses using pandas.json_normalize to manage context length
    and improve readability of complex nested structures.
    """
    
    def __init__(self, max_response_size: int = 10000, max_items: int = 100):
        """
        Initialize the normalizer with size limits.
        
        Args:
            max_response_size (int): Maximum character length for responses
            max_items (int): Maximum number of items to include in lists
        """
        self.max_response_size = max_response_size
        self.max_items = max_items
    
    def normalize_response(self, response: Dict[str, Any], context: str = "graphql") -> Dict[str, Any]:
        """
        Normalize a GraphQL response to prevent context overflow.
        
        Args:
            response (Dict): The GraphQL response to normalize
            context (str): Context description for the response
            
        Returns:
            Dict: Normalized response with manageable size
        """
        try:
            # Check if response is already small enough
            response_str = json.dumps(response, default=str)
            if len(response_str) <= self.max_response_size:
                return response
            
            # Handle different types of GraphQL responses
            if "data" in response:
                return self._normalize_data_response(response, context)
            elif "types" in response:
                return self._normalize_types_response(response, context)
            elif "query_operations" in response:
                return self._normalize_operations_response(response, context)
            elif "schema_summary" in response:
                return self._normalize_schema_summary(response, context)
            else:
                return self._generic_normalize(response, context)
                
        except Exception as e:
            # Fallback to simple truncation if normalization fails
            return self._fallback_truncate(response, str(e))
    
    def _normalize_data_response(self, response: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Normalize GraphQL data responses with actual query results."""
        normalized = {
            "context": f"GraphQL {context} response (normalized)",
            "success": True,
            "data_summary": {}
        }
        
        data = response.get("data", {})
        
        # Use pandas.json_normalize to flatten the data structure
        try:
            if isinstance(data, dict) and data:
                # Normalize the data structure
                df = pd.json_normalize(data, max_level=2)
                
                # Limit the number of rows
                if len(df) > self.max_items:
                    df = df.head(self.max_items)
                    normalized["truncation_note"] = f"Showing first {self.max_items} items of {len(pd.json_normalize(data, max_level=2))} total"
                
                # Convert back to dict format but flattened
                normalized["data_summary"] = {
                    "columns": list(df.columns),
                    "row_count": len(df),
                    "sample_data": df.head(10).to_dict('records') if len(df) > 0 else [],
                    "data_types": df.dtypes.astype(str).to_dict() if len(df) > 0 else {}
                }
                
                # Add original keys for reference
                normalized["original_keys"] = list(data.keys())
                
            else:
                normalized["data_summary"] = {"message": "No data or empty response"}
                
        except Exception as e:
            normalized["data_summary"] = {
                "error": f"Failed to normalize data: {str(e)}",
                "raw_keys": list(data.keys()) if isinstance(data, dict) else "Non-dict data"
            }
        
        # Preserve important metadata
        if "errors" in response:
            normalized["errors"] = response["errors"]
        if "query_info" in response:
            normalized["query_info"] = response["query_info"]
            
        return normalized
    
    def _normalize_types_response(self, response: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Normalize GraphQL schema types responses."""
        types = response.get("types", [])
        
        # Use pandas to analyze the types
        if types:
            df = pd.json_normalize(types)
            
            # Group by kind for better organization
            type_summary = {}
            if 'kind' in df.columns:
                type_counts = df['kind'].value_counts().to_dict()
                type_summary = {
                    "total_types": len(df),
                    "types_by_kind": type_counts,
                    "sample_types": df.head(20).to_dict('records')
                }
            else:
                type_summary = {
                    "total_types": len(types),
                    "sample_types": types[:20]
                }
        else:
            type_summary = {"message": "No types found"}
        
        return {
            "context": f"GraphQL types response (normalized)",
            "type_summary": type_summary,
            "pagination_info": {
                "total_available": response.get("total_types_available", len(types)),
                "returned": response.get("types_returned", len(types)),
                "limit_applied": response.get("limit_applied"),
                "category_filter": response.get("category_filter")
            },
            "usage_tip": "Use get_schema_types(limit=X, category='KIND') for specific type exploration"
        }
    
    def _normalize_operations_response(self, response: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Normalize GraphQL operations responses."""
        operations = response.get("query_operations", [])
        
        if operations:
            # Use pandas to analyze operations
            df = pd.json_normalize(operations)
            
            # Limit operations shown
            if len(operations) > self.max_items:
                operations = operations[:self.max_items]
                truncated = True
            else:
                truncated = False
            
            # Create summary
            operations_summary = {
                "total_operations": response.get("total_operations", len(operations)),
                "operations_shown": len(operations),
                "truncated": truncated,
                "operations": [
                    {
                        "name": op.get("name"),
                        "description": (op.get("description", "")[:100] + "...") if op.get("description") and len(op.get("description", "")) > 100 else op.get("description", "No description"),
                        "return_type": op.get("return_type"),
                        "argument_count": len(op.get("arguments", []))
                    }
                    for op in operations
                ]
            }
        else:
            operations_summary = {"message": "No operations found"}
        
        return {
            "context": f"GraphQL operations response (normalized)",
            "operations_summary": operations_summary,
            "usage_tip": "Use query_graphql() with specific operation names to execute queries"
        }
    
    def _normalize_schema_summary(self, response: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Normalize schema summary responses."""
        # Schema summaries are already compact, just ensure they stay manageable
        summary = response.get("schema_summary", {})
        sample_types = response.get("sample_types", [])
        
        # Limit sample types
        if len(sample_types) > 20:
            sample_types = sample_types[:20]
        
        return {
            "context": f"GraphQL schema summary (normalized)",
            "schema_overview": summary,
            "sample_types": sample_types,
            "endpoint": response.get("endpoint"),
            "usage_notes": response.get("usage_notes", {}),
            "performance_optimized": True
        }
    
    def _generic_normalize(self, response: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generic normalization for unknown response types."""
        try:
            # Use pandas.json_normalize for general flattening
            df = pd.json_normalize(response, max_level=1)
            
            return {
                "context": f"Generic response (normalized)",
                "summary": {
                    "original_keys": list(response.keys()),
                    "flattened_columns": list(df.columns) if len(df) > 0 else [],
                    "data_preview": df.head(5).to_dict('records') if len(df) > 0 else {},
                    "size_info": f"Original: ~{len(json.dumps(response, default=str))} chars"
                },
                "truncation_applied": True
            }
        except Exception as e:
            return self._fallback_truncate(response, str(e))
    
    def _fallback_truncate(self, response: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fallback truncation when normalization fails."""
        response_str = json.dumps(response, default=str, indent=2)
        
        if len(response_str) > self.max_response_size:
            truncated = response_str[:self.max_response_size] + "\n... [TRUNCATED]"
        else:
            truncated = response_str
        
        return {
            "context": "Response (fallback truncation)",
            "normalization_error": error,
            "truncated_response": truncated,
            "original_size": len(response_str),
            "truncated_size": len(truncated)
        }

# Global normalizer instance
normalizer = GraphQLResponseNormalizer(max_response_size=8000, max_items=50)

def normalize_graphql_response(response: Dict[str, Any], context: str = "graphql") -> Dict[str, Any]:
    """
    Convenience function to normalize GraphQL responses.
    
    Args:
        response (Dict): The response to normalize
        context (str): Context description
        
    Returns:
        Dict: Normalized response
    """
    return normalizer.normalize_response(response, context) 