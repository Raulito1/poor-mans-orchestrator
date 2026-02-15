# Roo CLI Integration Guide

Complete guide for using the orchestrator with Roo CLI's Deep AI Agent Architecture.

---

## 🎯 Why Roo CLI + Orchestrator is Perfect

### **Two-Level Orchestration**

Your orchestrator provides **MACRO orchestration** (Jira → Phases):
```
JIRA-123 (Feature)
├─ Phase 1: Analysis (25K tokens)
├─ Phase 2: Planning (20K tokens)
├─ Phase 3: Implementation (60K tokens)
├─ Phase 4: Testing (30K tokens)
├─ Phase 5: Documentation (15K tokens)
└─ Phase 6: Review (20K tokens)
```

Roo CLI provides **MICRO orchestration** (Phase → Sub-tasks):
```
Phase 3: Implementation
├─ Planning: Break down into sub-tasks
├─ Orchestrator: Delegate to specialized agents
│  ├─ Coder agent: Write core module
│  ├─ Search agent: Find dependencies
│  └─ Verifier: Check quality
├─ Context Engineering: Learn patterns, avoid overload
└─ Verification: Quality checks
```

**Result:** Perfectly managed context at both levels! 🎉

---

## 🚀 Quick Start

### 1. Install Roo CLI

```bash
# Follow installation guide
# https://docs.roocode.com/cli/installation

# Verify installation
roo-cli --version
```

### 2. Set Up Workspace

```bash
# CRITICAL: Always specify workspace
export ROO_WORKSPACE=/path/to/your/project

# Or set it per-command
./roo-auto start PROJ-123 feature auto --workspace /path/to/your/project
```

### 3. Run Automated Orchestrator

```bash
chmod +x roo-auto

# Fully automated execution
./roo-auto start PROJ-123 feature auto

# Orchestrator will:
# 1. Generate phase prompts
# 2. Send to Roo CLI
# 3. Roo CLI uses Deep AI Agent Architecture
# 4. Results saved to artifacts
# 5. Automatically continues to next phase
```

---

## 🏗️ Architecture Integration

### **How It Works**

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Orchestrator                        │
│  • Breaks JIRA into phases                                  │
│  • Manages 200K context budget                              │
│  • Tracks state across phases                               │
│  • Generates focused prompts                                │
└─────────────────┬───────────────────────────────────────────┘
                  │ Sends prompt for Phase 1
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Roo CLI Server                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Planning Agent                                  │   │
│  │     • Structured, updatable task plans              │   │
│  │     • Living to-do list                             │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. Orchestrator & Sub-Agents                       │   │
│  │     • Central orchestrator manages delegation       │   │
│  │     • Specialized sub-agents (coder, search, etc.)  │   │
│  │     • Intelligent delegation                        │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  3. Context Retrieval & Memory                      │   │
│  │     • Stores work in external systems               │   │
│  │     • Hybrid memory (agent + semantic search)       │   │
│  │     • Prevents context overload                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4. Context Engineering                             │   │
│  │     • Learns complex patterns from data             │   │
│  │     • Specialized info without overloading          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  5. Verification                                    │   │
│  │     • Systematic checking of outputs                │   │
│  │     • Quality assurance at every step               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────┘
                  │ Returns results
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Artifact Storage                         │
│  .roo-artifacts/PROJ-123/01-analysis.md                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Complete Workflow Example

### **Feature Development: E-commerce Checkout**

```bash
# Setup
export ROO_WORKSPACE=/Users/you/projects/ecommerce
cd $ROO_WORKSPACE

# Start orchestrator
./roo-auto start SHOP-42 feature auto
```

**What happens:**

#### Phase 1: Analysis (Architect Mode, 25K tokens)
```
Orchestrator → Roo CLI:
"Analyze requirements for checkout redesign..."

Roo CLI:
├─ Planning Agent: Creates structured task plan
├─ Context Engineering: Learns checkout patterns from codebase
├─ Search Agent: Finds related checkout code
├─ Analysis: Breaks down requirements
└─ Verification: Checks analysis completeness

Output → .roo-artifacts/SHOP-42/01-analysis.md
```

