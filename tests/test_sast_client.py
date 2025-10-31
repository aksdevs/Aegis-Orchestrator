import unittest
from unittest.mock import Mock, patch
from services.sast_client import SASTClient

class TestSASTClient(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.project_id = "test-project"
        self.location = "us-central1"
        self.sast_client = SASTClient(self.project_id, self.location)

    def test_initialization(self):
        """Test that the SASTClient initializes correctly."""
        self.assertIsNotNone(self.sast_client)
        self.assertEqual(self.sast_client.project_id, self.project_id)
        self.assertEqual(self.sast_client.location, self.location)

    @patch('services.sast_client.aiplatform')
    def test_scan_code(self, mock_aiplatform):
        """Test code scanning functionality."""
        # Setup test data
        test_repo_path = "/test/repo/path"
        
        # Setup mock model and endpoint
        mock_model = Mock()
        mock_endpoint = Mock()
        mock_model.deploy.return_value = mock_endpoint
        mock_aiplatform.Model.list.return_value = [mock_model]
        
        # Test code scanning
        scan_id = self.sast_client.scan_code(test_repo_path)
        
        # Verify scanning process
        self.assertIsInstance(scan_id, str)
        mock_aiplatform.Model.list.assert_called_once()
        mock_model.deploy.assert_called_once()

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

    @patch('services.sast_client.aiplatform')
    def test_analyze_vulnerabilities(self, mock_aiplatform):
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
        
        # Setup mock endpoint
        mock_endpoint = Mock()
        mock_aiplatform.Endpoint.return_value = mock_endpoint
        
        # Test vulnerability analysis
        analysis_results = self.sast_client.analyze_vulnerabilities(test_scan_results)
        
        # Verify analysis
        self.assertIsInstance(analysis_results, list)
        mock_aiplatform.Endpoint.assert_called_once()

    def test_cleanup(self):
        """Test cleanup functionality."""
        # Test cleanup
        self.sast_client.cleanup()
        # No assertions needed as cleanup is a placeholder

if __name__ == '__main__':
    unittest.main()