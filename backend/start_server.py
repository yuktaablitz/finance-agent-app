#!/usr/bin/env python3
"""
Finance Agent API Server Startup Script
Run this to start the development server
"""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("❌ python-dotenv not found. Please install it with: pip install python-dotenv")
    sys.exit(1)

def main():
    """Start the Finance Agent API server."""
    
    # Check for required environment variables
    required_vars = ["GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set up your .env file with the required variables.")
        print("Copy .env.example to .env and fill in your values.")
        sys.exit(1)
    
    print("🚀 Starting Finance Agent API...")
    print(f"📊 Gemini Model: {os.getenv('GEMINI_MODEL', 'models/gemini-3-flash-preview')}")
    print(f"⚡ Rate Limit: {os.getenv('GEMINI_RATE_LIMIT', '60')} requests/minute")
    print(f"💾 Cache TTL: {os.getenv('GEMINI_CACHE_TTL', '300')} seconds")
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    
    # Import uvicorn here to avoid import issues
    try:
        import uvicorn
    except ImportError:
        print("❌ uvicorn not found. Please install it with: pip install uvicorn")
        sys.exit(1)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
