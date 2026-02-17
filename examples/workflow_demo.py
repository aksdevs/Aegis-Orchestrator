"""Example script demonstrating the Aegis Orchestrator LangGraph workflow."""
import os
import sys
from typing import Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.workflow import create_aegis_workflow, WorkflowState
from config.settings import config

async def run_example_workflow(repo_url: str = "https://github.com/example/vulnerable-app") -> Dict[str, Any]:
    """Run an example workflow with the Aegis Orchestrator.
    
    Args:
        repo_url: Repository URL to analyze
        
    Returns:
        Dict containing workflow results
    """
    print("🚀 Starting Aegis Orchestrator Example Workflow")
    print("=" * 60)
    
    # Create the LangGraph workflow
    workflow = create_aegis_workflow()
    
    # Define initial state
    initial_state = {
        "repository_url": repo_url,
        "vulnerabilities": [],
        "fixes": [],
        "analysis_results": {},
        "current_state": WorkflowState.SCAN_VULNERABILITIES,
        "pull_request_url": None,
        "error_message": None
    }
    
    print("📋 Configuration:")
    print(f"  - Repository: {repo_url}")
    
    from config.settings import ModelType
    scanner_config = config.get_model_config(ModelType.VULNERABILITY_SCANNER)
    researcher_config = config.get_model_config(ModelType.SECURITY_RESEARCHER)
    fixer_config = config.get_model_config(ModelType.CODE_FIXER)
    reviewer_config = config.get_model_config(ModelType.CODE_REVIEWER)
    
    print(f"  - Scanner Model: {scanner_config.model_name}")
    print(f"  - Researcher Model: {researcher_config.model_name}")
    print(f"  - Fixer Model: {fixer_config.model_name}")
    print(f"  - Reviewer Model: {reviewer_config.model_name}")
    print()
    
    try:
        print("🔄 Executing LangGraph workflow...")
        
        # Execute the workflow
        final_state = await workflow.ainvoke(initial_state)
        
        # Display results
        print("\n✅ Workflow Execution Complete!")
        print("=" * 40)
        
        return {
            "status": "success" if final_state["current_state"] == WorkflowState.COMPLETE else "incomplete",
            "final_state": final_state["current_state"].value,
            "vulnerabilities_found": len(final_state["vulnerabilities"]),
            "fixes_applied": len(final_state["fixes"]),
            "pull_request": {
                "url": final_state.get("pull_request_url"),
                "created": final_state.get("pull_request_url") is not None
            },
            "analysis_results": final_state["analysis_results"],
            "summary_report": generate_summary_report(final_state)
        }
        
    except (ValueError, ConnectionError, OSError) as e:
        print(f"\n❌ Workflow failed with error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "vulnerabilities_found": 0,
            "fixes_applied": 0
        }

def generate_summary_report(state: Dict[str, Any]) -> str:
    """Generate a summary report from the workflow state."""
    vulnerabilities = state.get("vulnerabilities", [])
    fixes = state.get("fixes", [])
    
    report = []
    report.append("📊 SECURITY ANALYSIS SUMMARY")
    report.append("=" * 30)
    
    if vulnerabilities:
        report.append(f"\n🔍 Vulnerabilities Detected ({len(vulnerabilities)}):")
        for i, vuln in enumerate(vulnerabilities, 1):
            vuln_type = vuln.get("type", "Unknown")
            severity = vuln.get("severity", "Unknown")
            file_path = vuln.get("file", "Unknown file")
            report.append(f"  {i}. {vuln_type} ({severity}) in {file_path}")
    else:
        report.append("\n✅ No vulnerabilities detected!")
    
    if fixes:
        report.append(f"\n🛠️ Fixes Applied ({len(fixes)}):")
        for i, fix in enumerate(fixes, 1):
            fix_type = fix.get("type", "Unknown fix")
            status = fix.get("status", "Unknown")
            report.append(f"  {i}. {fix_type} - Status: {status}")
    
    analysis_results = state.get("analysis_results", {})
    if analysis_results:
        report.append("\n📈 Analysis Metrics:")
        for metric, value in analysis_results.items():
            report.append(f"  • {metric}: {value}")
    
    return "\n".join(report)

