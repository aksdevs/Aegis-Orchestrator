# GitHub Wiki Content for Aegis Orchestrator

## Wiki Page Structure

### Home Page (README)
```markdown
# Welcome to the Aegis Orchestrator Wiki

🔒 **AI-Powered Security Automation Platform**

This wiki contains comprehensive documentation, tutorials, and guides for using and contributing to the Aegis Orchestrator project.

## 🚀 Quick Navigation

### For Users
- [Getting Started Guide](Getting-Started)
- [Configuration Reference](Configuration)
- [API Documentation](API-Reference)
- [Troubleshooting](Troubleshooting)

### For Developers
- [Development Setup](Development-Setup)
- [Architecture Overview](Architecture)
- [Contributing Guidelines](Contributing)
- [Testing Guide](Testing)

### Advanced Topics
- [LangGraph Workflows](LangGraph-Workflows)
- [Google Cloud Integration](Google-Cloud-Setup)
- [Security Best Practices](Security)
- [Performance Tuning](Performance)

## 🆘 Need Help?
- 📧 Email: atulksin@gmail.com
- 🐛 [Create an Issue](https://github.com/atulksin/Aegis-Orchestrator/issues)
- 📚 Browse this wiki for detailed guides

## 📈 Project Status
- **Current Version**: 1.0.0
- **Build Status**: [![Build Status](https://github.com/atulksin/Aegis-Orchestrator/workflows/CI-CD/badge.svg)](https://github.com/atulksin/Aegis-Orchestrator/actions)
- **License**: Apache 2.0
```

---

### Getting Started Page
```markdown
# Getting Started with Aegis Orchestrator

Welcome to Aegis Orchestrator! This guide will help you get up and running with the AI-powered security automation platform.

## 🎯 Overview

Aegis Orchestrator automatically:
1. **Scans** your repositories for security vulnerabilities
2. **Analyzes** issues using AI models
3. **Generates** intelligent fixes
4. **Creates** pull requests with remediation
5. **Tests** fixes for effectiveness

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Git**: Latest version
- **Google Cloud Account**: With billing enabled
- **Memory**: Minimum 4GB RAM
- **Storage**: 10GB available space

### Required APIs
Enable these Google Cloud APIs:
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/atulksin/Aegis-Orchestrator.git
cd Aegis-Orchestrator
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Google Cloud
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### 4. Set Environment Variables
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

## 🧪 Test Installation

### Run Quick Test
```bash
# Test basic functionality
python main.py --help

# Test workflow
python test_workflow.py

# List supported vulnerabilities
python main.py --list-vulnerabilities
```

### Run Sample Analysis
```bash
# Analyze a public repository (dry run)
python main.py --dry-run https://github.com/example/vulnerable-repo
```

## 🎯 Your First Analysis

### 1. Prepare Target Repository
- Ensure you have read access to the repository
- Repository should contain source code
- Git credentials should be configured

### 2. Run Analysis
```bash
# Full analysis with PR creation
python main.py https://github.com/your-username/your-repo

