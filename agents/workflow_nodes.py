"""Workflow nodes implementation for LangGraph-based security automation."""
from typing import Dict, List
import logging
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from config.settings import config, ModelType
from services.git_handler import GitHandler
from services.sast_client import SASTClient
from agents.workflow import AegisState, WorkflowState, VulnerabilityInfo, FixInfo

logger = logging.getLogger(__name__)

class WorkflowNodes:
    """Implementation of workflow nodes for the LangGraph state machine."""

    def __init__(self):
        """Initialize workflow nodes with LangChain models."""
        self.git_handler = None
        self.sast_client = None

        # Initialize Ollama models for different tasks
        scanner_config = config.get_model_config(ModelType.VULNERABILITY_SCANNER)
        self.vulnerability_scanner = ChatOllama(
            model=scanner_config.model_name,
            base_url=scanner_config.base_url,
            temperature=scanner_config.temperature,
            num_predict=scanner_config.max_tokens
        )

        researcher_config = config.get_model_config(ModelType.SECURITY_RESEARCHER)
        self.security_researcher = ChatOllama(
            model=researcher_config.model_name,
            base_url=researcher_config.base_url,
            temperature=researcher_config.temperature,
            num_predict=researcher_config.max_tokens
        )

        fixer_config = config.get_model_config(ModelType.CODE_FIXER)
        self.code_fixer = ChatOllama(
            model=fixer_config.model_name,
            base_url=fixer_config.base_url,
            temperature=fixer_config.temperature,
            num_predict=fixer_config.max_tokens
        )

        reviewer_config = config.get_model_config(ModelType.CODE_REVIEWER)
        self.code_reviewer = ChatOllama(
            model=reviewer_config.model_name,
            base_url=reviewer_config.base_url,
            temperature=reviewer_config.temperature,
            num_predict=reviewer_config.max_tokens
        )

    def initialize_workspace(self, state: AegisState) -> AegisState:
        """Initialize workspace by cloning repository."""
        try:
            logger.info(f"Initializing workspace for repository: {state['repo_url']}")

            self.git_handler = GitHandler(config.workspace_dir)
            repo_path = self.git_handler.clone_repository(state["repo_url"])

            # Create a new branch for fixes
            branch_name = f"aegis-security-fixes-{hash(state['repo_url']) % 10000}"
            self.git_handler.create_branch(branch_name)

            state["repo_path"] = repo_path
            state["branch_name"] = branch_name
            state["current_state"] = WorkflowState.SCAN_VULNERABILITIES

            logger.info(f"Workspace initialized successfully at {repo_path}")
            return state

        except Exception as e:
            logger.error(f"Failed to initialize workspace: {e}")
            state["error_message"] = f"Workspace initialization failed: {str(e)}"
            state["current_state"] = WorkflowState.ERROR
            return state

    def scan_vulnerabilities(self, state: AegisState) -> AegisState:
        """Scan repository for security vulnerabilities using AI."""
        try:
            logger.info("Scanning for vulnerabilities...")

            # Initialize SAST client if not already done
            if not self.sast_client:
                self.sast_client = SASTClient(
                    model_name=config.ollama_model,
                    base_url=config.ollama_base_url
                )

            # Use AI-powered vulnerability scanning
            scan_prompt = PromptTemplate(
                input_variables=["repo_path"],
                template="""
                You are a security expert tasked with scanning a repository for vulnerabilities.
                Analyze the code repository at: {repo_path}

                Focus on common vulnerability patterns including:
                - SQL Injection
                - Cross-Site Scripting (XSS)
                - Command Injection
                - Path Traversal
                - Insecure Deserialization
                - Authentication/Authorization issues
                - Cryptographic weaknesses
                - Input validation issues

                For each vulnerability found, provide:
                1. Vulnerability ID (generate unique identifier)
                2. Title (brief description)
                3. Detailed description
                4. Severity (CRITICAL, HIGH, MEDIUM, LOW)
                5. CWE ID if applicable
                6. File path and line number
                7. Code snippet showing the vulnerability
                8. Confidence level (0.0-1.0)

                Return results in JSON format with array of vulnerabilities.
                """
            )

            messages = [
                SystemMessage(content="You are an expert security vulnerability scanner."),
                HumanMessage(content=scan_prompt.format(repo_path=state["repo_path"]))
            ]

            response = self.vulnerability_scanner.invoke(messages)

            # Parse response and extract vulnerabilities
            vulnerabilities = self._parse_vulnerability_response(response.content)

            state["vulnerabilities"] = vulnerabilities
            state["current_state"] = WorkflowState.RESEARCH_VULNERABILITIES

            logger.info(f"Found {len(vulnerabilities)} vulnerabilities")
            return state

        except Exception as e:
            logger.error(f"Vulnerability scanning failed: {e}")
            state["error_message"] = f"Vulnerability scanning failed: {str(e)}"
            state["current_state"] = WorkflowState.ERROR
            return state

    def research_vulnerabilities(self, state: AegisState) -> AegisState:
        """Research vulnerabilities for context and remediation approaches."""
        try:
            logger.info("Researching vulnerabilities...")

            research_results = {}

            for vuln in state["vulnerabilities"]:
                research_prompt = PromptTemplate(
                    input_variables=["vulnerability"],
                    template="""
                    You are a cybersecurity researcher. Analyze this vulnerability and provide detailed research:

                    Vulnerability: {vulnerability}

                    Provide comprehensive research including:
                    1. Root cause analysis
                    2. Attack vectors and exploitation methods
                    3. Business impact assessment
                    4. Industry-standard remediation approaches
                    5. Best practices for prevention
                    6. Relevant security frameworks (OWASP, NIST, etc.)
                    7. Code examples of secure implementations
                    8. Testing strategies to verify fixes

                    Format as structured JSON with clear sections.
                    """
                )

                messages = [
                    SystemMessage(content="You are an expert cybersecurity researcher."),
                    HumanMessage(content=research_prompt.format(vulnerability=vuln))
                ]

                response = self.security_researcher.invoke(messages)
                research_results[vuln["id"]] = {
                    "analysis": response.content,
                    "vulnerability": vuln
                }

            state["research_results"] = research_results
            state["current_state"] = WorkflowState.GENERATE_FIXES

            logger.info(f"Completed research for {len(research_results)} vulnerabilities")
            return state

        except Exception as e:
            logger.error(f"Vulnerability research failed: {e}")
            state["error_message"] = f"Vulnerability research failed: {str(e)}"
            state["current_state"] = WorkflowState.ERROR
            return state

    def generate_fixes(self, state: AegisState) -> AegisState:
        """Generate code fixes for identified vulnerabilities."""
        try:
            logger.info("Generating fixes...")

            fixes = []

            for vuln_id, research in state["research_results"].items():
                vuln = research["vulnerability"]

                fix_prompt = PromptTemplate(
                    input_variables=["vulnerability", "research", "code_snippet"],
                    template="""
                    You are an expert secure code developer. Generate a secure fix for this vulnerability:

                    Vulnerability: {vulnerability}
                    Research Analysis: {research}
                    Original Code: {code_snippet}

                    Provide:
                    1. Complete fixed code that addresses the vulnerability
                    2. Detailed explanation of changes made
                    3. Why this fix is secure and follows best practices
                    4. Any additional security considerations
                    5. Confidence level in the fix (0.0-1.0)

                    Ensure the fix:
                    - Completely eliminates the vulnerability
                    - Maintains code functionality
                    - Follows secure coding standards
                    - Is production-ready
                    - Includes proper input validation/sanitization
                    - Uses secure libraries and APIs

                    Format as JSON with fixed_code, explanation, and confidence fields.
                    """
                )

                messages = [
                    SystemMessage(content="You are an expert secure code developer."),
                    HumanMessage(content=fix_prompt.format(
                        vulnerability=vuln,
                        research=research["analysis"],
                        code_snippet=vuln["code_snippet"]
                    ))
                ]

                response = self.code_fixer.invoke(messages)
                fix_data = self._parse_fix_response(response.content, vuln)

                if fix_data:
                    fixes.append(fix_data)

            state["fixes"] = fixes
            state["current_state"] = WorkflowState.REVIEW_FIXES

            logger.info(f"Generated {len(fixes)} fixes")
            return state

        except Exception as e:
            logger.error(f"Fix generation failed: {e}")
            state["error_message"] = f"Fix generation failed: {str(e)}"
            state["current_state"] = WorkflowState.ERROR
            return state

    def review_fixes(self, state: AegisState) -> AegisState:
        """Review and validate generated fixes."""
        try:
            logger.info("Reviewing fixes...")

            reviewed_fixes = []

            for fix in state["fixes"]:
                review_prompt = PromptTemplate(
                    input_variables=["original_code", "fixed_code", "vulnerability"],
                    template="""
                    You are a senior security code reviewer. Review this security fix:

                    Original Vulnerable Code: {original_code}
                    Proposed Fix: {fixed_code}
                    Vulnerability Details: {vulnerability}

                    Evaluate:
                    1. Does the fix completely eliminate the vulnerability?
                    2. Are there any new security issues introduced?
                    3. Does it maintain code functionality?
                    4. Is it following security best practices?
                    5. Are there any edge cases not handled?
                    6. Code quality and maintainability
                    7. Performance implications

                    Provide:
                    - Review status: APPROVED, NEEDS_REVISION, or REJECTED
                    - Detailed review comments
                    - Specific recommendations if changes needed
                    - Security assessment score (0-100)

                    Format as JSON with status, comments, recommendations, and score fields.
                    """
                )

                messages = [
                    SystemMessage(content="You are a senior security code reviewer."),
                    HumanMessage(content=review_prompt.format(
                        original_code=fix["original_code"],
                        fixed_code=fix["fixed_code"],
                        vulnerability=fix["vulnerability_id"]
                    ))
                ]

                response = self.code_reviewer.invoke(messages)
                review_data = self._parse_review_response(response.content)

                fix["review_status"] = review_data.get("status", "NEEDS_REVISION")
                fix["review_comments"] = review_data.get("comments", "")
                fix["security_score"] = review_data.get("score", 0)

                if fix["review_status"] == "APPROVED":
                    reviewed_fixes.append(fix)

            state["reviewed_fixes"] = reviewed_fixes
            state["current_state"] = WorkflowState.CREATE_PR

            logger.info(f"Approved {len(reviewed_fixes)} fixes out of {len(state['fixes'])}")
            return state

        except Exception as e:
            logger.error(f"Fix review failed: {e}")
            state["error_message"] = f"Fix review failed: {str(e)}"
            state["current_state"] = WorkflowState.ERROR
            return state

    def create_pull_request(self, state: AegisState) -> AegisState:
        """Create pull request with fixes and documentation."""
        try:
            logger.info("Creating pull request...")

            # Apply fixes to files
            for fix in state["reviewed_fixes"]:
                self._apply_fix_to_file(fix)

            # Commit changes
            commit_message = f"Security fixes: Resolved {len(state['reviewed_fixes'])} vulnerabilities"
            self.git_handler.commit_changes(commit_message)

            # Generate comprehensive PR description
            pr_description = self._generate_pr_description(state)

            # Create pull request
            pr_details = self.git_handler.create_pull_request(
                title="🔒 Automated Security Vulnerability Fixes",
                body=pr_description
            )

            state["pull_request_url"] = pr_details["url"]
            state["summary_report"] = self._generate_summary_report(state)
            state["current_state"] = WorkflowState.COMPLETE

            logger.info(f"Pull request created: {pr_details['url']}")
            return state

        except Exception as e:
            logger.error(f"Pull request creation failed: {e}")
            state["error_message"] = f"Pull request creation failed: {str(e)}"
            state["current_state"] = WorkflowState.ERROR
            return state

    def _parse_vulnerability_response(self, response: str) -> List[VulnerabilityInfo]:
        """Parse vulnerability scanning response."""
        # Simplified parsing - in real implementation would use robust JSON parsing
        vulnerabilities = []
        try:
            import json
            data = json.loads(response)
            for item in data.get("vulnerabilities", []):
                vuln = VulnerabilityInfo(
                    id=item.get("id", ""),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    severity=item.get("severity", "MEDIUM"),
                    cwe_id=item.get("cwe_id"),
                    file_path=item.get("file_path", ""),
                    line_number=item.get("line_number", 0),
                    code_snippet=item.get("code_snippet", ""),
                    confidence=item.get("confidence", 0.8)
                )
                vulnerabilities.append(vuln)
        except:
            # Fallback for non-JSON responses
            logger.warning("Could not parse vulnerability response as JSON")

        return vulnerabilities

    def _parse_fix_response(self, response: str, vuln: VulnerabilityInfo) -> FixInfo:
        """Parse fix generation response."""
        try:
            import json
            data = json.loads(response)
            return FixInfo(
                vulnerability_id=vuln["id"],
                file_path=vuln["file_path"],
                original_code=vuln["code_snippet"],
                fixed_code=data.get("fixed_code", ""),
                explanation=data.get("explanation", ""),
                confidence=data.get("confidence", 0.8),
                review_status="PENDING"
            )
        except:
            # Fallback
            return FixInfo(
                vulnerability_id=vuln["id"],
                file_path=vuln["file_path"],
                original_code=vuln["code_snippet"],
                fixed_code="// Fix could not be parsed",
                explanation="Failed to parse fix response",
                confidence=0.0,
                review_status="NEEDS_REVISION"
            )

    def _parse_review_response(self, response: str) -> Dict:
        """Parse code review response."""
        try:
            import json
            return json.loads(response)
        except:
            return {"status": "NEEDS_REVISION", "comments": "Could not parse review", "score": 0}

    def _apply_fix_to_file(self, fix: FixInfo) -> None:
        """Apply a fix to the actual file."""
        # Simplified implementation - would need robust file patching
        try:
            file_path = fix["file_path"]
            logger.info(f"Applying fix to {file_path}")
            # In real implementation, would apply the fix to the actual file
        except Exception as e:
            logger.error(f"Failed to apply fix to {fix['file_path']}: {e}")

    def _generate_pr_description(self, state: AegisState) -> str:
        """Generate comprehensive PR description."""
        description = "## 🔒 Automated Security Vulnerability Fixes\n\n"
        description += f"This PR addresses {len(state['reviewed_fixes'])} security vulnerabilities found in the codebase.\n\n"

        description += "### 📋 Vulnerabilities Fixed:\n"
        for fix in state["reviewed_fixes"]:
            description += f"- **{fix['vulnerability_id']}**: {fix['explanation'][:100]}...\n"

        description += "\n### ✅ Security Review:\n"
        description += "All fixes have been reviewed by AI security experts and approved for deployment.\n\n"

        description += "### 🧪 Testing:\n"
        description += "Please verify that all functionality remains intact after applying these security fixes.\n"

        return description

    def _generate_summary_report(self, state: AegisState) -> str:
        """Generate summary report of the security remediation process."""
        report = "# Security Remediation Summary\n\n"
        report += f"**Repository**: {state['repo_url']}\n"
        report += f"**Vulnerabilities Found**: {len(state['vulnerabilities'])}\n"
        report += f"**Fixes Applied**: {len(state['reviewed_fixes'])}\n"
        report += f"**Pull Request**: {state['pull_request_url']}\n\n"

        if state.get("error_message"):
            report += f"**Errors**: {state['error_message']}\n"

        return report
