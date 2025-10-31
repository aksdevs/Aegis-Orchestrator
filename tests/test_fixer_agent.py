import unittest
from unittest.mock import Mock, patch
import os
from agents.fixer_agent import FixerAgent
from services.git_handler import GitHandler

class TestFixerAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.project_id = "test-project"
        self.location = "us-central1"
        self.fixer_agent = FixerAgent(self.project_id, self.location)
        self.test_workspace = os.path.join(os.path.dirname(__file__), "test_workspace")

    def test_initialization(self):
        """Test that the FixerAgent initializes correctly."""
        self.assertIsNotNone(self.fixer_agent)
        self.assertEqual(self.fixer_agent.project_id, self.project_id)
        self.assertEqual(self.fixer_agent.location, self.location)

    @patch('agents.fixer_agent.aiplatform')
    def test_setup_workspace(self, mock_aiplatform):
        """Test workspace setup functionality."""
        test_repo_url = "https://github.com/test/repo.git"
        
        # Setup mock GitHandler
        mock_git_handler = Mock(spec=GitHandler)
        mock_git_handler.clone_repository.return_value = "/test/path"
        self.fixer_agent.git_handler = mock_git_handler
        
        # Test workspace setup
        self.fixer_agent.setup_workspace(self.test_workspace, test_repo_url)
        
        # Verify GitHandler was called correctly
        mock_git_handler.clone_repository.assert_called_once_with(test_repo_url)
        self.assertEqual(self.fixer_agent.repo_path, "/test/path")

    @patch('agents.fixer_agent.aiplatform')
    def test_fix_vulnerability(self, mock_aiplatform):
        """Test vulnerability fixing functionality."""
        # Setup test data
        test_vulnerability = {
            "id": "VULN-001",
            "title": "SQL Injection",
            "file": "app.py",
            "line": 42,
            "severity": "HIGH"
        }
        
        # Setup mock model and endpoint
        mock_model = Mock()
        mock_endpoint = Mock()
        mock_model.deploy.return_value = mock_endpoint
        mock_aiplatform.Model.list.return_value = [mock_model]
        
        # Setup mock GitHandler
        mock_git_handler = Mock(spec=GitHandler)
        self.fixer_agent.git_handler = mock_git_handler
        
        # Test fix generation
        fix_result = self.fixer_agent.fix_vulnerability(test_vulnerability)
        
        # Verify correct branch creation
        mock_git_handler.create_branch.assert_called_once_with("fix/vuln-VULN-001")
        
        # Verify model deployment and usage
        mock_aiplatform.Model.list.assert_called_once()
        mock_model.deploy.assert_called_once()
        
        # Verify fix was committed
        self.assertTrue(mock_git_handler.commit_changes.called)
        self.assertIsInstance(fix_result, dict)
        self.assertEqual(fix_result["file"], "app.py")

    @patch('agents.fixer_agent.aiplatform')
    def test_create_fix_pr(self, mock_aiplatform):
        """Test pull request creation functionality."""
        # Setup test data
        test_fixes = [
            {
                "file": "app.py",
                "description": "Fixed SQL injection vulnerability"
            },
            {
                "file": "utils.py",
                "description": "Fixed XSS vulnerability"
            }
        ]
        
        # Setup mock GitHandler
        mock_git_handler = Mock(spec=GitHandler)
        mock_git_handler.create_pull_request.return_value = {
            "url": "https://github.com/test/repo/pull/1",
            "number": 1,
            "status": "open"
        }
        self.fixer_agent.git_handler = mock_git_handler
        
        # Test PR creation
        pr_result = self.fixer_agent.create_fix_pr(test_fixes)
        
        # Verify PR creation
        self.assertTrue(mock_git_handler.create_pull_request.called)
        self.assertEqual(pr_result["number"], 1)
        self.assertEqual(pr_result["status"], "open")

if __name__ == '__main__':
    unittest.main()