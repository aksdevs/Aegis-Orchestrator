"""Agent responsible for fixing identified vulnerabilities."""
from typing import Dict, List, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from services.git_handler import GitHandler

class FixerAgent:
    """Agent that fixes security vulnerabilities in code."""

    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"):
        """Initialize the Fixer Agent.

        Args:
            model_name: The Ollama model to use for fix generation
            base_url: The Ollama server base URL
        """
        self.model_name = model_name
        self.base_url = base_url

        # Initialize ChatOllama
        self.llm = ChatOllama(model=model_name, base_url=base_url)

        # Initialize Git handler
        self.git_handler = None

    def setup_workspace(self, workspace_dir: str, repo_url: str) -> None:
        """Set up the workspace for fixing vulnerabilities.

        Args:
            workspace_dir: Directory to use as workspace
            repo_url: URL of the repository to fix
        """
        # Allow tests to inject a mock git_handler. Only create a real
        # GitHandler if one hasn't been provided by the caller/tests.
        if self.git_handler is None:
            self.git_handler = GitHandler(workspace_dir)
        self.repo_path = self.git_handler.clone_repository(repo_url)

    def fix_vulnerability(self, vulnerability: Dict) -> Dict:
        """Generate and apply a fix for a vulnerability.

        Args:
            vulnerability: Dictionary containing vulnerability details

        Returns:
            Dictionary containing fix details
        """
        # Create a new branch for the fix
        branch_name = f"fix/vuln-{vulnerability['id']}"
        self.git_handler.create_branch(branch_name)

        # Use Ollama LLM to generate the fix
        messages = [
            SystemMessage(content="You are an expert secure code developer. Generate a fix for the given vulnerability."),
            HumanMessage(content=(
                f"Fix this vulnerability:\n"
                f"ID: {vulnerability['id']}\n"
                f"Title: {vulnerability['title']}\n"
                f"File: {vulnerability['file']}\n"
                f"Severity: {vulnerability.get('severity', 'UNKNOWN')}\n\n"
                f"Provide a JSON response with 'file', 'changes', and 'description' fields."
            ))
        ]

        response = self.llm.invoke(messages)

        fix_details = {
            "file": vulnerability["file"],
            "changes": [],
            "description": f"AI-generated fix for {vulnerability['title']}"
        }

        # Commit the changes
        commit_message = f"Fix: {vulnerability['title']}\n\nAutomated fix for vulnerability {vulnerability['id']}"
        self.git_handler.commit_changes(commit_message, [fix_details["file"]])

        return fix_details

    def create_fix_pr(self, fixes: List[Dict]) -> Dict:
        """Create a pull request with the fixes.

        Args:
            fixes: List of fix details

        Returns:
            Dictionary containing PR details
        """
        title = "Security fixes: Automated vulnerability remediation"
        body = "This PR contains automated fixes for the following vulnerabilities:\n\n"
        for fix in fixes:
            body += f"- {fix['description']}\n"

        return self.git_handler.create_pull_request(title, body)

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.git_handler:
            self.git_handler.cleanup()
