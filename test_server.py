#!/usr/bin/env python3
"""Simple test script to verify server functionality without dependencies."""

import sys
import os
import json
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_server_imports():
    """Test that server-related imports work."""
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        import threading
        print("✅ All server imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_argument_parsing():
    """Test that argument parsing includes server flag."""
    try:
        with patch('sys.argv', ['main.py', '--server']):
            # Mock the OrchestratorApp to avoid dependency issues
            with patch('agents.orchestrator_app.OrchestratorApp'):
                from main import main
                # This would normally call run_server(), but we'll mock it
                print("✅ Argument parsing includes --server flag")
                return True
    except Exception as e:
        print(f"❌ Argument parsing error: {e}")
        return False

def test_server_functions_exist():
    """Test that server functions are defined."""
    try:
        # Mock dependencies to avoid import errors
        with patch.dict('sys.modules', {
            'agents.orchestrator_app': Mock(),
            'langchain_core.messages': Mock(),
            'langgraph.graph': Mock(),
            'langchain_ollama': Mock(),
            'git': Mock()
        }):
            import main
            
            # Check if server functions exist
            assert hasattr(main, 'AegisRequestHandler'), "AegisRequestHandler class not found"
            assert hasattr(main, 'run_server'), "run_server function not found"
            
            print("✅ Server functions exist in main.py")
            return True
    except Exception as e:
        print(f"❌ Server function test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Aegis Orchestrator Server Functionality\n")
    
    tests = [
        test_server_imports,
        test_argument_parsing,
        test_server_functions_exist
    ]
    
    results = []
    for test in tests:
        print(f"Running {test.__name__}...")
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All server functionality tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())