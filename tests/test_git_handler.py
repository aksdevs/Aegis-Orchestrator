import unittest
import os
import shutil
from unittest.mock import Mock, patch
from services.git_handler import GitHandler

class TestGitHandler(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_workspace = os.path.join(os.path.dirname(__file__), "test_workspace")
        self.git_handler = GitHandler(self.test_workspace)

    def tearDown(self):
        """Clean up test workspace after each test."""
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)

    def test_initialization(self):
        """Test that the GitHandler initializes correctly."""
        self.assertIsNotNone(self.git_handler)
        self.assertEqual(self.git_handler.workspace_dir, self.test_workspace)
        self.assertIsNone(self.git_handler.repo)

    @patch('services.git_handler.Repo')
    def test_clone_repository(self, mock_repo):
        """Test repository cloning functionality."""
        # Setup test data
        test_repo_url = "https://github.com/test/repo.git"
        test_branch = "main"
        
        # Setup mock repo
        mock_repo_instance = Mock()
        mock_repo.clone_from.return_value = mock_repo_instance
        
        # Test repository cloning
        repo_path = self.git_handler.clone_repository(test_repo_url, test_branch)
        
        # Verify repository was cloned correctly
        expected_path = os.path.join(self.test_workspace, "repo")
        self.assertEqual(repo_path, expected_path)
        mock_repo.clone_from.assert_called_once_with(test_repo_url, expected_path)
        mock_repo_instance.git.checkout.assert_called_once_with(test_branch)
        self.assertEqual(self.git_handler.repo, mock_repo_instance)

    def test_create_branch_no_repo(self):
        """Test branch creation with no repository."""
        with self.assertRaises(Exception) as context:
            self.git_handler.create_branch("new-branch")
        self.assertIn("No repository has been cloned yet", str(context.exception))

    @patch('services.git_handler.Repo')
    def test_create_branch(self, mock_repo):
        """Test branch creation functionality."""
        # Setup mock repo
        mock_repo_instance = Mock()
        self.git_handler.repo = mock_repo_instance
        
        # Setup mock head
        mock_head = Mock()
        mock_repo_instance.create_head.return_value = mock_head
        
        # Test branch creation
        self.git_handler.create_branch("feature/new-feature")
        
        # Verify branch was created and checked out
        mock_repo_instance.create_head.assert_called_once_with("feature/new-feature")
        mock_head.checkout.assert_called_once()

    @patch('services.git_handler.Repo')
    def test_commit_changes(self, mock_repo):
        """Test changes commit functionality."""
        # Setup mock repo
        mock_repo_instance = Mock()
        mock_index = Mock()
        mock_repo_instance.index = mock_index
        self.git_handler.repo = mock_repo_instance
        
        # Test committing specific files
        test_files = ["file1.py", "file2.py"]
        result = self.git_handler.commit_changes("Test commit message", test_files)
        
        # Verify files were added and committed
        mock_index.add.assert_called_once_with(test_files)
        mock_index.commit.assert_called_once_with("Test commit message")
        self.assertTrue(result)
        
        # Test committing all changes
        mock_index.reset_mock()
        result = self.git_handler.commit_changes("Commit all changes")
        
        # Verify all changes were committed
        mock_repo_instance.git.add.assert_called_once_with(A=True)
        mock_index.commit.assert_called_once_with("Commit all changes")
        self.assertTrue(result)

    def test_commit_changes_no_repo(self):
        """Test commit changes with no repository."""
        with self.assertRaises(Exception) as context:
            self.git_handler.commit_changes("Test commit")
        self.assertIn("No repository has been cloned yet", str(context.exception))

    def test_create_pull_request(self):
        """Test pull request creation functionality."""
        # Setup mock repo
        mock_repo = Mock()
        self.git_handler.repo = mock_repo
        
        # Test data
        title = "Fix security vulnerabilities"
        body = "This PR fixes multiple security issues"
        base_branch = "main"
        
        # Create pull request
        pr_details = self.git_handler.create_pull_request(title, body, base_branch)
        
        # Verify PR details
        self.assertIsInstance(pr_details, dict)
        self.assertIn("url", pr_details)
        self.assertIn("number", pr_details)
        self.assertIn("status", pr_details)
        self.assertEqual(pr_details["status"], "open")

    def test_cleanup(self):
        """Test cleanup functionality."""
        # Setup mock repo
        mock_repo = Mock()
        self.git_handler.repo = mock_repo
        
        # Test cleanup
        self.git_handler.cleanup()
        
        # Verify repo was closed
        mock_repo.close.assert_called_once()
        self.assertTrue(os.path.exists(self.test_workspace))

if __name__ == '__main__':
    unittest.main()