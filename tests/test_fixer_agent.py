import unittest
from unittest.mock import Mock, patch, MagicMock
import os
from agents.fixer_agent import FixerAgent
from services.git_handler import GitHandler

class TestFixerAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.model_name = "llama3.1"
        self.base_url = "http://localhost:11434"
        with patch('agents.fixer_agent.ChatOllama'):
            self.fixer_agent = FixerAgent(self.model_name, self.base_url)
        self.test_workspace = os.path.join(os.path.dirname(__file__), "test_workspace")

    def test_initialization(self):
        """Test that the FixerAgent initializes correctly."""
        self.assertIsNotNone(self.fixer_agent)
        self.assertEqual(self.fixer_agent.model_name, self.model_name)
        self.assertEqual(self.fixer_agent.base_url, self.base_url)

    def test_setup_workspace(self):
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

    def test_fix_vulnerability(self):
        """Test vulnerability fixing functionality."""
        # Setup test data
        test_vulnerability = {
            "id": "VULN-001",
            "title": "SQL Injection",
            "file": "app.py",
            "line": 42,
            "severity": "HIGH"
        }

        # Setup mock LLM response
        mock_response = MagicMock()
        mock_response.content = '{"file": "app.py", "changes": [], "description": "Fix generated"}'
        self.fixer_agent.llm = MagicMock()
        self.fixer_agent.llm.invoke.return_value = mock_response

        # Setup mock GitHandler
        mock_git_handler = Mock(spec=GitHandler)
        self.fixer_agent.git_handler = mock_git_handler

        # Test fix generation
        fix_result = self.fixer_agent.fix_vulnerability(test_vulnerability)

        # Verify correct branch creation
        mock_git_handler.create_branch.assert_called_once_with("fix/vuln-VULN-001")

        # Verify LLM was invoked
        self.fixer_agent.llm.invoke.assert_called_once()

        # Verify fix was committed
        self.assertTrue(mock_git_handler.commit_changes.called)
        self.assertIsInstance(fix_result, dict)
        self.assertEqual(fix_result["file"], "app.py")

    def test_create_fix_pr(self):
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
