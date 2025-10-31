"""Agent responsible for running tests against a repository and reporting results.

This tester agent is intentionally minimal so unit tests can exercise it
without network calls. It uses `services.testing_harness.TestingHarness` to
run tests and `services.git_handler.GitHandler` to manage repository cloning
when a real GitHandler is provided.
"""
from typing import Dict, Optional
from services.testing_harness import TestingHarness
from services.git_handler import GitHandler


class TesterAgent:
    """Runs tests for a target repository and produces a report.

    The class is lightweight and test-friendly: callers can inject a
    `TestingHarness` or `GitHandler` mock to avoid external calls.
    """

    def __init__(self, testing_harness: Optional[TestingHarness] = None) -> None:
        self.testing_harness = testing_harness or TestingHarness()
        self.git_handler: Optional[GitHandler] = None
        self.repo_path: Optional[str] = None

    def setup_workspace(self, workspace_dir: str, repo_url: str, git_handler: Optional[GitHandler] = None) -> None:
        """Prepare a workspace by cloning the repository (if necessary).

        If `git_handler` is provided it will be used; otherwise a new
        `GitHandler` will be created which will perform a real clone.
        """
        if git_handler is not None:
            self.git_handler = git_handler
        else:
            self.git_handler = GitHandler(workspace_dir)

        # Clone repository and keep repo path
        self.repo_path = self.git_handler.clone_repository(repo_url)

    def run_tests(self) -> Dict:
        """Run tests using the configured TestingHarness against the cloned repo.

        Returns the dictionary returned by `TestingHarness.run_tests`.
        """
        if not self.repo_path:
            raise RuntimeError("Repository not set up. Call setup_workspace first.")
        return self.testing_harness.run_tests(self.repo_path)

    def generate_report(self, results: Dict) -> str:
        """Return a human-readable report for the given test results."""
        return self.testing_harness.generate_report(results)

    def validate_results(self, results: Dict) -> bool:
        """Validate test results and return True if they indicate success."""
        return self.testing_harness.validate_results(results)

    def create_test_comment(self, results: Dict, pr_url: Optional[str] = None) -> Dict:
        """Create a comment payload summarizing test results for a PR.

        This is a small helper that formats the test summary. In a full
        implementation this would call the GitHub API or Git provider to post
        the comment.
        """
        report = self.generate_report(results)
        payload = {
            "pr_url": pr_url,
            "report": report,
            "status": "passed" if self.validate_results(results) else "failed"
        }
        return payload

    def cleanup(self) -> None:
        """Clean up resources used by the tester agent."""
        if self.git_handler:
            try:
                self.git_handler.cleanup()
            except Exception:
                # Best-effort cleanup; do not raise during cleanup
                pass
        try:
            self.testing_harness.cleanup()
        except Exception:
            pass
