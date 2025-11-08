"""Test the simplified LangGraph workflow."""
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.simplified_workflow import create_simplified_workflow, WorkflowState

def test_simplified_workflow():
    """Test the simplified workflow execution."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Testing Simplified LangGraph Workflow")
        print("=" * 60)
        
        # Create workflow
        workflow = create_simplified_workflow()
        logger.info("✓ Workflow created successfully")
        
        # Define initial state
        initial_state = {
            "repository_url": "https://github.com/test/vulnerable-repo",
            "vulnerabilities": [],
            "fixes": [],
            "analysis_results": {},
            "current_state": WorkflowState.SCAN_VULNERABILITIES.value,
            "pull_request_url": None,
            "error_message": None
        }
        
        logger.info("🔄 Executing workflow...")
        
        # Execute workflow
        result = workflow.invoke(initial_state)
        
        # Print results
        print("\n✅ Workflow execution completed!")
        print("=" * 40)
        
        vulnerabilities = result.get("vulnerabilities", [])
        fixes = result.get("fixes", [])
        
        print(f"🔍 Vulnerabilities found: {len(vulnerabilities)}")
        for i, vuln in enumerate(vulnerabilities, 1):
            print(f"  {i}. {vuln['title']} ({vuln['severity']}) in {vuln['file_path']}")
        
        print(f"🛠️ Fixes generated: {len(fixes)}")
        for i, fix in enumerate(fixes, 1):
            status = fix.get('review_status', 'pending')
            print(f"  {i}. {fix['fix_type']} - Status: {status}")
        
        if result.get("pull_request_url"):
            print(f"🔗 Pull request created: {result['pull_request_url']}")
            
        analysis_results = result.get("analysis_results", {})
        if analysis_results:
            print(f"📊 Analysis results:")
            for key, value in analysis_results.items():
                print(f"  • {key}: {value}")
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_simplified_workflow()
    sys.exit(0 if success else 1)