"""Main orchestrator application that coordinates the security automation workflow."""
import os
from typing import Dict, List
from services.sast_client import SASTClient
from services.git_handler import GitHandler
from agents.fixer_agent import FixerAgent
from agents.researcher_agent import ResearcherAgent

class OrchestratorApp:
    """Main application that orchestrates the security automation workflow."""

    def __init__(self, config: Dict):
        """Initialize the Orchestrator.
        
        Args:
            config: Configuration dictionary containing:
                - project_id: GCP project ID
                - location: GCP region
                - workspace_dir: Directory for workspace
        """
        self.config = config
        self.project_id = config["project_id"]
        self.location = config.get("location", "us-central1")
        self.workspace_dir = config["workspace_dir"]
        
        # Initialize components
        self.sast_client = SASTClient(self.project_id, self.location)
        self.researcher = ResearcherAgent(self.project_id, self.location)
        self.fixer = FixerAgent(self.project_id, self.location)

    def process_repository(self, repo_url: str) -> Dict:
        """Process a repository for vulnerabilities and fixes.
        
        Args:
            repo_url: URL of the repository to process
            
        Returns:
            Dictionary containing processing results
        """
        # Set up the workspace
        self.fixer.setup_workspace(self.workspace_dir, repo_url)
        
        # Scan for vulnerabilities
        scan_id = self.sast_client.scan_code(self.workspace_dir)
        scan_results = self.sast_client.get_scan_results(scan_id)
        
        # Process each vulnerability
        fixes = []
        for vuln in scan_results.get("vulnerabilities", []):
            # Research the vulnerability
            research_findings = self.researcher.research_vulnerability(vuln)
            fix_approaches = self.researcher.analyze_fix_approaches(research_findings)
            recommendation = self.researcher.generate_fix_recommendation(
                research_findings, fix_approaches
            )
            
            # Generate and apply fix
            fix_result = self.fixer.fix_vulnerability({
                **vuln,
                "recommendation": recommendation
            })
            fixes.append(fix_result)
        
        # Create pull request with all fixes
        if fixes:
            pr_details = self.fixer.create_fix_pr(fixes)
            return {
                "status": "success",
                "fixes_applied": len(fixes),
                "pull_request": pr_details
            }
        
        return {
            "status": "success",
            "fixes_applied": 0,
            "message": "No vulnerabilities found"
        }

    def cleanup(self) -> None:
        """Clean up all resources."""
        self.sast_client.cleanup()
        self.researcher.cleanup()
        self.fixer.cleanup()
