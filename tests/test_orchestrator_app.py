import unittest
from unittest.mock import Mock, patch
import os
from agents.orchestrator_app import OrchestratorApp
from agents.workflow import WorkflowState


class TestOrchestratorApp(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock environment variables for configuration
        self.env_patcher = patch.dict(os.environ, {
            'OLLAMA_BASE_URL': 'http://localhost:11434',
            'OLLAMA_MODEL': 'llama3.1',
            'WORKSPACE_DIR': '/test/workspace'
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.env_patcher.stop()

    @patch('agents.orchestrator_app.create_aegis_workflow')
    @patch('config.settings.AegisConfig.validate')
    def test_initialization(self, mock_validate, mock_create_workflow):
        """Test that the OrchestratorApp initializes correctly."""
        # Mock config validation to pass
        mock_validate.return_value = True
        
        # Mock the workflow creation
        mock_workflow = Mock()
        mock_create_workflow.return_value = mock_workflow
        
        orchestrator = OrchestratorApp()
        self.assertIsNotNone(orchestrator)
        
        # Verify workflow was created
        mock_create_workflow.assert_called_once()

    @patch('agents.orchestrator_app.create_aegis_workflow')
    @patch('config.settings.AegisConfig.validate')
    def test_process_repository_no_vulnerabilities(self, mock_validate, mock_create_workflow):
        """Test repository processing when no vulnerabilities are found."""
        # Mock config validation
        mock_validate.return_value = True
        
        # Mock workflow that returns success with no vulnerabilities
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {
            "current_state": WorkflowState.COMPLETE,
            "vulnerabilities": [],
            "reviewed_fixes": [],
            "pull_request_url": None,
            "summary_report": "No vulnerabilities found"
        }
        mock_create_workflow.return_value = mock_workflow

        test_repo_url = "https://github.com/test/repo"
        orchestrator = OrchestratorApp()
        
        result = orchestrator.process_repository(test_repo_url)

        # Verify the workflow was invoked
        mock_workflow.invoke.assert_called_once()
        call_args = mock_workflow.invoke.call_args[0][0]
        self.assertEqual(call_args["repo_url"], test_repo_url)

        # Verify result structure
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["vulnerabilities_found"], 0)

    @patch('agents.orchestrator_app.create_aegis_workflow')
    @patch('config.settings.AegisConfig.validate')
    def test_process_repository_with_vulnerabilities(self, mock_validate, mock_create_workflow):
        """Test repository processing when vulnerabilities are found."""
        # Mock config validation
        mock_validate.return_value = True
        
        # Mock workflow that returns vulnerabilities and fixes
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {
            "current_state": WorkflowState.COMPLETE,
            "vulnerabilities": [
                {"id": "VULN-001", "title": "SQL Injection", "severity": "HIGH"}
            ],
            "reviewed_fixes": [
                {"id": "FIX-001", "vulnerability_id": "VULN-001", "fix_type": "Parameterization"}
            ],
            "pull_request_url": "https://github.com/test/repo/pull/1",
            "summary_report": "Fixed 1 vulnerability"
        }
        mock_create_workflow.return_value = mock_workflow

        test_repo_url = "https://github.com/test/repo"
        orchestrator = OrchestratorApp()
        
        result = orchestrator.process_repository(test_repo_url)

        # Verify the workflow was invoked
        mock_workflow.invoke.assert_called_once()
        call_args = mock_workflow.invoke.call_args[0][0]
        self.assertEqual(call_args["repo_url"], test_repo_url)

        # Verify result structure
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["vulnerabilities_found"], 1)
        self.assertEqual(result["fixes_applied"], 1)
        self.assertIsNotNone(result["pull_request"]["url"])

    @patch('agents.orchestrator_app.create_aegis_workflow')  
    @patch('config.settings.AegisConfig.validate')
    def test_cleanup(self, mock_validate, mock_create_workflow):
        """Test cleanup functionality."""
        mock_validate.return_value = True
        mock_workflow = Mock()
        mock_create_workflow.return_value = mock_workflow
        
        orchestrator = OrchestratorApp()
        
        # Test cleanup - should not raise any exceptions
        orchestrator.cleanup()
        
        # Verify cleanup completed without errors
        self.assertIsNotNone(orchestrator)


if __name__ == "__main__":
    unittest.main()