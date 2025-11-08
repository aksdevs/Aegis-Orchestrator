"""Simplified LangGraph workflow for testing without external dependencies."""
from typing import Dict, Any
from enum import Enum
from langgraph.graph import StateGraph, END
from agents.simplified_workflow_nodes import SimplifiedWorkflowNodes

class WorkflowState(Enum):
    """Workflow state enumeration."""
    INITIALIZE = "initialize"
    SCAN_VULNERABILITIES = "scan_vulnerabilities"
    RESEARCH_VULNERABILITIES = "research_vulnerabilities" 
    GENERATE_FIXES = "generate_fixes"
    REVIEW_FIXES = "review_fixes"
    CREATE_PR = "create_pr"
    COMPLETE = "complete"
    ERROR = "error"

def should_research(state: Dict[str, Any]) -> str:
    """Decide whether to research vulnerabilities."""
    vulnerabilities = state.get("vulnerabilities", [])
    if vulnerabilities:
        return "research_vulnerabilities"
    return "complete"

def should_fix(state: Dict[str, Any]) -> str:
    """Decide whether to generate fixes."""
    vulnerabilities = state.get("vulnerabilities", [])
    if vulnerabilities:
        return "generate_fixes"
    return "complete"

def should_review(state: Dict[str, Any]) -> str:
    """Decide whether to review fixes."""
    fixes = state.get("fixes", [])
    if fixes:
        return "review_fixes"
    return "complete"

def should_create_pr(state: Dict[str, Any]) -> str:
    """Decide whether to create pull request."""
    fixes = state.get("fixes", [])
    approved_fixes = [f for f in fixes if f.get("review_status") == "approved"]
    if approved_fixes:
        return "create_pr"
    return "complete"

def create_simplified_workflow():
    """Create a simplified LangGraph workflow for testing."""
    
    # Initialize workflow nodes
    nodes = SimplifiedWorkflowNodes()
    
    # Create the state graph
    workflow = StateGraph(dict)
    
    # Add nodes to the workflow
    workflow.add_node("scan_vulnerabilities", nodes.scan_vulnerabilities)
    workflow.add_node("research_vulnerabilities", nodes.research_vulnerabilities)
    workflow.add_node("generate_fixes", nodes.generate_fixes)
    workflow.add_node("review_fixes", nodes.review_fixes)
    workflow.add_node("create_pr", nodes.create_pr)
    
    # Set entry point
    workflow.set_entry_point("scan_vulnerabilities")
    
    # Add edges with conditional routing
    workflow.add_conditional_edges(
        "scan_vulnerabilities",
        should_research,
        {
            "research_vulnerabilities": "research_vulnerabilities",
            "complete": END
        }
    )
    
    workflow.add_conditional_edges(
        "research_vulnerabilities",
        should_fix,
        {
            "generate_fixes": "generate_fixes",
            "complete": END
        }
    )
    
    workflow.add_conditional_edges(
        "generate_fixes", 
        should_review,
        {
            "review_fixes": "review_fixes",
            "complete": END
        }
    )
    
    workflow.add_conditional_edges(
        "review_fixes",
        should_create_pr,
        {
            "create_pr": "create_pr",
            "complete": END
        }
    )
    
    workflow.add_edge("create_pr", END)
    
    # Compile the workflow
    return workflow.compile()