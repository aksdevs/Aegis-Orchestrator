"""Simplified workflow nodes for testing without external dependencies."""
from typing import Dict, Any
import logging

class SimplifiedWorkflowNodes:
    """Simplified workflow nodes for testing the LangGraph structure."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def scan_vulnerabilities(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Mock vulnerability scanning."""
        self.logger.info("Scanning repository for vulnerabilities...")
        
        # Mock vulnerability data
        vulnerabilities = [
            {
                "id": "vuln_1",
                "title": "SQL Injection",
                "description": "Potential SQL injection vulnerability",
                "severity": "HIGH",
                "cwe_id": "CWE-89",
                "file_path": "src/database.py",
                "line_number": 45,
                "code_snippet": "query = f'SELECT * FROM users WHERE id = {user_id}'",
                "confidence": 0.95
            },
            {
                "id": "vuln_2", 
                "title": "Cross-Site Scripting",
                "description": "Potential XSS vulnerability",
                "severity": "MEDIUM",
                "cwe_id": "CWE-79",
                "file_path": "templates/user_profile.html",
                "line_number": 12,
                "code_snippet": "<div>{{ user_input | safe }}</div>",
                "confidence": 0.87
            }
        ]
        
        return {
            **state,
            "vulnerabilities": vulnerabilities,
            "analysis_results": {
                "files_scanned": 45,
                "lines_of_code": 2847,
                "scan_duration": "2.3s"
            }
        }
        
    def research_vulnerabilities(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Mock vulnerability research."""
        self.logger.info("Researching vulnerabilities...")
        
        vulnerabilities = state.get("vulnerabilities", [])
        
        # Add research data to vulnerabilities
        for vuln in vulnerabilities:
            if vuln["id"] == "vuln_1":
                vuln["research_data"] = {
                    "remediation": "Use parameterized queries or prepared statements",
                    "references": ["https://owasp.org/www-community/attacks/SQL_Injection"],
                    "impact": "Data breach, unauthorized data access"
                }
            elif vuln["id"] == "vuln_2":
                vuln["research_data"] = {
                    "remediation": "Escape user input before rendering",
                    "references": ["https://owasp.org/www-community/attacks/xss/"],
                    "impact": "Session hijacking, defacement"
                }
        
        return {
            **state,
            "vulnerabilities": vulnerabilities
        }
        
    def generate_fixes(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Mock fix generation.""" 
        self.logger.info("Generating fixes...")
        
        vulnerabilities = state.get("vulnerabilities", [])
        fixes = []
        
        for vuln in vulnerabilities:
            if vuln["id"] == "vuln_1":
                fixes.append({
                    "id": "fix_1",
                    "vulnerability_id": "vuln_1",
                    "fix_type": "SQL Injection Fix",
                    "description": "Replace string formatting with parameterized query",
                    "file_path": "src/database.py",
                    "original_code": "query = f'SELECT * FROM users WHERE id = {user_id}'",
                    "fixed_code": "query = 'SELECT * FROM users WHERE id = ?'",
                    "confidence": 0.95
                })
            elif vuln["id"] == "vuln_2":
                fixes.append({
                    "id": "fix_2", 
                    "vulnerability_id": "vuln_2",
                    "fix_type": "XSS Protection",
                    "description": "Escape user input to prevent XSS",
                    "file_path": "templates/user_profile.html",
                    "original_code": "<div>{{ user_input | safe }}</div>",
                    "fixed_code": "<div>{{ user_input | e }}</div>",
                    "confidence": 0.87
                })
        
        return {
            **state,
            "fixes": fixes
        }
        
    def review_fixes(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Mock fix review."""
        self.logger.info("Reviewing fixes...")
        
        fixes = state.get("fixes", [])
        
        # Mark all fixes as approved for this mock
        for fix in fixes:
            fix["review_status"] = "approved"
            fix["review_comments"] = "Fix looks good and follows security best practices"
            
        return {
            **state,
            "fixes": fixes,
            "review_complete": True
        }
        
    def create_pr(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Mock PR creation."""
        self.logger.info("Creating pull request...")
        
        fixes = state.get("fixes", [])
        approved_fixes = [f for f in fixes if f.get("review_status") == "approved"]
        
        mock_pr_url = "https://github.com/example/repo/pull/123"
        
        return {
            **state,
            "pull_request_url": mock_pr_url,
            "pr_created": True,
            "fixes_applied": len(approved_fixes)
        }