#### Phase 2: Planning (Architect Mode, 20K tokens)
```
Orchestrator → Roo CLI:
"Read 01-analysis.md and create implementation plan..."

Roo CLI:
├─ Reads analysis artifact
├─ Planning Agent: Creates detailed plan
├─ Context Retrieval: Pulls relevant architecture docs
├─ Orchestrator: Breaks into sub-tasks
└─ Verification: Validates plan completeness

Output → .roo-artifacts/SHOP-42/02-plan.md
```

#### Phase 3: Implementation (Code Mode, 60K tokens)
```
Orchestrator → Roo CLI:
"Implement checkout changes per plan..."

Your maxTokens: 8192
Roo CLI breaks into ~8 iterations:

Iteration 1 (8192 tokens):
├─ Coder Agent: Implements CheckoutForm component
└─ Verification: Checks code quality

Iteration 2 (8192 tokens):
├─ Coder Agent: Implements payment validation
└─ Verification: Checks validation logic

Iteration 3 (8192 tokens):
├─ Coder Agent: Implements order submission
└─ Verification: Checks error handling

... continues for ~8 iterations ...

Output → .roo-artifacts/SHOP-42/03-implementation.md
```

#### Phase 4: Testing (Debug Mode, 30K tokens)
```
Orchestrator → Roo CLI:
"Create tests for checkout implementation..."

Roo CLI:
├─ Reads implementation artifact
├─ Coder Agent: Creates unit tests
├─ Coder Agent: Creates integration tests
├─ Verification: Runs tests, checks coverage
└─ Quality Assurance: Validates test quality

Output → .roo-artifacts/SHOP-42/04-testing.md
```

#### Phase 5: Documentation (Code Mode, 15K tokens)
```
Orchestrator → Roo CLI:
"Document all checkout changes..."

Roo CLI:
├─ Reads all previous artifacts
├─ Coder Agent: Updates README
├─ Coder Agent: Adds inline comments
├─ Verification: Checks documentation completeness

Output → .roo-artifacts/SHOP-42/05-documentation.md
```

#### Phase 6: Review (Architect Mode, 20K tokens)
```
Orchestrator → Roo CLI:
"Final review of all checkout changes..."

Roo CLI:
├─ Planning Agent: Reviews against original plan
├─ Verification: Comprehensive quality check
├─ Context Retrieval: Compares with best practices
└─ Final Report: Summary and recommendations

Output → .roo-artifacts/SHOP-42/06-review.md
```

**Total Time:** ~60-90 minutes (fully automated!)

---

## ⚙️ Configuration Best Practices

### **Your Settings (Already Optimal!)**

```json
{
  "devgpt.performance.maxTokens": 8192,
  "devgpt.context.maxConcurrentFileReads": 3,
  "devgpt.files.autoTruncateThreshold": 500
}
```

**How orchestrator uses these:**

```python
# Phase: Implementation (60K budget)
# User maxTokens: 8192
# Iterations needed: 60000 / 8192 ≈ 7.3 → 8 iterations

# Prompt includes:
"""
EXECUTION CONTEXT:
- Phase Budget: 60,000 tokens total
- Your maxTokens: 8,192
- Expected Iterations: ~8
- Work incrementally within your 8,192 token limit
"""
```

### **Workspace Management**

**CRITICAL:** Always set workspace:

```bash
# Option 1: Environment variable (recommended)
export ROO_WORKSPACE=/path/to/project
./roo-auto start PROJ-123 feature auto

# Option 2: Command line flag
./roo-auto start PROJ-123 feature auto --workspace /path/to/project

# Option 3: Config file
echo "export ROO_WORKSPACE=/path/to/project" >> ~/.bashrc
source ~/.bashrc
```