def print_workflow_info():
    """Print information about the workflow structure."""
    print("🏗️ AEGIS ORCHESTRATOR WORKFLOW ARCHITECTURE")
    print("=" * 50)
    
    workflow_steps = [
        ("1. SCANNING", "Analyze repository for security vulnerabilities using AI"),
        ("2. RESEARCH", "Research vulnerability details and remediation strategies"),
        ("3. FIXING", "Generate and apply security fixes using AI models"),
        ("4. REVIEW", "Review fixes for quality and effectiveness"),
        ("5. COMPLETE", "Create pull request with security improvements")
    ]
    
    for step, description in workflow_steps:
        print(f"\n{step}")
        print(f"   └─ {description}")
    
    print("\n🤖 AI Models Configuration:")
    from config.settings import ModelType
    scanner_config = config.get_model_config(ModelType.VULNERABILITY_SCANNER)
    researcher_config = config.get_model_config(ModelType.SECURITY_RESEARCHER)
    fixer_config = config.get_model_config(ModelType.CODE_FIXER)
    reviewer_config = config.get_model_config(ModelType.CODE_REVIEWER)
    
    print(f"   • Scanner: {scanner_config.model_name}")
    print(f"   • Researcher: {researcher_config.model_name}") 
    print(f"   • Fixer: {fixer_config.model_name}")
    print(f"   • Reviewer: {reviewer_config.model_name}")
    
    print("\n🌍 LLM Provider: Ollama (Local)")
    print(f"   • Base URL: {config.ollama_base_url}")
    print(f"   • Model: {config.ollama_model}")

def main():
    """Main example execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aegis Orchestrator Example")
    parser.add_argument(
        "--repo-url",
        default="https://github.com/example/vulnerable-app",
        help="Repository URL to analyze"
    )
    parser.add_argument(
        "--info-only",
        action="store_true",
        help="Show workflow information only"
    )
    
    args = parser.parse_args()
    
    if args.info_only:
        print_workflow_info()
        return
    
    # Note: This is a mock example since we need a running Ollama instance
    print("📝 NOTE: This is a demonstration of the workflow structure.")
    print("🔑 To run with real AI models, ensure Ollama is running locally.")
    print()
    
    print_workflow_info()
    print("\n" + "=" * 60)
    
    # Simulate workflow execution with mock data
    mock_result = {
        "status": "success",
        "final_state": "complete",
        "vulnerabilities_found": 3,
        "fixes_applied": 2,
        "pull_request": {
            "url": "https://github.com/example/vulnerable-app/pull/123",
            "created": True
        },
        "analysis_results": {
            "sql_injection_risks": 2,
            "xss_vulnerabilities": 1,
            "files_analyzed": 45,
            "lines_of_code": 2847
        },
        "summary_report": """📊 SECURITY ANALYSIS SUMMARY
==============================

🔍 Vulnerabilities Detected (3):
  1. SQL Injection (High) in src/database/queries.py
  2. Cross-Site Scripting (Medium) in templates/user_profile.html
  3. Insecure Deserialization (High) in utils/serializer.py

🛠️ Fixes Applied (2):
  1. SQL Injection Fix - Status: completed
  2. XSS Protection - Status: completed

📈 Analysis Metrics:
  • sql_injection_risks: 2
  • xss_vulnerabilities: 1
  • files_analyzed: 45
  • lines_of_code: 2847"""
    }
    
    print("\n🎯 Mock Workflow Results:")
    print(f"✅ Status: {mock_result['status'].upper()}")
    print(f"🔍 Vulnerabilities Found: {mock_result['vulnerabilities_found']}")
    print(f"🛠️ Fixes Applied: {mock_result['fixes_applied']}")
    
    if mock_result['pull_request']['created']:
        print(f"🔗 Pull Request: {mock_result['pull_request']['url']}")
    
    print(f"\n{mock_result['summary_report']}")

if __name__ == "__main__":
    main()