# GitHub Issues Template

## Issue Templates for Aegis Orchestrator

### 1. Bug Report Template
```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug'
assignees: 'atulksin'

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment (please complete the following information):**
 - OS: [e.g. Windows, macOS, Linux]
 - Python Version: [e.g. 3.11]
 - Aegis Orchestrator Version: [e.g. 1.0.0]
 - Google Cloud Project ID: [if applicable]

**Additional context**
Add any other context about the problem here.

**Logs**
```
Paste relevant log output here
```
```

### 2. Feature Request Template
```markdown
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: 'enhancement'
assignees: 'atulksin'

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**Priority Level**
- [ ] Low
- [ ] Medium
- [ ] High
- [ ] Critical
```

### 3. Security Vulnerability Template
```markdown
---
name: Security Vulnerability
about: Report a security issue (please use private reporting for sensitive issues)
title: '[SECURITY] '
labels: 'security'
assignees: 'atulksin'

---

**⚠️ SECURITY NOTICE**
If this is a sensitive security issue, please report it privately via email to atulksin@gmail.com instead of creating a public issue.

**Vulnerability Description**
A clear description of the security vulnerability.

**Impact Assessment**
- [ ] Low Impact
- [ ] Medium Impact  
- [ ] High Impact
- [ ] Critical Impact

**Affected Components**
- [ ] AI Agents
- [ ] Workflow Engine
- [ ] Authentication
- [ ] API Endpoints
- [ ] Infrastructure
- [ ] Other: ___________

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Mitigation Suggestions**
Any suggestions for how to fix or mitigate this issue.
```

## Initial Issues to Create

### Issue #1: Documentation Improvement
**Title**: [FEATURE] Create comprehensive getting started guide
**Labels**: documentation, enhancement
**Body**:
```markdown
We need a comprehensive getting started guide for new users to quickly onboard with Aegis Orchestrator.

**Requirements:**
- [ ] Installation guide for different platforms
- [ ] Google Cloud setup instructions
- [ ] Configuration examples
- [ ] First workflow walkthrough
- [ ] Troubleshooting section

**Acceptance Criteria:**
- Documentation should be beginner-friendly
- Include code examples and screenshots
- Cover both local and cloud deployment
```

### Issue #2: Enhanced Vulnerability Detection
**Title**: [FEATURE] Add support for JavaScript/TypeScript vulnerability detection
**Labels**: enhancement, ai-models
**Body**:
```markdown
Expand the AI-powered vulnerability detection to support JavaScript and TypeScript codebases.

**Current Support:**
- Python
- General security patterns

**Requested Addition:**
- JavaScript/Node.js vulnerabilities
- TypeScript-specific issues
- NPM dependency scanning
- React/Angular framework vulnerabilities

**Priority**: High
```

### Issue #3: Performance Optimization
**Title**: [ENHANCEMENT] Optimize workflow performance for large repositories
**Labels**: performance, enhancement
**Body**:
```markdown
Large repositories (>1000 files) are experiencing slower analysis times.

**Current Performance:**
- Small repos (<100 files): ~2 minutes
- Large repos (>1000 files): ~15+ minutes

**Target Performance:**
- Large repos should complete in <10 minutes

**Proposed Solutions:**
- [ ] Parallel file processing
- [ ] Incremental analysis
- [ ] Smart file filtering
- [ ] Caching mechanisms
```