# Full Automation Guide - Roo Orchestrator

This guide explains how to use the **fully automated** version of the Roo Orchestrator that can execute phases automatically without manual copy-paste.

---

## 🤖 Automation Modes

The orchestrator supports three execution modes:

### 1. **Manual Mode** (Default - Original Behavior)
- Shows prompts for you to copy
- You paste into DevGPT Cline manually
- Safe, proven approach
- Best for: Learning, testing, complex tasks

### 2. **Roo CLI Mode** (Direct Execution)
- Executes via Roo Code CLI directly
- Fully automated
- No VS Code needed
- Best for: CI/CD, scripts, batch processing

### 3. **VS Code API Mode** (DevGPT Cline Integration)
- Integrates with VS Code DevGPT Cline extension
- Sends commands via REST API
- Automatic mode switching (Architect/Code/Debug)
- Best for: Interactive development, real-time feedback

---

## 🚀 Quick Start - Automated Execution

### Option 1: Via Roo Code CLI

```bash
# Install Roo Code CLI first (if not already)
# Follow: https://docs.roocode.com/cli/installation

# Run automated orchestrator
python roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --type feature \
  --execution-mode roo-cli \
  --max-tokens 8192
```

**What happens:**
1. Orchestrator generates phase prompt
2. Sends directly to Roo Code CLI
3. CLI executes using your auth
4. Results saved to artifacts
5. Automatically moves to next phase
6. Repeat until complete

### Option 2: Via VS Code DevGPT Cline API

```bash
# 1. Start VS Code with DevGPT Cline extension
# 2. Enable REST API in DevGPT Cline settings (if available)
# 3. Run orchestrator

python roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --type feature \
  --execution-mode vscode-api \
  --max-tokens 8192
```

**What happens:**
1. Orchestrator sends command to VS Code
2. DevGPT Cline starts new task in recommended mode
3. Executes phase automatically
4. Orchestrator polls for completion
5. Results saved to artifacts
6. Automatically moves to next phase

### Option 3: Manual Mode (Original)

```bash
python roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --type feature \
  --execution-mode manual
  
# Or just omit --execution-mode (manual is default)
python roo-orchestrator-auto.py --jira PROJ-123 --type feature
```

---

## ⚙️ Configuration

### Your DevGPT Cline Settings

The orchestrator needs to know your `maxTokens` setting to plan iterations:

```bash
# Your settings.json shows: "devgpt.performance.maxTokens": 8192
python roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --type feature \
  --max-tokens 8192  # Match your setting
```

**Why this matters:**
- Phase budget: 25,000 tokens (total for phase)
- Your maxTokens: 8,192 tokens (per response)
- Iterations needed: ~3-4 responses to complete phase
- Orchestrator plans accordingly!

### Environment Variables

For VS Code API mode:

```bash
# Set VS Code API URL (default: http://localhost:3000)
export VSCODE_API_URL="http://localhost:3000"

# Run orchestrator
python roo-orchestrator-auto.py --jira PROJ-123 --type feature --execution-mode vscode-api
```

---

## 📋 Complete Examples

### Example 1: Fully Automated Feature Development

```bash
# Start automated feature development
python roo-orchestrator-auto.py \
  --jira SHOP-42 \
  --type feature \
  --execution-mode roo-cli \
  --max-tokens 8192

# Orchestrator runs:
# Phase 1: analysis (Architect mode, 25K tokens)
# Phase 2: planning (Architect mode, 20K tokens)
# Phase 3: implementation (Code mode, 60K tokens) 
# Phase 4: testing (Debug mode, 30K tokens)
# Phase 5: documentation (Code mode, 15K tokens)
# Phase 6: review (Architect mode, 20K tokens)

# All automatic! Just wait for completion.
```

### Example 2: Automated Bug Fix

```bash
python roo-orchestrator-auto.py \
  --jira BUG-88 \
  --type bug \
  --execution-mode roo-cli \
  --max-tokens 8192

# Phases:
# 1. reproduce (Debug, 20K)
# 2. diagnosis (Debug, 40K)
# 3. fix (Code, 60K)
# 4. testing (Debug, 30K)
# 5. documentation (Code, 20K)
```

### Example 3: Research Spike

```bash
python roo-orchestrator-auto.py \
  --jira SPIKE-15 \
  --type spike \
  --execution-mode roo-cli \
  --max-tokens 8192

# Phases:
# 1. research (Architect, 50K)
# 2. poc (Code, 60K)
# 3. analysis (Architect, 40K)
# 4. recommendations (Architect, 20K)
```

### Example 4: Mixed Mode (Manual + Auto)