# Analysis only (no PRs)
python main.py --dry-run https://github.com/your-username/your-repo
```

### 3. Review Results
The tool will:
- Clone the repository
- Scan for vulnerabilities
- Generate fixes using AI
- Create pull requests (if not dry-run)
- Provide detailed reports

## 📊 Understanding Output

### Console Output
```
🔍 Scanning repository: https://github.com/user/repo
📊 Found 5 vulnerabilities
🤖 Generating fixes using AI models
✅ Generated 4 fixes
🔄 Creating pull request
✅ Pull request created: https://github.com/user/repo/pull/123
```

### Result Structure
```json
{
  "status": "success",
  "vulnerabilities_found": 5,
  "fixes_generated": 4,
  "pull_request": {
    "url": "https://github.com/user/repo/pull/123",
    "title": "Security fixes by Aegis Orchestrator"
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**Authentication Errors**
```bash
# Re-authenticate
gcloud auth application-default login
```

**API Not Enabled**
```bash
# Check enabled APIs
gcloud services list --enabled
```

**Permission Denied**
- Verify service account has required permissions
- Check repository access rights

### Get Help
- Check the [Troubleshooting](Troubleshooting) page
- [Create an issue](https://github.com/atulksin/Aegis-Orchestrator/issues)
- Email: atulksin@gmail.com

## 🎯 Next Steps

1. **Explore Configuration**: Learn about [Configuration Options](Configuration)
2. **API Usage**: Check [API Documentation](API-Reference)
3. **Advanced Workflows**: Read [LangGraph Workflows](LangGraph-Workflows)
4. **Contribute**: See [Contributing Guidelines](Contributing)

Happy securing! 🔒
```

---

### Configuration Page
```markdown
# Configuration Reference

Complete configuration guide for Aegis Orchestrator.

## 🔧 Environment Variables

### Required Variables
```bash
PROJECT_ID="your-gcp-project-id"          # Google Cloud Project ID
REGION="us-central1"                      # GCP Region
GOOGLE_APPLICATION_CREDENTIALS="path"     # Service account key path
```

### Optional Variables
```bash
LOG_LEVEL="INFO"                          # Logging level
WORKSPACE_DIR="/tmp/aegis-workspace"      # Working directory
MAX_CONCURRENT_ANALYSES=5                 # Parallel processing limit
```

## ⚙️ Configuration Files

### config/settings.py
```python
# Model Configuration
MODEL_CONFIG = {
    "scanner": "gemini-pro",
    "researcher": "gemini-pro", 
    "fixer": "gemini-pro",
    "reviewer": "gemini-pro"
}

# Workflow Settings
WORKFLOW_CONFIG = {
    "max_retries": 3,
    "timeout_seconds": 1800,
    "enable_parallel": True
}
```

### Command Line Options
```bash
# Basic usage
python main.py [OPTIONS] REPO_URL

# Available options
--log-level {DEBUG,INFO,WARNING,ERROR}    # Set logging level
--dry-run                                 # Analysis only, no PRs
--list-vulnerabilities                    # Show supported types
--server                                  # Run as HTTP server
```

## 🎛️ Advanced Configuration

### Custom Vulnerability Types
Add custom vulnerability patterns in `config/vulnerabilities.yaml`:

```yaml
custom_vulnerabilities:
  - name: "Custom SQL Injection"
    cwe_id: "CWE-89"
    severity: "HIGH"
    patterns:
      - "SELECT.*FROM.*WHERE.*=.*\\$"
      - "INSERT.*INTO.*VALUES.*\\$"
```

### Model Fine-tuning
```python
# Custom model parameters
VERTEX_AI_CONFIG = {
    "temperature": 0.1,
    "max_output_tokens": 2048,
    "top_k": 40,
    "top_p": 0.8
}
```

Ready to configure your setup? Check the [API Reference](API-Reference) for more details!
```

---

### API Reference Page
```markdown
# API Reference

Complete API documentation for Aegis Orchestrator.

## 🌐 HTTP Server Mode

### Start Server
```bash
python main.py --server
```
Server runs on port 8080 (configurable via PORT environment variable).

### Endpoints

#### GET /health
Health check endpoint for load balancers.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET /
Service information page.

**Response:**
```html
<h1>Aegis Orchestrator</h1>
<p>AI-powered security automation platform</p>
```

#### POST /analyze
Analyze repository for security vulnerabilities.

**Request:**
```json
{
  "repo_url": "https://github.com/user/repo",
  "dry_run": false
}
```

**Response:**
```json
{
  "status": "success",
  "vulnerabilities_found": 5,
  "fixes_generated": 4,
  "pull_request": {
    "url": "https://github.com/user/repo/pull/123",
    "title": "Security fixes by Aegis Orchestrator"
  },
  "analysis_time": "120 seconds"
}
```

## 🐍 Python API

### OrchestratorApp Class

```python
from agents.orchestrator_app import OrchestratorApp

# Initialize
orchestrator = OrchestratorApp()

# Process repository
result = orchestrator.process_repository(
    repo_url="https://github.com/user/repo",
    dry_run=False
)
```

### Methods

#### process_repository()
Main method to analyze and fix vulnerabilities.

**Parameters:**
- `repo_url` (str): Repository URL to analyze
- `dry_run` (bool): If True, analysis only without creating PRs

**Returns:**
- `dict`: Analysis results and status

#### list_supported_vulnerability_types()
Get list of supported vulnerability types.

**Returns:**
- `dict`: Vulnerability categories and types

### Workflow API

```python
from agents.workflow import create_aegis_workflow, AegisState

# Create workflow
workflow = create_aegis_workflow()

# Initialize state
initial_state = AegisState(
    repo_url="https://github.com/user/repo",
    vulnerabilities=[],
    fixes=[],
    status="initialized"
)

# Execute workflow
result = workflow.invoke(initial_state)
```

Ready to integrate? Check our [examples](https://github.com/atulksin/Aegis-Orchestrator/tree/main/examples)!
```