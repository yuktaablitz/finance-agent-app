"""
Response Formatting Utilities
Handles JSON response formatting for the Finance Agent API
"""

import json
from typing import Any, Dict
from fastapi import Response
from fastapi.responses import JSONResponse


def format_json_response(data: Dict[str, Any], status_code: int = 200) -> JSONResponse:
    """
    Format response data as pretty JSON with proper headers.
    
    Args:
        data: Dictionary containing response data
        status_code: HTTP status code (default: 200)
    
    Returns:
        JSONResponse with formatted content and proper headers
    """
    return JSONResponse(
        content=data,
        status_code=status_code,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


def format_error_response(message: str, status_code: int = 400, error_code: str = None) -> JSONResponse:
    """
    Format error response with consistent structure.
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        error_code: Optional error code for client reference
    
    Returns:
        JSONResponse with error structure
    """
    error_data = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    
    if error_code:
        error_data["error_code"] = error_code
    
    return format_json_response(error_data, status_code)


def format_success_response(data: Any, message: str = None) -> JSONResponse:
    """
    Format success response with consistent structure.
    
    Args:
        data: Response data
        message: Optional success message
    
    Returns:
        JSONResponse with success structure
    """
    response_data = {
        "success": True,
        "data": data
    }
    
    if message:
        response_data["message"] = message
    
    return format_json_response(response_data)


def pretty_print_json(data: Dict[str, Any]) -> str:
    """
    Return pretty-printed JSON string for logging/debugging.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Pretty-formatted JSON string
    """
    return json.dumps(data, indent=2, ensure_ascii=False)