```bash
# Start with manual for complex phases
python roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --type feature \
  --phase analysis \
  --execution-mode manual

# Analysis done, switch to auto for implementation
python roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --phase implementation \
  --execution-mode roo-cli

# Continue automatically
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode roo-cli
```

---

## 🔧 Advanced Usage

### Retry Failed Phases

If a phase fails, the orchestrator asks if you want to retry:

```bash
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode roo-cli

# Phase 3 fails...
⚠️ Phase 'implementation' completed with issues
Output: Error executing...

Retry this phase? (y/n): y
# Automatically retries with same prompt

# Or skip:
Skip and continue? (y/n): y
# Marks as complete, moves to next phase
```

### Resume After Interruption

State is saved after each phase:

```bash
# Start task
python roo-orchestrator-auto.py --jira PROJ-123 --type feature --execution-mode roo-cli

# Interrupt (Ctrl+C) after phase 2
^C

# Later, resume from where you left off
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode roo-cli
# Automatically starts at phase 3!
```

### Check Status Anytime

```bash
python roo-orchestrator-auto.py --jira PROJ-123 --status

# Output shows:
# - Phases completed
# - Current phase
# - Execution mode used
# - History of last 5 executions
```

### Run Specific Phase Multiple Times

For large implementations:

```bash
# Run implementation phase 3 times (for different modules)
python roo-orchestrator-auto.py --jira PROJ-123 --phase implementation --execution-mode roo-cli
# Module A done

python roo-orchestrator-auto.py --jira PROJ-123 --phase implementation --execution-mode roo-cli
# Module B done

python roo-orchestrator-auto.py --jira PROJ-123 --phase implementation --execution-mode roo-cli
# Module C done

# Continue to next phase
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode roo-cli
```

---

## 🎯 Optimization Tips

### Matching Your Config

Your DevGPT Cline settings:
```json
{
  "devgpt.performance.maxTokens": 8192,
  "devgpt.performance.temperature": 0.1,
  "devgpt.context.maxConcurrentFileReads": 3,
  "devgpt.files.autoTruncateThreshold": 500
}
```

**Optimal orchestrator usage:**
```bash
python roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --type feature \
  --execution-mode roo-cli \
  --max-tokens 8192  # Matches your setting
```

**Why this works:**
- Implementation phase: 60K tokens budget
- Your maxTokens: 8192 per response
- Iterations: ~8 responses (60K / 8192 ≈ 7.3)
- Each response makes incremental progress
- Context never overloads!

### Performance Settings

For fastest execution:

```bash
# Use Roo CLI mode (no VS Code overhead)
python roo-orchestrator-auto.py \
  --jira PROJ-123 \
  --type feature \
  --execution-mode roo-cli \
  --max-tokens 16384  # Higher if your config allows

# Or run in parallel for multiple tasks
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode roo-cli &
python roo-orchestrator-auto.py --jira PROJ-456 --execution-mode roo-cli &
python roo-orchestrator-auto.py --jira PROJ-789 --execution-mode roo-cli &
wait
```

---

## 🔍 Monitoring & Debugging

### View Execution History

```bash
python roo-orchestrator-auto.py --jira PROJ-123 --status

# Shows:
📜 Execution History:
  ✅ analysis       2026-02-15 09:45:23 (roo-cli)
  ✅ planning       2026-02-15 09:52:11 (roo-cli)
  ⚠️ implementation 2026-02-15 10:15:44 (roo-cli)
  ✅ implementation 2026-02-15 10:28:33 (roo-cli)
  ✅ testing        2026-02-15 10:45:12 (roo-cli)
```

### Check Artifacts

All outputs are saved:

```bash
.roo-artifacts/PROJ-123/
├── phase-analysis-instructions.txt        # Prompt sent
├── phase-analysis-output.txt              # Execution output
├── 01-analysis.md                         # Actual artifact
├── phase-planning-instructions.txt
├── phase-planning-output.txt
├── 02-plan.md
└── ...
```

### Review Outputs

```bash
# View last phase output
cat .roo-artifacts/PROJ-123/phase-implementation-output.txt

# View actual artifact
cat .roo-artifacts/PROJ-123/03-implementation.md
```

---

## 🚨 Troubleshooting

### Problem: "Roo Code CLI not found"

**Solution:**
```bash
# Check if installed
which roo-code

# If not, install:
# https://docs.roocode.com/cli/installation

# Or try alternate names:
which roo
which roo-cli

# Or use manual mode:
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode manual
```

### Problem: "VS Code API not available"

