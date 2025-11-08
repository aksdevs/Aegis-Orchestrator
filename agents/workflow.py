"""LangGraph state definitions and workflow orchestration for security automation."""
from typing import Dict, List, Optional, TypedDict, Annotated
from enum import Enum
import operator
from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolNode  # Not needed for this workflow
from langchain_core.messages import BaseMessage

class WorkflowState(Enum):
    """Enum for workflow states."""
    INITIALIZE = "initialize"
    SCAN_VULNERABILITIES = "scan_vulnerabilities" 
    RESEARCH_VULNERABILITIES = "research_vulnerabilities"
    GENERATE_FIXES = "generate_fixes"
    REVIEW_FIXES = "review_fixes"
    CREATE_PR = "create_pr"
    COMPLETE = "complete"
    ERROR = "error"

class VulnerabilityInfo(TypedDict):
    """Type definition for vulnerability information."""
    id: str
    title: str
    description: str
    severity: str
    cwe_id: Optional[str]
    file_path: str
    line_number: int
    code_snippet: str
    confidence: float

class FixInfo(TypedDict):
    """Type definition for fix information."""
    vulnerability_id: str
    file_path: str
    original_code: str
    fixed_code: str
    explanation: str
    confidence: float
    review_status: str

class AegisState(TypedDict):
    """State definition for the Aegis Orchestrator workflow."""
    # Repository information
    repo_url: str
    repo_path: Optional[str]
    branch_name: Optional[str]
    
    # Workflow control
    current_state: WorkflowState
    messages: Annotated[List[BaseMessage], operator.add]
    error_message: Optional[str]
    
    # Vulnerability analysis
    vulnerabilities: List[VulnerabilityInfo]
    research_results: Dict[str, Dict]
    
    # Fix generation and review
    fixes: List[FixInfo]
    reviewed_fixes: List[FixInfo]
    
    # Final output
    pull_request_url: Optional[str]
    summary_report: Optional[str]

def create_aegis_workflow() -> StateGraph:
    """Create the main LangGraph workflow for vulnerability remediation."""
    
    def initialize_workspace(state: AegisState) -> AegisState:
        """Initialize the workspace and clone repository."""
        from agents.workflow_nodes import WorkflowNodes
        nodes = WorkflowNodes()
        return nodes.initialize_workspace(state)
    
    def scan_for_vulnerabilities(state: AegisState) -> AegisState:
        """Scan repository for security vulnerabilities."""
        from agents.workflow_nodes import WorkflowNodes
        nodes = WorkflowNodes()
        return nodes.scan_vulnerabilities(state)
    
    def research_vulnerabilities(state: AegisState) -> AegisState:
        """Research vulnerabilities for context and remediation approaches."""
        from agents.workflow_nodes import WorkflowNodes
        nodes = WorkflowNodes()
        return nodes.research_vulnerabilities(state)
    
    def generate_fixes(state: AegisState) -> AegisState:
        """Generate code fixes for identified vulnerabilities."""
        from agents.workflow_nodes import WorkflowNodes
        nodes = WorkflowNodes()
        return nodes.generate_fixes(state)
    
    def review_fixes(state: AegisState) -> AegisState:
        """Review and validate generated fixes."""
        from agents.workflow_nodes import WorkflowNodes
        nodes = WorkflowNodes()
        return nodes.review_fixes(state)
    
    def create_pull_request(state: AegisState) -> AegisState:
        """Create pull request with fixes and documentation."""
        from agents.workflow_nodes import WorkflowNodes
        nodes = WorkflowNodes()
        return nodes.create_pull_request(state)
    
    def route_workflow(state: AegisState) -> str:
        """Route workflow based on current state."""
        current_state = state.get("current_state", WorkflowState.INITIALIZE)
        
        if current_state == WorkflowState.INITIALIZE:
            return "scan_vulnerabilities"
        elif current_state == WorkflowState.SCAN_VULNERABILITIES:
            if state.get("vulnerabilities"):
                return "research_vulnerabilities"
            else:
                return END
        elif current_state == WorkflowState.RESEARCH_VULNERABILITIES:
            return "generate_fixes"
        elif current_state == WorkflowState.GENERATE_FIXES:
            return "review_fixes"
        elif current_state == WorkflowState.REVIEW_FIXES:
            return "create_pr"
        elif current_state == WorkflowState.CREATE_PR:
            return END
        elif current_state == WorkflowState.ERROR:
            return END
        else:
            return END
    
    # Create the workflow graph
    workflow = StateGraph(AegisState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_workspace)
    workflow.add_node("scan_vulnerabilities", scan_for_vulnerabilities)
    workflow.add_node("research_vulnerabilities", research_vulnerabilities)
    workflow.add_node("generate_fixes", generate_fixes)
    workflow.add_node("review_fixes", review_fixes)
    workflow.add_node("create_pr", create_pull_request)
    
    # Add edges
    workflow.set_entry_point("initialize")
    workflow.add_conditional_edges(
        "initialize",
        route_workflow,
        {
            "scan_vulnerabilities": "scan_vulnerabilities",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "scan_vulnerabilities", 
        route_workflow,
        {
            "research_vulnerabilities": "research_vulnerabilities",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "research_vulnerabilities",
        route_workflow,
        {
            "generate_fixes": "generate_fixes",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "generate_fixes",
        route_workflow,
        {
            "review_fixes": "review_fixes",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "review_fixes",
        route_workflow,
        {
            "create_pr": "create_pr",
            END: END
        }
    )
    workflow.add_edge("create_pr", END)
    
    return workflow.compile()

# Create the compiled workflow
aegis_workflow = create_aegis_workflow()