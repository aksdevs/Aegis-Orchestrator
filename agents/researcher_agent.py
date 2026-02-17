"""Agent responsible for researching vulnerabilities and their solutions."""
from typing import Dict, List
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

class ResearcherAgent:
    """Agent that researches security vulnerabilities and potential fixes."""

    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"):
        """Initialize the Researcher Agent.

        Args:
            model_name: The Ollama model to use for research
            base_url: The Ollama server base URL
        """
        self.model_name = model_name
        self.base_url = base_url

        # Initialize ChatOllama
        self.llm = ChatOllama(model=model_name, base_url=base_url)

    def research_vulnerability(self, vulnerability_details: Dict) -> Dict:
        """Research a vulnerability to understand its impact and potential fixes.

        Args:
            vulnerability_details: Dictionary containing vulnerability information

        Returns:
            Dictionary containing research findings
        """
        messages = [
            SystemMessage(content="You are an expert cybersecurity researcher."),
            HumanMessage(content=(
                f"Research this vulnerability and provide findings:\n"
                f"ID: {vulnerability_details['id']}\n"
                f"Type: {vulnerability_details.get('type', 'Unknown')}\n"
                f"Severity: {vulnerability_details.get('severity', 'Unknown')}\n\n"
                f"Provide: severity assessment, impact analysis, remediation approaches, and references."
            ))
        ]

        response = self.llm.invoke(messages)

        findings = {
            "vulnerability_id": vulnerability_details["id"],
            "severity": vulnerability_details.get("severity", "HIGH"),
            "impact": "Potential remote code execution",
            "remediation_approaches": [],
            "references": [],
            "llm_analysis": response.content
        }

        return findings

    def analyze_fix_approaches(self, findings: Dict) -> List[Dict]:
        """Analyze different approaches to fix the vulnerability.

        Args:
            findings: Dictionary containing research findings

        Returns:
            List of possible fix approaches
        """
        messages = [
            SystemMessage(content="You are an expert cybersecurity researcher specializing in vulnerability remediation."),
            HumanMessage(content=(
                f"Analyze fix approaches for vulnerability: {findings['vulnerability_id']}\n"
                f"Severity: {findings['severity']}\n"
                f"Impact: {findings['impact']}\n\n"
                f"Provide a list of fix approaches with complexity and risk levels."
            ))
        ]

        response = self.llm.invoke(messages)

        approaches = [
            {
                "approach": "patch",
                "complexity": "medium",
                "risk_level": "low",
                "estimated_time": "2 hours",
                "llm_details": response.content
            }
        ]

        return approaches

    def generate_fix_recommendation(self, findings: Dict, approaches: List[Dict]) -> Dict:
        """Generate a final recommendation for fixing the vulnerability.

        Args:
            findings: Research findings about the vulnerability
            approaches: List of possible fix approaches

        Returns:
            Dictionary containing the recommended fix approach
        """
        approaches_text = "\n".join(
            f"- {a['approach']} (complexity: {a['complexity']}, risk: {a['risk_level']})"
            for a in approaches
        )

        messages = [
            SystemMessage(content="You are an expert cybersecurity advisor."),
            HumanMessage(content=(
                f"Recommend the best fix approach for vulnerability: {findings['vulnerability_id']}\n"
                f"Severity: {findings['severity']}\n"
                f"Available approaches:\n{approaches_text}\n\n"
                f"Provide a recommendation with justification and implementation steps."
            ))
        ]

        response = self.llm.invoke(messages)

        recommendation = {
            "recommended_approach": approaches[0],
            "justification": "This approach provides the best balance of security and implementation complexity",
            "implementation_steps": [],
            "llm_recommendation": response.content
        }

        return recommendation

    def cleanup(self) -> None:
        """Clean up resources."""
        pass
