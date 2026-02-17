import unittest
from unittest.mock import Mock, patch, MagicMock
from agents.researcher_agent import ResearcherAgent

class TestResearcherAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.model_name = "llama3.1"
        self.base_url = "http://localhost:11434"
        with patch('agents.researcher_agent.ChatOllama'):
            self.researcher_agent = ResearcherAgent(self.model_name, self.base_url)

    def test_initialization(self):
        """Test that the ResearcherAgent initializes correctly."""
        self.assertIsNotNone(self.researcher_agent)
        self.assertEqual(self.researcher_agent.model_name, self.model_name)
        self.assertEqual(self.researcher_agent.base_url, self.base_url)

    def test_research_vulnerability(self):
        """Test vulnerability research functionality."""
        # Setup test data
        test_vulnerability = {
            "id": "VULN-001",
            "type": "SQL Injection",
            "cve": "CVE-2025-1234",
            "severity": "HIGH"
        }

        # Setup mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Detailed vulnerability analysis..."
        self.researcher_agent.llm = MagicMock()
        self.researcher_agent.llm.invoke.return_value = mock_response

        # Test vulnerability research
        findings = self.researcher_agent.research_vulnerability(test_vulnerability)

        # Verify LLM was invoked
        self.researcher_agent.llm.invoke.assert_called_once()

        # Verify research findings
        self.assertIsInstance(findings, dict)
        self.assertEqual(findings["vulnerability_id"], test_vulnerability["id"])
        self.assertIn("severity", findings)
        self.assertIn("impact", findings)
        self.assertIn("remediation_approaches", findings)

    def test_analyze_fix_approaches(self):
        """Test fix approaches analysis functionality."""
        # Setup test data
        test_findings = {
            "vulnerability_id": "VULN-001",
            "severity": "HIGH",
            "impact": "Critical data exposure",
            "affected_components": ["database", "api"]
        }

        # Setup mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Fix approach analysis..."
        self.researcher_agent.llm = MagicMock()
        self.researcher_agent.llm.invoke.return_value = mock_response

        # Test fix analysis
        approaches = self.researcher_agent.analyze_fix_approaches(test_findings)

        # Verify LLM was invoked
        self.researcher_agent.llm.invoke.assert_called_once()

        # Verify analysis results
        self.assertIsInstance(approaches, list)
        self.assertTrue(len(approaches) > 0)
        for approach in approaches:
            self.assertIn("approach", approach)
            self.assertIn("complexity", approach)
            self.assertIn("risk_level", approach)

    def test_generate_fix_recommendation(self):
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

        # Setup mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Recommendation details..."
        self.researcher_agent.llm = MagicMock()
        self.researcher_agent.llm.invoke.return_value = mock_response

        # Test recommendation generation
        recommendation = self.researcher_agent.generate_fix_recommendation(
            test_findings, test_approaches
        )

        # Verify LLM was invoked
        self.researcher_agent.llm.invoke.assert_called_once()

        # Verify recommendation
        self.assertIsInstance(recommendation, dict)
        self.assertIn("recommended_approach", recommendation)
        self.assertIn("justification", recommendation)
        self.assertIn("implementation_steps", recommendation)

if __name__ == '__main__':
    unittest.main()
