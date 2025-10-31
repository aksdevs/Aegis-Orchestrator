import unittest
from unittest.mock import Mock, patch
from agents.researcher_agent import ResearcherAgent

class TestResearcherAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.project_id = "test-project"
        self.location = "us-central1"
        self.researcher_agent = ResearcherAgent(self.project_id, self.location)

    def test_initialization(self):
        """Test that the ResearcherAgent initializes correctly."""
        self.assertIsNotNone(self.researcher_agent)
        self.assertEqual(self.researcher_agent.project_id, self.project_id)
        self.assertEqual(self.researcher_agent.location, self.location)

    @patch('agents.researcher_agent.aiplatform')
    def test_research_vulnerability(self, mock_aiplatform):
        """Test vulnerability research functionality."""
        # Setup test data
        test_vulnerability = {
            "id": "VULN-001",
            "type": "SQL Injection",
            "cve": "CVE-2025-1234",
            "severity": "HIGH"
        }
        
        # Setup mock model and endpoint
        mock_model = Mock()
        mock_endpoint = Mock()
        mock_model.deploy.return_value = mock_endpoint
        mock_aiplatform.Model.list.return_value = [mock_model]
        
        # Test vulnerability research
        findings = self.researcher_agent.research_vulnerability(test_vulnerability)
        
        # Verify correct model usage
        mock_aiplatform.Model.list.assert_called_once()
        mock_model.deploy.assert_called_once()
        
        # Verify research findings
        self.assertIsInstance(findings, dict)
        self.assertEqual(findings["vulnerability_id"], test_vulnerability["id"])
        self.assertIn("severity", findings)
        self.assertIn("impact", findings)
        self.assertIn("remediation_approaches", findings)

    @patch('agents.researcher_agent.aiplatform')
    def test_analyze_fix_approaches(self, mock_aiplatform):
        """Test fix approaches analysis functionality."""
        # Setup test data
        test_findings = {
            "vulnerability_id": "VULN-001",
            "severity": "HIGH",
            "impact": "Critical data exposure",
            "affected_components": ["database", "api"]
        }
        
        # Setup mock model and endpoint
        mock_model = Mock()
        mock_endpoint = Mock()
        mock_model.deploy.return_value = mock_endpoint
        mock_aiplatform.Model.list.return_value = [mock_model]
        
        # Test fix analysis
        approaches = self.researcher_agent.analyze_fix_approaches(test_findings)
        
        # Verify model usage
        mock_aiplatform.Model.list.assert_called_once()
        mock_model.deploy.assert_called_once()
        
        # Verify analysis results
        self.assertIsInstance(approaches, list)
        self.assertTrue(len(approaches) > 0)
        for approach in approaches:
            self.assertIn("approach", approach)
            self.assertIn("complexity", approach)
            self.assertIn("risk_level", approach)

    @patch('agents.researcher_agent.aiplatform')
    def test_generate_fix_recommendation(self, mock_aiplatform):
        """Test fix recommendation generation."""
        # Setup test data
        test_findings = {
            "vulnerability_id": "VULN-001",
            "severity": "HIGH",
            "impact": "Critical data exposure"
        }
        test_approaches = [
            {
                "approach": "input_validation",
                "complexity": "low",
                "risk_level": "low"
            },
            {
                "approach": "parameterization",
                "complexity": "medium",
                "risk_level": "low"
            }
        ]
        
        # Setup mock model and endpoint
        mock_model = Mock()
        mock_endpoint = Mock()
        mock_model.deploy.return_value = mock_endpoint
        mock_aiplatform.Model.list.return_value = [mock_model]
        
        # Test recommendation generation
        recommendation = self.researcher_agent.generate_fix_recommendation(
            test_findings, test_approaches
        )
        
        # Verify model usage
        mock_aiplatform.Model.list.assert_called_once()
        mock_model.deploy.assert_called_once()
        
        # Verify recommendation
        self.assertIsInstance(recommendation, dict)
        self.assertIn("recommended_approach", recommendation)
        self.assertIn("justification", recommendation)
        self.assertIn("implementation_steps", recommendation)

if __name__ == '__main__':
    unittest.main()