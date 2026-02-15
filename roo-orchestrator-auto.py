#!/usr/bin/env python3
"""
Roo Code Orchestrator - FULLY AUTOMATED Version
Intelligently breaks down Jira tasks to avoid context window overload (200K tokens)
WITH automatic DevGPT Cline / Roo Code CLI execution!

This version can:
- Generate prompts (manual mode - original behavior)
- Execute automatically via Roo Code CLI
- Execute automatically via VS Code REST API (for DevGPT Cline extension)
"""

import argparse
import json
import subprocess
import sys
import os
import time
import re
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ExecutionMode(Enum):
    """How to execute phases"""
    MANUAL = "manual"           # Show prompts, user copies to DevGPT Cline
    ROO_CLI = "roo-cli"        # Execute via Roo Code CLI directly
    VSCODE_API = "vscode-api"  # Execute via VS Code REST API (DevGPT Cline)


class TaskType(Enum):
    FEATURE = "feature"
    BUG = "bug"
    SPIKE = "spike"


class ContextBudget:
    """Manages token budget allocation for different phases
    
    Based on DevGPT Cline best practices:
    - Be thoughtful about Max Tokens settings (every token allocated takes away from history)
    - Use high Max Tokens / Max Thinking Tokens for Architect and Debug modes
    - Keep Code mode at 16k max tokens or less for efficiency
    """
    TOTAL_BUDGET = 200_000
    
    # Reserve tokens for system/overhead
    SYSTEM_OVERHEAD = 30_000
    
    # Available for actual work
    AVAILABLE = TOTAL_BUDGET - SYSTEM_OVERHEAD
    
    # Per-phase budgets
    FEATURE_PHASES = {
        "analysis": 25_000,
        "planning": 20_000,
        "implementation": 60_000,
        "testing": 30_000,
        "documentation": 15_000,
        "review": 20_000
    }
    
    BUG_PHASES = {
        "reproduce": 20_000,
        "diagnosis": 40_000,
        "fix": 60_000,
        "testing": 30_000,
        "documentation": 20_000
    }
    
    SPIKE_PHASES = {
        "research": 50_000,
        "poc": 60_000,
        "analysis": 40_000,
        "recommendations": 20_000
    }
    
    # Mode recommendations (for use with DevGPT Cline)
    MODE_RECOMMENDATIONS = {
        "analysis": "Architect",
        "planning": "Architect",
        "implementation": "Code",
        "testing": "Debug",
        "documentation": "Code",
        "review": "Architect",
        "reproduce": "Debug",
        "diagnosis": "Debug",
        "fix": "Code",
        "research": "Architect",
        "poc": "Code"
    }