**Why it matters:**
- Roo CLI opens in present working directory if not specified
- Setting workspace ensures consistent behavior
- Server associates with specific workspace

---

## 🚨 Common Issues & Solutions

### Issue 1: "Server doesn't connect"

From Roo CLI docs: *"Sometimes if server doesn't get connected, run roo-cli again"*

**Orchestrator handles this automatically:**
```python
# Auto-retry logic built-in
if "server" in error_msg and "connect" in error_msg:
    print("🔄 Retrying...")
    # Automatic retry once
```

**Manual retry:**
```bash
# If orchestrator fails, just run again
./roo-auto continue PROJ-123 auto
# Will retry from last phase
```

### Issue 2: "Cannot run multiple roo-cli agents"

From docs: *"You cannot run multiple roo-cli agents in multiple terminals"*

**Not an issue!** Orchestrator runs phases **sequentially**:
```bash
# Only ONE Roo CLI instance runs at a time
Phase 1 → Roo CLI → Complete
Phase 2 → Roo CLI → Complete
Phase 3 → Roo CLI → Complete
...
```

**Parallel tasks?** Use different workspaces:
```bash
# Terminal 1
cd /project-a
./roo-auto start PROJ-123 feature auto

# Terminal 2
cd /project-b
./roo-auto start PROJ-456 bug auto

# Each has its own Roo CLI server!
```

### Issue 3: "Workspace confusion"

From docs: *"Once opened, if you want to --setWorkspace to change working dir, you need to kill the server"*

**Solution:**
```bash
# Always start with correct workspace
./roo-auto start PROJ-123 feature auto --workspace /correct/path

# If you need to change workspace mid-task:
# 1. Stop orchestrator (Ctrl+C)
# 2. Kill Roo CLI server
pkill -f roo-cli

# 3. Restart with new workspace
./roo-auto continue PROJ-123 auto --workspace /new/path
```

### Issue 4: "Server takes time to start"

From docs: *"Sometimes if server does not get instantiated, use --startDelay to increase server acknowledgement time"*

**Orchestrator provides feedback:**
```
🤖 Executing via Roo CLI...
📁 Workspace: /path/to/project
⏳ Executing (timeout: 600s)...
   Note: Roo CLI may take a moment to start server...
```

**If consistently slow:**
```bash
# Increase timeout
# Edit orchestrator or wait longer
# Default: 600s (10 minutes) per phase
```

---

## 🎯 Optimization Tips

### 1. **Workspace Structure**

Organize for optimal Roo CLI access:
```
project/
├── src/                    # Source code
├── tests/                  # Tests
├── docs/                   # Documentation
├── .roo-artifacts/         # Orchestrator artifacts
│   └── PROJ-123/
│       ├── 01-analysis.md
│       ├── 02-plan.md
│       └── ...
└── .roo-state-PROJ-123.json  # Orchestrator state
```

### 2. **Artifact Usage**

Roo CLI's context memory + orchestrator artifacts = perfect combo:
```bash
# Phase 1: Analysis
# Roo CLI stores findings in memory + artifact file

# Phase 2: Planning
# Roo CLI retrieves from memory
# Also reads artifact for details
# Result: No context overload!
```

### 3. **Iteration Planning**

Match phase complexity to Roo CLI's capabilities:
```bash
# Simple phases (1-2 iterations)
- Analysis: Quick review
- Documentation: Add comments

# Medium phases (3-5 iterations)  
- Planning: Detailed design
- Testing: Create test suite

# Complex phases (7-10 iterations)
- Implementation: Build features
- Multiple components, integrations
```

### 4. **Verification Levels**

Two-level quality assurance:
```bash
# Roo CLI: Checks every sub-task
└─ Verification agent validates output

# Orchestrator: Checks every phase
└─ Verifies artifact created
└─ Offers retry if issues
```

---

## 📊 Performance Metrics

### **Expected Timing (per phase)**

