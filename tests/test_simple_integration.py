"""Simple integration tests for the LangGraph workflow system."""
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.simplified_workflow import create_simplified_workflow, WorkflowState


class TestSimplifiedWorkflow(unittest.TestCase):
    """Test cases for simplified LangGraph workflow integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow = create_simplified_workflow()
        self.test_repo_url = "https://github.com/test/vulnerable-repo"
        
        self.initial_state = {
            "repository_url": self.test_repo_url,
            "vulnerabilities": [],
            "fixes": [],
            "analysis_results": {},
            "current_state": WorkflowState.SCAN_VULNERABILITIES.value,
            "pull_request_url": None,
            "error_message": None
        }
        
    def test_workflow_creation(self):
        """Test that workflow is created successfully."""
        self.assertIsNotNone(self.workflow)
        
    def test_initial_state_structure(self):
        """Test that initial state has correct structure."""
        required_keys = [
            "repository_url", "vulnerabilities", "fixes", 
            "analysis_results", "current_state", 
            "pull_request_url", "error_message"
        ]
        
        for key in required_keys:
            self.assertIn(key, self.initial_state)
            
    def test_workflow_state_enum(self):
        """Test WorkflowState enum values."""
        expected_states = [
            "INITIALIZE", "SCAN_VULNERABILITIES", "RESEARCH_VULNERABILITIES",
            "GENERATE_FIXES", "REVIEW_FIXES", "CREATE_PR", "COMPLETE", "ERROR"
        ]
        
        workflow_states = [state.name for state in WorkflowState]
        
        for state in expected_states:
            self.assertIn(state, workflow_states)
            
    def test_workflow_execution(self):
        """Test workflow execution."""
        result = self.workflow.invoke(self.initial_state)
        
        # Check that workflow produced results
        self.assertIsNotNone(result)
        self.assertIn("vulnerabilities", result)
        self.assertIn("fixes", result)
        
        # Should have found vulnerabilities
        self.assertGreater(len(result["vulnerabilities"]), 0)
        
        # Should have generated fixes
        self.assertGreater(len(result["fixes"]), 0)
        
        # Should have created PR
        self.assertIsNotNone(result.get("pull_request_url"))


def run_simple_integration_tests():
    """Run simplified integration tests."""
    print("🧪 Running Simplified LangGraph Integration Tests")
    print("=" * 60)
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimplifiedWorkflow)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"💥 Tests errored: {len(result.errors)}")
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_simple_integration_tests()
    sys.exit(0 if success else 1)