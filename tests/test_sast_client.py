import unittest
from unittest.mock import Mock, patch, MagicMock
from services.sast_client import SASTClient

class TestSASTClient(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.model_name = "llama3.1"
        self.base_url = "http://localhost:11434"
        with patch('services.sast_client.ChatOllama'):
            self.sast_client = SASTClient(self.model_name, self.base_url)

    def test_initialization(self):
        """Test that the SASTClient initializes correctly."""
        self.assertIsNotNone(self.sast_client)
        self.assertEqual(self.sast_client.model_name, self.model_name)
        self.assertEqual(self.sast_client.base_url, self.base_url)

    def test_scan_code(self):
        """Test code scanning functionality."""
        # Setup test data
        test_repo_path = "/test/repo/path"

        # Setup mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Scan complete"
        self.sast_client.llm = MagicMock()
        self.sast_client.llm.invoke.return_value = mock_response

        # Test code scanning
        scan_id = self.sast_client.scan_code(test_repo_path)

        # Verify scanning process
        self.assertIsInstance(scan_id, str)
        self.sast_client.llm.invoke.assert_called_once()

    def test_get_scan_results(self):
        """Test scan results retrieval."""
        # Test data
        test_scan_id = "scan_123"

        # Get scan results
        results = self.sast_client.get_scan_results(test_scan_id)

        # Verify results
        self.assertIsInstance(results, dict)
        self.assertEqual(results["scan_id"], test_scan_id)
        self.assertIn("vulnerabilities", results)
        self.assertIn("status", results)
        self.assertEqual(results["status"], "completed")

    def test_analyze_vulnerabilities(self):
        """Test vulnerability analysis functionality."""
        # Setup test data
        test_scan_results = {
            "scan_id": "scan_123",
            "vulnerabilities": [
                {
                    "id": "VULN-001",
                    "type": "SQL Injection",
                    "severity": "HIGH"
                }
            ]
        }

        # Setup mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Analysis complete"
        self.sast_client.llm = MagicMock()
        self.sast_client.llm.invoke.return_value = mock_response

        # Test vulnerability analysis
        analysis_results = self.sast_client.analyze_vulnerabilities(test_scan_results)

        # Verify analysis
        self.assertIsInstance(analysis_results, list)
        self.sast_client.llm.invoke.assert_called_once()

    def test_cleanup(self):
        """Test cleanup functionality."""
        # Test cleanup
        self.sast_client.cleanup()
        # No assertions needed as cleanup is a placeholder

if __name__ == '__main__':
    unittest.main()