| Phase | Budget | Iterations | Roo CLI Time | Total |
|-------|--------|------------|--------------|-------|
| Analysis | 25K | 3 | 2-3 min/iter | 6-9 min |
| Planning | 20K | 2-3 | 2-3 min/iter | 4-9 min |
| Implementation | 60K | 7-8 | 2-4 min/iter | 14-32 min |
| Testing | 30K | 4 | 2-3 min/iter | 8-12 min |
| Documentation | 15K | 2 | 2-3 min/iter | 4-6 min |
| Review | 20K | 3 | 2-3 min/iter | 6-9 min |

**Total for feature:** 42-77 minutes

**Factors affecting time:**
- Codebase complexity
- Test coverage requirements
- Network/API latency
- Roo CLI server performance

---

## 🎓 Advanced Patterns

### **Pattern 1: Iterative Implementation**

For very large features:
```bash
# Break implementation into sub-phases
./roo-auto run PROJ-123 implementation auto
# Implements Module A

./roo-auto run PROJ-123 implementation auto  
# Implements Module B

./roo-auto run PROJ-123 implementation auto
# Implements Module C

# Continue to testing
./roo-auto continue PROJ-123 auto
```

### **Pattern 2: Debug-Focused**

When hitting complex bugs:
```bash
# Main task
./roo-auto start PROJ-123 feature auto

# Hits bug in implementation phase
# Don't debug in main task!

# Start separate debug task
./roo-auto start PROJ-123-DEBUG bug auto
# Phases: reproduce → diagnosis → fix

# Fix complete, return to main
./roo-auto continue PROJ-123 auto
```

### **Pattern 3: Parallel Workspaces**

Speed up with parallel execution:
```bash
#!/bin/bash
# parallel-dev.sh

# Terminal 1: Feature A
(cd /project-a && ./roo-auto start FEAT-1 feature auto) &

# Terminal 2: Feature B
(cd /project-b && ./roo-auto start FEAT-2 feature auto) &

# Terminal 3: Bug fix
(cd /project-c && ./roo-auto start BUG-1 bug auto) &

wait
echo "All tasks complete!"
```

---

## 🔍 Monitoring & Debugging

### **Check Orchestrator Status**
```bash
./roo-auto status PROJ-123

# Shows:
# - Phases completed
# - Current phase
# - Execution history
# - Roo CLI execution times
```

### **Check Roo CLI Logs**
```bash
# Roo CLI logs location (varies by installation)
tail -f ~/.roo/logs/roo-cli.log

# Or check orchestrator output files
cat .roo-artifacts/PROJ-123/phase-implementation-output.txt
```

### **Live Monitoring**
```bash
# In one terminal: Run orchestrator
./roo-auto start PROJ-123 feature auto

# In another terminal: Watch progress
watch -n 5 './roo-auto status PROJ-123'
```

---

## ✅ Success Checklist

Before running automated orchestrator:

- [ ] Roo CLI installed (`roo-cli --version`)
- [ ] Workspace set (`echo $ROO_WORKSPACE`)
- [ ] In correct directory (`pwd` shows project root)
- [ ] No other Roo CLI instances running (`ps aux | grep roo-cli`)
- [ ] Orchestrator configured (`./roo-auto config`)
- [ ] Test setup (`./roo-auto test`)

---

## 🎉 Results

**Your workflow:**
```bash
# Old way (manual):
9:00 AM  - Start work on JIRA-123
12:00 PM - Still wrestling with context windows
3:00 PM  - Finally making progress
5:00 PM  - 70% done, exhausted

# New way (automated):
9:00 AM  - ./roo-auto start JIRA-123 feature auto
9:05 AM  - Go get coffee ☕
10:30 AM - Check status: 100% complete! ✅

Time saved: 6.5 hours → 1.5 hours = 77% reduction! 🎉
```

---

**Ready to run?**
```bash
./roo-auto start YOUR-JIRA feature auto
```

---

Made with ❤️ for efficient AI-assisted development with Roo CLI