class AutomatedExecutor:
    """Handles automatic execution of prompts via various methods"""
    
    @staticmethod
    def execute_via_roo_cli(prompt: str, workspace: Path, timeout: int = 600) -> Tuple[bool, str]:
        """Execute prompt via Roo Code CLI
        
        Based on Roo CLI documentation:
        - Uses Deep AI Agent Architecture with built-in orchestration
        - Requires workspace to be set (opens in that directory)
        - Server-based, only one instance per workspace
        - May need retry if server doesn't connect
        
        Args:
            prompt: The prompt to execute
            workspace: Working directory (REQUIRED for Roo CLI)
            timeout: Max execution time in seconds
            
        Returns:
            (success, output) tuple
        """
        try:
            print("\n🤖 Executing via Roo CLI...")
            print(f"📁 Workspace: {workspace}")
            
            # Check if roo-cli is available
            cli_path = None
            possible_commands = ["roo-cli", "roo-code", "roo"]
            
            for cmd in possible_commands:
                check = subprocess.run(
                    ["which", cmd],
                    capture_output=True,
                    text=True
                )
                if check.returncode == 0:
                    cli_path = cmd
                    print(f"✓ Found Roo CLI: {cmd}")
                    break
            
            if not cli_path:
                return False, "Roo CLI not found. Install from: https://docs.roocode.com/cli/installation"
            
            # Prepare prompt file (Roo CLI can read from stdin)
            prompt_file = workspace / ".roo-temp-prompt.txt"
            with open(prompt_file, 'w') as f:
                f.write(prompt)
            
            print(f"⏳ Executing (timeout: {timeout}s)...")
            print("   Note: Roo CLI may take a moment to start server...")
            
            # Execute via Roo CLI with workspace set
            # Note: Roo CLI opens in current dir if no --setWorkspace
            result = subprocess.run(
                [cli_path],
                input=prompt,
                capture_output=True,
                text=True,
                cwd=workspace,  # Run from workspace directory
                timeout=timeout,
                env={**os.environ, 'ROO_WORKSPACE': str(workspace)}
            )
            
            # Clean up temp file
            if prompt_file.exists():
                prompt_file.unlink()
            
            if result.returncode == 0:
                print("✅ Execution successful!")
                return True, result.stdout
            else:
                error_msg = result.stderr or result.stdout
                
                # Check for common issues
                if "server" in error_msg.lower() and "connect" in error_msg.lower():
                    print("⚠️  Server connection issue detected")
                    print("💡 Tip: Try running 'roo-cli' again if this persists")
                    
                    # Auto-retry once
                    print("🔄 Retrying...")
                    result = subprocess.run(
                        [cli_path],
                        input=prompt,
                        capture_output=True,
                        text=True,
                        cwd=workspace,
                        timeout=timeout,
                        env={**os.environ, 'ROO_WORKSPACE': str(workspace)}
                    )
                    
                    if result.returncode == 0:
                        print("✅ Retry successful!")
                        return True, result.stdout
                
                print(f"⚠️  Execution completed with errors")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            if prompt_file.exists():
                prompt_file.unlink()
            return False, f"Execution timed out after {timeout} seconds. Roo CLI may be processing a large task."
        except Exception as e:
            if prompt_file.exists():
                prompt_file.unlink()
            return False, f"Execution error: {str(e)}"
    
    @staticmethod
    def execute_via_vscode_api(prompt: str, workspace: Path, mode: str = "Code") -> Tuple[bool, str]:
        """Execute prompt via VS Code REST API (for DevGPT Cline extension)
        
        This sends commands to VS Code's DevGPT Cline extension via REST API.
        Requires VS Code with DevGPT Cline extension running.
        
        Args:
            prompt: The prompt to execute
            workspace: Working directory
            mode: DevGPT Cline mode (Architect, Code, Debug)
            
        Returns:
            (success, output) tuple
        """
        try:
            import urllib.request
            import urllib.parse
            
            print(f"\n🤖 Executing via VS Code DevGPT Cline ({mode} mode)...")
            
            # VS Code REST API endpoint (default port)
            api_url = os.getenv("VSCODE_API_URL", "http://localhost:3000")
            
            # Create request to start new task in specified mode
            data = {
                "command": "devgpt.startNewTask",
                "mode": mode,
                "prompt": prompt,
                "workspace": str(workspace)
            }
            
            req = urllib.request.Request(
                f"{api_url}/api/command",
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get("success"):
                    task_id = result.get("taskId")
                    print(f"✅ Task started: {task_id}")
                    
                    # Poll for completion
                    max_wait = 600  # 10 minutes
                    interval = 5
                    elapsed = 0
                    
                    while elapsed < max_wait:
                        time.sleep(interval)
                        elapsed += interval
                        
                        # Check task status
                        status_req = urllib.request.Request(
                            f"{api_url}/api/task/{task_id}/status"
                        )
                        
                        with urllib.request.urlopen(status_req, timeout=10) as status_response:
                            status = json.loads(status_response.read().decode('utf-8'))
                            
                            if status.get("completed"):
                                print(f"✅ Task completed after {elapsed}s")
                                return True, status.get("output", "")
                            elif status.get("error"):
                                print(f"⚠️  Task failed: {status.get('error')}")
                                return False, status.get("error", "")
                        
                        print(f"⏳ Waiting... ({elapsed}s elapsed)")
                    
                    return False, f"Task timed out after {max_wait}s"
                else:
                    return False, result.get("error", "Unknown error")
                    
        except urllib.error.URLError as e:
            return False, f"VS Code API not available: {str(e)}. Is VS Code running with DevGPT Cline?"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
    
    @staticmethod
    def execute_manual(prompt: str) -> Tuple[bool, str]:
        """Show prompt for manual execution (original behavior)"""
        print("\n" + "="*60)
        print("PROMPT FOR DEVGPT CLINE / ROO CODE:")
        print("="*60)
        print(prompt)
        print("="*60)
        
        print("\n📋 Copy the above prompt and paste into DevGPT Cline")
        input("Press Enter when complete...")
        
        return True, "Manual execution completed"


class RooOrchestrator:
    def __init__(
        self, 
        jira_id: str, 
        task_type: TaskType, 
        workspace_dir: str = ".",
        execution_mode: ExecutionMode = ExecutionMode.MANUAL,
        max_tokens: int = 8192
    ):
        self.jira_id = jira_id
        self.task_type = task_type
        self.workspace_dir = Path(workspace_dir).resolve()
        self.execution_mode = execution_mode
        self.max_tokens = max_tokens
        self.state_file = self.workspace_dir / f".roo-state-{jira_id}.json"
        self.state = self._load_state()
        self.executor = AutomatedExecutor()
        
    def _load_state(self) -> Dict:
        """Load orchestrator state from disk"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "jira_id": self.jira_id,
            "task_type": self.task_type.value,
            "phases_completed": [],
            "current_phase": None,
            "artifacts": {},
            "execution_history": []
        }
    
    def _save_state(self):
        """Save orchestrator state to disk"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _get_phases(self) -> List[str]:
        """Get phases for current task type"""
        if self.task_type == TaskType.FEATURE:
            return list(ContextBudget.FEATURE_PHASES.keys())
        elif self.task_type == TaskType.BUG:
            return list(ContextBudget.BUG_PHASES.keys())
        else:  # SPIKE
            return list(ContextBudget.SPIKE_PHASES.keys())
    
    def _get_phase_budget(self, phase: str) -> int:
        """Get token budget for a specific phase"""
        if self.task_type == TaskType.FEATURE:
            return ContextBudget.FEATURE_PHASES.get(phase, 30_000)
        elif self.task_type == TaskType.BUG:
            return ContextBudget.BUG_PHASES.get(phase, 30_000)
        else:  # SPIKE
            return ContextBudget.SPIKE_PHASES.get(phase, 30_000)
    
    def _get_mode_recommendation(self, phase: str) -> str:
        """Get recommended DevGPT Cline mode for phase"""
        return ContextBudget.MODE_RECOMMENDATIONS.get(phase, "Code")
    
    def _create_phase_prompt(self, phase: str) -> str:
        """Create a focused prompt for the current phase"""
        budget = self._get_phase_budget(phase)
        mode = self._get_mode_recommendation(phase)
        
        # Calculate number of iterations based on user's maxTokens setting
        iterations = max(1, budget // self.max_tokens)
        
        # Common best practices footer
        best_practices = f"""
---
EXECUTION CONTEXT:
- Phase Budget: {budget:,} tokens total
- Your maxTokens: {self.max_tokens:,}
- Expected Iterations: ~{iterations}
- Recommended Mode: {mode}

DEVGPT CLINE BEST PRACTICES:
- This is a NEW task - fresh context window
- Focus ONLY on this phase
- Save results to artifact file (specified below)
- Next phase will read your artifacts
- If you need more space: save progress and we'll continue

TOKEN MANAGEMENT:
- Work incrementally within your {self.max_tokens:,} token limit
- Each response should make progress toward phase goal
- Use artifacts to preserve state between responses
- Don't try to do everything in one response

FILE MANAGEMENT:
- Drag relevant files into chat (hold Shift for multiple)
- Focus on files needed for THIS phase only
- Large files will be auto-truncated (your setting: 500 lines)
"""
        
        prompts = {
            # FEATURE PHASES
            "analysis": f"""PHASE 1/6: Requirements Analysis for {self.jira_id}

GOAL: Analyze requirements and create detailed breakdown

STEPS:
1. Review Jira ticket requirements for {self.jira_id}
2. Identify affected components/modules
3. List dependencies and prerequisites
4. Create implementation task breakdown
5. Save complete analysis to: .roo-artifacts/{self.jira_id}/01-analysis.md

OUTPUT FORMAT:
Create a markdown file with:
- Requirements summary
- Affected components list
- Dependencies
- Task breakdown
- Risk assessment

Keep output focused. Implementation will happen in later phases.{best_practices}""",
            
            "planning": f"""PHASE 2/6: Technical Planning for {self.jira_id}

GOAL: Create implementation plan based on analysis

INPUT: Read .roo-artifacts/{self.jira_id}/01-analysis.md

STEPS:
1. Design technical approach and architecture
2. Identify specific files to modify/create
3. Define interfaces and contracts
4. Plan testing strategy
5. Save plan to: .roo-artifacts/{self.jira_id}/02-plan.md

OUTPUT FORMAT:
Create a markdown file with:
- Architecture/design decisions
- Files to modify (with specific changes)
- New files to create
- Interface definitions
- Testing approach

Be specific and actionable.{best_practices}""",
            
            "implementation": f"""PHASE 3/6: Implementation for {self.jira_id}

GOAL: Implement planned changes

INPUT: Read .roo-artifacts/{self.jira_id}/02-plan.md

STEPS:
1. Implement changes ONE module/component at a time
2. Follow the plan from previous phase
3. Test each change as you go
4. Document what you implemented
5. Update .roo-artifacts/{self.jira_id}/03-implementation.md with:
   - What was implemented
   - Files changed
   - Any deviations from plan
   - Issues encountered

IMPORTANT: 
- Work incrementally (you have ~{iterations} iterations)
- Save progress after each component
- Can call this phase multiple times if needed

If you hit a complex bug:
- Save your progress
- Note the issue in implementation.md
- We can start a separate debug task{best_practices}""",
            
            "testing": f"""PHASE 4/6: Testing for {self.jira_id}

GOAL: Create and execute comprehensive tests

INPUT: Read .roo-artifacts/{self.jira_id}/03-implementation.md

STEPS:
1. Create unit tests for new/modified functions
2. Create integration tests for workflows
3. Run all tests
4. Document results in: .roo-artifacts/{self.jira_id}/04-testing.md

OUTPUT FORMAT:
- Test files created
- Test coverage achieved
- Test results (pass/fail)
- Any issues found{best_practices}""",
            
            "documentation": f"""PHASE 5/6: Documentation for {self.jira_id}

GOAL: Document all changes

INPUTS: Read all previous artifacts

STEPS:
1. Update README if public APIs changed
2. Add/update inline code comments
3. Create/update API documentation
4. Document configuration changes
5. Save to: .roo-artifacts/{self.jira_id}/05-documentation.md

OUTPUT FORMAT:
- Documentation files updated
- Comments added
- README changes
- API docs updates{best_practices}""",
            
            "review": f"""PHASE 6/6: Review and Cleanup for {self.jira_id}

GOAL: Final review before completion

INPUTS: Read all previous artifacts

STEPS:
1. Review all code changes for quality
2. Check test coverage is adequate
3. Verify documentation is complete
4. Look for edge cases missed
5. Create summary in: .roo-artifacts/{self.jira_id}/06-review.md

OUTPUT FORMAT:
- Code quality assessment
- Coverage review
- Completeness check
- Recommendations for next steps
- Final summary{best_practices}""",
            
            # BUG PHASES
            "reproduce": f"""PHASE 1/5: Bug Reproduction for {self.jira_id}

GOAL: Create minimal reproduction case

STEPS:
1. Review bug report for {self.jira_id}
2. Create minimal code to reproduce
3. Document exact steps to reproduce
4. Capture error messages/stack traces
5. Save to: .roo-artifacts/{self.jira_id}/01-reproduction.md

OUTPUT FORMAT:
- Bug description
- Reproduction steps
- Expected vs actual behavior
- Stack traces / error messages
- Environment details

TIP: If bug is complex, consider creating a custom mode based on the bug domain.{best_practices}""",
            
            "diagnosis": f"""PHASE 2/5: Bug Diagnosis for {self.jira_id}

GOAL: Identify root cause

INPUT: Read .roo-artifacts/{self.jira_id}/01-reproduction.md

STEPS:
1. Analyze stack traces and error messages
2. Trace code execution path
3. Identify the faulty code section
4. Determine why it's failing
5. Save analysis to: .roo-artifacts/{self.jira_id}/02-diagnosis.md

OUTPUT FORMAT:
- Root cause identified
- Faulty code location
- Why it's failing
- Proposed fix approach
- Potential side effects

TIP: Use Debug mode with high tokens for deep analysis.
If context gets too large, save findings and start fresh.{best_practices}""",
            
            "fix": f"""PHASE 3/5: Bug Fix Implementation for {self.jira_id}

GOAL: Implement the fix

INPUT: Read .roo-artifacts/{self.jira_id}/02-diagnosis.md

STEPS:
1. Implement the fix as planned
2. Ensure changes are minimal and focused
3. Add tests to prevent regression
4. Verify fix works
5. Document in: .roo-artifacts/{self.jira_id}/03-fix.md

OUTPUT FORMAT:
- Fix implemented
- Files changed
- Tests added
- Verification results{best_practices}""",
            
            # SPIKE PHASES  
            "research": f"""PHASE 1/4: Research for {self.jira_id}

GOAL: Research and gather information

STEPS:
1. Research technologies/approaches for {self.jira_id}
2. Review relevant documentation
3. Analyze tradeoffs of different approaches
4. Gather code examples if relevant
5. Save to: .roo-artifacts/{self.jira_id}/01-research.md

OUTPUT FORMAT:
- Options identified
- Pros/cons of each
- Technical feasibility
- Code examples
- Recommendations for POC{best_practices}""",
            
            "poc": f"""PHASE 2/4: Proof of Concept for {self.jira_id}

GOAL: Build minimal POC to validate approach

INPUT: Read .roo-artifacts/{self.jira_id}/01-research.md

STEPS:
1. Implement minimal POC for recommended approach
2. Test feasibility and performance
3. Document findings
4. Save to: .roo-artifacts/{self.jira_id}/02-poc.md

OUTPUT FORMAT:
- POC implementation
- Test results
- Performance metrics
- Issues encountered
- Lessons learned

TIP: Consider parallel development - create multiple repo copies 
and run POCs in parallel for different approaches.{best_practices}""",
            
            "analysis": f"""PHASE 3/4: Analysis for {self.jira_id}

GOAL: Analyze POC results

INPUT: Read .roo-artifacts/{self.jira_id}/02-poc.md

STEPS:
1. Evaluate POC results
2. Compare against requirements
3. Assess production readiness
4. Identify gaps and risks
5. Save to: .roo-artifacts/{self.jira_id}/03-analysis.md

OUTPUT FORMAT:
- POC evaluation
- Production readiness assessment
- Gaps identified
- Risks and mitigations{best_practices}""",
            
            "recommendations": f"""PHASE 4/4: Recommendations for {self.jira_id}

GOAL: Provide final recommendations

INPUTS: Read all previous artifacts

STEPS:
1. Summarize all findings
2. Provide clear recommendation
3. Estimate implementation effort
4. Outline next steps
5. Save to: .roo-artifacts/{self.jira_id}/04-recommendations.md

OUTPUT FORMAT:
- Executive summary
- Recommendation (with rationale)
- Effort estimate
- Implementation roadmap
- Risks and dependencies{best_practices}"""
        }
        
        return prompts.get(phase, f"Execute phase: {phase}")
    
    def run_phase(self, phase: str, auto: bool = True) -> bool:
        """Execute a single phase
        
        Args:
            phase: Phase name to execute
            auto: If False, always use manual mode regardless of execution_mode
        """
        mode = self._get_mode_recommendation(phase)
        budget = self._get_phase_budget(phase)
        
        print(f"\n{'='*70}")
        print(f"PHASE: {phase.upper()}")
        print(f"Task Type: {self.task_type.value}")
        print(f"Token Budget: {budget:,}")
        print(f"Recommended Mode: {mode}")
        print(f"Execution: {self.execution_mode.value if auto else 'manual'}")
        print(f"{'='*70}\n")
        
        # Create artifacts directory
        artifacts_dir = self.workspace_dir / ".roo-artifacts" / self.jira_id
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Get phase prompt
        prompt = self._create_phase_prompt(phase)
        
        # Save instruction file
        instruction_file = artifacts_dir / f"phase-{phase}-instructions.txt"
        with open(instruction_file, 'w') as f:
            f.write(prompt)
        print(f"📝 Instructions saved to: {instruction_file}")
        
        # Execute based on mode
        success = False
        output = ""
        
        if not auto or self.execution_mode == ExecutionMode.MANUAL:
            success, output = self.executor.execute_manual(prompt)
        elif self.execution_mode == ExecutionMode.ROO_CLI:
            success, output = self.executor.execute_via_roo_cli(
                prompt, 
                self.workspace_dir
            )
        elif self.execution_mode == ExecutionMode.VSCODE_API:
            success, output = self.executor.execute_via_vscode_api(
                prompt,
                self.workspace_dir,
                mode
            )
        
        # Save execution history
        self.state["execution_history"].append({
            "phase": phase,
            "timestamp": time.time(),
            "mode": mode,
            "success": success,
            "execution_mode": self.execution_mode.value if auto else "manual",
            "output_length": len(output)
        })
        
        # Save output if available
        if output:
            output_file = artifacts_dir / f"phase-{phase}-output.txt"
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"💾 Output saved to: {output_file}")
        
        if success:
            # Update state
            self.state["phases_completed"].append(phase)
            self.state["current_phase"] = phase
            self._save_state()
            print(f"\n✅ Phase '{phase}' completed successfully!")
            return True
        else:
            print(f"\n⚠️  Phase '{phase}' completed with issues")
            print(f"Output: {output[:500]}...")
            
            retry = input("\nRetry this phase? (y/n): ").strip().lower()
            if retry == 'y':
                return self.run_phase(phase, auto)
            
            skip = input("Skip and continue? (y/n): ").strip().lower()
            if skip == 'y':
                self.state["phases_completed"].append(phase)
                self.state["current_phase"] = phase
                self._save_state()
                return True
            
            return False
    
    def run_all(self, auto: bool = True):
        """Execute all phases for the task"""
        phases = self._get_phases()
        
        print(f"\n🚀 Starting {'AUTOMATED' if auto and self.execution_mode != ExecutionMode.MANUAL else 'MANUAL'} Orchestrator")
        print(f"Task: {self.jira_id}")
        print(f"Type: {self.task_type.value}")
        print(f"Phases: {len(phases)}")
        print(f"Execution Mode: {self.execution_mode.value if auto else 'manual'}")
        print(f"Max Tokens: {self.max_tokens:,}")
        
        start_time = time.time()
        
        for i, phase in enumerate(phases, 1):
            if phase in self.state["phases_completed"]:
                print(f"\n✓ Phase {i}/{len(phases)}: {phase} (already completed)")
                continue
            
            print(f"\n▶️  Phase {i}/{len(phases)}: {phase}")
            
            if not self.run_phase(phase, auto):
                print("\n⚠️  Orchestration stopped")
                return False
        
        elapsed = time.time() - start_time
        print(f"\n✅ All phases completed for {self.jira_id}!")
        print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
        return True
    
    def status(self):
        """Show current status"""
        phases = self._get_phases()
        completed = self.state["phases_completed"]
        
        print(f"\n📊 Status for {self.jira_id}")
        print(f"Task Type: {self.task_type.value}")
        print(f"Progress: {len(completed)}/{len(phases)} phases")
        print(f"Execution Mode: {self.execution_mode.value}")
        print("\nPhases:")
        
        for phase in phases:
            status = "✓" if phase in completed else "○"
            budget = self._get_phase_budget(phase)
            mode = self._get_mode_recommendation(phase)
            print(f"  {status} {phase:15} ({budget:,} tokens, {mode} mode)")
        
        # Show execution history
        if self.state.get("execution_history"):
            print("\n📜 Execution History:")
            for entry in self.state["execution_history"][-5:]:  # Last 5
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry["timestamp"]))
                status_icon = "✅" if entry["success"] else "⚠️"
                print(f"  {status_icon} {entry['phase']:15} {timestamp} ({entry['execution_mode']})")
    
    def reset(self):
        """Reset orchestrator state"""
        if self.state_file.exists():
            self.state_file.unlink()
        print(f"✓ Reset state for {self.jira_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Roo Code Orchestrator - FULLY AUTOMATED task management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # AUTOMATED EXECUTION (via Roo Code CLI)
  python roo-orchestrator-auto.py --jira PROJ-123 --type feature --execution-mode roo-cli
  
  # AUTOMATED via VS Code DevGPT Cline API
  python roo-orchestrator-auto.py --jira PROJ-123 --type feature --execution-mode vscode-api
  
  # MANUAL (original behavior - show prompts)
  python roo-orchestrator-auto.py --jira PROJ-123 --type feature --execution-mode manual
  python roo-orchestrator-auto.py --jira PROJ-123 --type feature  # manual is default
  
  # Set your maxTokens setting
  python roo-orchestrator-auto.py --jira PROJ-123 --type feature --max-tokens 8192
  
  # Check status
  python roo-orchestrator-auto.py --jira PROJ-123 --status
  
  # Run specific phase
  python roo-orchestrator-auto.py --jira PROJ-123 --phase implementation
        """
    )
    
    parser.add_argument("--jira", required=True, help="Jira ticket ID")
    parser.add_argument(
        "--type",
        choices=["feature", "bug", "spike"],
        help="Task type (required for new tasks)"
    )
    parser.add_argument("--workspace", default=".", help="Workspace directory")
    parser.add_argument("--phase", help="Run specific phase")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--reset", action="store_true", help="Reset state")
    parser.add_argument(
        "--execution-mode",
        choices=["manual", "roo-cli", "vscode-api"],
        default="manual",
        help="How to execute phases (default: manual)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=8192,
        help="Your DevGPT Cline maxTokens setting (default: 8192)"
    )
    parser.add_argument(
        "--no-auto",
        action="store_true",
        help="Disable auto-execution (use manual mode)"
    )
    
    args = parser.parse_args()
    
    # Determine execution mode
    exec_mode = ExecutionMode(args.execution_mode)
    
    # Determine task type
    orchestrator = None
    state_file = Path(args.workspace) / f".roo-state-{args.jira}.json"
    
    if state_file.exists() and not args.type:
        # Load from existing state
        with open(state_file, 'r') as f:
            state = json.load(f)
            task_type = TaskType(state["task_type"])
            orchestrator = RooOrchestrator(
                args.jira, 
                task_type, 
                args.workspace,
                exec_mode,
                args.max_tokens
            )
    elif args.type:
        task_type = TaskType(args.type)
        orchestrator = RooOrchestrator(
            args.jira, 
            task_type, 
            args.workspace,
            exec_mode,
            args.max_tokens
        )
    else:
        print("Error: --type required for new tasks")
        sys.exit(1)
    
    # Execute commands
    if args.reset:
        orchestrator.reset()
    elif args.status:
        orchestrator.status()
    elif args.phase:
        orchestrator.run_phase(args.phase, not args.no_auto)
    else:
        orchestrator.run_all(not args.no_auto)


if __name__ == "__main__":
    main()
