import unittest
from unittest.mock import Mock, patch
from agents.orchestrator_app import OrchestratorApp
from services.sast_client import SASTClient
from agents.researcher_agent import ResearcherAgent
from agents.fixer_agent import FixerAgent


class TestOrchestratorApp(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "project_id": "test-project",
            "location": "us-central1",
            "workspace_dir": "/test/workspace",
        }

    def test_initialization(self):
        """Test that the OrchestratorApp initializes correctly."""
        orchestrator = OrchestratorApp(self.config)
        self.assertIsNotNone(orchestrator)
        self.assertEqual(orchestrator.project_id, self.config["project_id"])
        self.assertEqual(orchestrator.location, self.config["location"])
        self.assertEqual(orchestrator.workspace_dir, self.config["workspace_dir"])

        # Verify component initialization
        self.assertIsInstance(orchestrator.sast_client, SASTClient)
        self.assertIsInstance(orchestrator.researcher, ResearcherAgent)
        self.assertIsInstance(orchestrator.fixer, FixerAgent)

    @patch("agents.orchestrator_app.SASTClient")
    @patch("agents.orchestrator_app.ResearcherAgent")
    @patch("agents.orchestrator_app.FixerAgent")
    def test_process_repository_no_vulnerabilities(
        self, mock_fixer_class, mock_researcher_class, mock_sast_class
    ):
        """Test repository processing when no vulnerabilities are found."""
        # Setup mock instances
        mock_sast = Mock()
        mock_researcher = Mock()
        mock_fixer = Mock()

        mock_sast_class.return_value = mock_sast
        mock_researcher_class.return_value = mock_researcher
        mock_fixer_class.return_value = mock_fixer

        # Setup mock scan results
        mock_sast.scan_code.return_value = "scan_123"
        mock_sast.get_scan_results.return_value = {"vulnerabilities": [], "status": "completed"}

        # Test repository processing
        test_repo_url = "https://github.com/test/repo.git"
        orchestrator = OrchestratorApp(self.config)
        result = orchestrator.process_repository(test_repo_url)

        # Verify processing
        mock_fixer.setup_workspace.assert_called_once_with(self.config["workspace_dir"], test_repo_url)
        mock_sast.scan_code.assert_called_once()
        mock_sast.get_scan_results.assert_called_once_with("scan_123")

        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["message"], "No vulnerabilities found")

    @patch("agents.orchestrator_app.SASTClient")
    @patch("agents.orchestrator_app.ResearcherAgent")
    @patch("agents.orchestrator_app.FixerAgent")
    def test_process_repository_with_vulnerabilities(
        self, mock_fixer_class, mock_researcher_class, mock_sast_class
    ):
        """Test repository processing when vulnerabilities are found."""
        # Setup mock instances
        mock_sast = Mock()
        mock_researcher = Mock()
        mock_fixer = Mock()

        mock_sast_class.return_value = mock_sast
        mock_researcher_class.return_value = mock_researcher
        mock_fixer_class.return_value = mock_fixer

        # Setup mock scan results
        mock_sast.scan_code.return_value = "scan_123"
        mock_sast.get_scan_results.return_value = {
            "vulnerabilities": [
                {"id": "VULN-001", "title": "SQL Injection", "severity": "HIGH"}
            ],
            "status": "completed",
        }

        # Setup mock research results
        mock_researcher.research_vulnerability.return_value = {"severity": "HIGH", "impact": "Critical"}
        mock_researcher.analyze_fix_approaches.return_value = [{"approach": "parameterization"}]
        mock_researcher.generate_fix_recommendation.return_value = {
            "recommended_approach": {"approach": "parameterization"}
        }

        # Setup mock fix results
        mock_fixer.fix_vulnerability.return_value = {"file": "app.py", "changes": ["parameterized query"]}
        mock_fixer.create_fix_pr.return_value = {"url": "https://github.com/test/repo/pull/1", "number": 1}

        # Test repository processing
        test_repo_url = "https://github.com/test/repo.git"
        orchestrator = OrchestratorApp(self.config)
        result = orchestrator.process_repository(test_repo_url)

        # Verify processing
        mock_fixer.setup_workspace.assert_called_once()
        mock_sast.scan_code.assert_called_once()
        mock_researcher.research_vulnerability.assert_called_once()
        mock_fixer.fix_vulnerability.assert_called_once()
        mock_fixer.create_fix_pr.assert_called_once()

        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["fixes_applied"], 1)
        self.assertIn("pull_request", result)

    def test_cleanup(self):
        """Test cleanup functionality."""
        # Instantiate orchestrator and inject mock components
        orchestrator = OrchestratorApp(self.config)
        orchestrator.sast_client = Mock()
        orchestrator.researcher = Mock()
        orchestrator.fixer = Mock()

        # Test cleanup
        orchestrator.cleanup()

        # Verify all components were cleaned up
        orchestrator.sast_client.cleanup.assert_called_once()
        orchestrator.researcher.cleanup.assert_called_once()
        orchestrator.fixer.cleanup.assert_called_once()


if __name__ == "__main__":
    unittest.main()