**Solution:**
```bash
# 1. Check VS Code is running
ps aux | grep "Visual Studio Code"

# 2. Check DevGPT Cline extension is active
# Open VS Code → Extensions → DevGPT Cline should be enabled

# 3. Check REST API is enabled (if supported)
# VS Code Settings → search "DevGPT Cline REST API"

# 4. Or fall back to manual mode:
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode manual
```

### Problem: "Execution timed out"

**Solution:**
```bash
# Increase timeout in code, or split phase:
python roo-orchestrator-auto.py --jira PROJ-123 --phase implementation --execution-mode roo-cli
# Do part 1

python roo-orchestrator-auto.py --jira PROJ-123 --phase implementation --execution-mode roo-cli
# Do part 2
```

### Problem: "Context window exceeded"

**This shouldn't happen!** The orchestrator prevents this by design.

If it does:
1. Check your `--max-tokens` setting matches DevGPT Cline
2. Verify phase budgets in code
3. Use manual mode to inspect what's happening

---

## 🎓 Best Practices

### 1. Start with Manual Mode
```bash
# First time with new task type? Use manual to understand flow
python roo-orchestrator-auto.py --jira PROJ-123 --type feature --execution-mode manual

# Once comfortable, switch to auto
python roo-orchestrator-auto.py --jira PROJ-456 --type feature --execution-mode roo-cli
```

### 2. Match Your Config
```bash
# Always set --max-tokens to match your DevGPT Cline setting
# Your config: "devgpt.performance.maxTokens": 8192
python roo-orchestrator-auto.py ... --max-tokens 8192
```

### 3. Monitor Progress
```bash
# In another terminal, watch status
watch -n 10 "python roo-orchestrator-auto.py --jira PROJ-123 --status"
```

### 4. Use Appropriate Mode
```bash
# Interactive development → VS Code API mode
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode vscode-api

# CI/CD / batch → Roo CLI mode
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode roo-cli

# Learning / complex → Manual mode
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode manual
```

### 5. Parallel Execution for Speed
```bash
# Different tasks in parallel
python roo-orchestrator-auto.py --jira PROJ-123 --execution-mode roo-cli &
python roo-orchestrator-auto.py --jira PROJ-456 --execution-mode roo-cli &
python roo-orchestrator-auto.py --jira PROJ-789 --execution-mode roo-cli &
wait

echo "All tasks complete!"
```

---

## 📊 Performance Expectations

### Single Task Timing

Based on 8192 maxTokens setting:

| Phase Type | Budget | Iterations | Est. Time | Notes |
|------------|--------|------------|-----------|-------|
| Analysis | 25K | ~3 | 5-10 min | Research heavy |
| Planning | 20K | ~2-3 | 3-8 min | Design thinking |
| Implementation | 60K | ~7-8 | 15-30 min | Most time |
| Testing | 30K | ~4 | 8-15 min | Test creation |
| Documentation | 15K | ~2 | 3-7 min | Writing |
| Review | 20K | ~2-3 | 5-10 min | Evaluation |

**Total for feature:** ~40-80 minutes (fully automated!)

**Compare to manual:**
- Manual: 2-4 hours (context management, copy-paste, etc.)
- Automated: 40-80 minutes (hands-off!)
- **Time saved: 60-70%** 🎉

---

## 🎉 Success Stories

### Before (Manual):
```
9:00 AM - Start PROJ-123
9:15 AM - Context window overload, restart
9:45 AM - Finally complete analysis
10:00 AM - Copy-paste prompts for planning
10:30 AM - Context overload again
11:00 AM - Start implementation phase 1
12:30 PM - Lunch break, lose context
1:00 PM - Restart from checkpoint
3:00 PM - Finally complete implementation
4:00 PM - Still working on tests
5:00 PM - Give up, resume tomorrow
```

### After (Automated):
```bash
9:00 AM - Run orchestrator
python roo-orchestrator-auto.py --jira PROJ-123 --type feature --execution-mode roo-cli

# Go get coffee ☕

10:20 AM - All phases complete!
✅ Analysis
✅ Planning  
✅ Implementation
✅ Testing
✅ Documentation
✅ Review

Ready for PR! 🚀
```

---

## 🔮 Future Enhancements

Coming soon:
- [ ] Slack notifications on phase completion
- [ ] Jira integration (auto-update tickets)
- [ ] Metrics dashboard
- [ ] Multi-task orchestration
- [ ] Custom phase definitions
- [ ] LLM-based phase planning

---

## 📚 Additional Resources

- [README.md](README.md) - Full documentation
- [DEVGPT_CLINE_TIPS.md](DEVGPT_CLINE_TIPS.md) - DevGPT Cline best practices
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Cheat sheet

---

**Questions? Issues?**

Check the troubleshooting section or open an issue!

---

Made with ❤️ for efficient AI-assisted development
