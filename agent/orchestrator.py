"""
agent/orchestrator.py - Core Agent Orchestrator for Agent01.

Implements the ReAct (Reasoning + Acting) execution loop:
1. SENSE / PERCEIVE: Builds state with current goal, available tools, and history.
2. THINK: LLM analyzes the situation and decides on a tool or finish action.
3. ACT: Executes the chosen Python tool via ToolRegistry.
4. OBSERVE: Feeds the tool output back into the loop for the next reasoning step.
"""

import json
import re
from typing import Dict, Any, Optional, List
from agent.llm import OllamaClient, LLMError
from agent.tool_registry import ToolRegistry


class Agent:
    """
    Autonomous task-automation agent orchestrator.
    """

    def __init__(
        self,
        llm: Optional[OllamaClient] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_steps: int = 5
    ) -> None:
        self.llm = llm or OllamaClient()
        self.tool_registry = tool_registry or ToolRegistry()
        self.max_steps = max_steps
        self.history: List[Dict[str, Any]] = []

    def run(self, goal: str) -> Dict[str, Any]:
        """
        Executes the agent's goal-driven loop.

        Args:
            goal: The objective the agent must fulfill.

        Returns:
            Dictionary containing goal status, steps taken, and final summary.
        """
        print(f"\n{'='*70}")
        print(f"[Agent01] Goal: '{goal}'")
        print(f"[Agent01] Registered Tools: {self.tool_registry.get_tool_names()}")
        print(f"[Agent01] Max Steps Allowed: {self.max_steps}")
        print(f"{'='*70}\n")

        self.history = []
        step = 0

        system_prompt = self._build_system_prompt()

        while step < self.max_steps:
            step += 1
            print(f"--- [Step {step}/{self.max_steps}] ---")

            # 1. PERCEIVE: Build state prompt
            user_prompt = self._build_user_prompt(goal, step)

            # 2. THINK: Request LLM reasoning & action selection
            try:
                raw_response = self.llm.generate(prompt=user_prompt, system=system_prompt)
            except LLMError as err:
                print(f"[Agent01 Error] LLM reasoning failed: {err}")
                return {
                    "success": False,
                    "error": str(err),
                    "steps": step,
                    "history": self.history
                }

            # Parse the structured decision from LLM output
            parsed_decision = self._parse_json_response(raw_response)
            if not parsed_decision:
                print(f"[Agent01 Warning] Could not parse JSON from model output:\n{raw_response}")
                self.history.append({
                    "step": step,
                    "thought": "Invalid JSON response",
                    "action": "none",
                    "observation": "Error: Output must be a valid JSON object with 'thought', 'action', and 'action_input'."
                })
                continue

            thought = parsed_decision.get("thought", "No thought provided.")
            action = parsed_decision.get("action", "")
            action_input = parsed_decision.get("action_input", {})

            # Ensure action_input is a dictionary
            if not isinstance(action_input, dict):
                action_input = {}

            print(f"Thought: {thought}")
            print(f"Action:  {action}")
            print(f"Inputs:  {action_input}")

            # 3. ACT & EVALUATE
            if action.lower() == "finish":
                summary = action_input.get("summary", thought)
                print(f"\n[Agent01] Goal accomplished at step {step}!")
                print(f"[Agent01] Final Summary:\n{summary}\n")
                return {
                    "success": True,
                    "summary": summary,
                    "steps": step,
                    "history": self.history
                }

            # 4. OBSERVE: Execute tool and capture observation
            observation = self.tool_registry.execute(action, **action_input)
            print(f"Observation from '{action}': {observation}\n")

            self.history.append({
                "step": step,
                "thought": thought,
                "action": action,
                "action_input": action_input,
                "observation": str(observation)
            })

        print(f"[Agent01] Reached max step limit ({self.max_steps}) without finishing.")
        return {
            "success": False,
            "error": "Max steps reached without finishing goal.",
            "steps": step,
            "history": self.history
        }

    def _build_system_prompt(self) -> str:
        """Constructs system prompt containing tool documentation and JSON schema."""
        tools_docs = self.tool_registry.get_prompt_descriptions()
        return (
            "You are Agent01, an autonomous task-automation agent running locally.\n"
            "You solve tasks by breaking down goals, using registered tools, observing "
            "their output, and verifying results.\n\n"
            "AVAILABLE TOOLS:\n"
            f"{tools_docs}\n"
            "- finish(summary: string): Call this when the goal has been achieved or answered.\n\n"
            "RULES:\n"
            "1. You MUST respond with a single valid JSON object and nothing else.\n"
            "2. Never make up tool names. Only use registered tools or 'finish'.\n"
            "3. After receiving tool observation, reason about the next step or conclude with 'finish'.\n"
            "4. If a goal specifies a condition or threshold: evaluate whether it is met. If the condition is NOT met, do NOT proceed with report/creation tools; call 'finish' and explain that the threshold was not reached.\n"
            "5. Once a created file is verified to exist, conclude immediately with 'finish'.\n\n"
            "JSON FORMAT:\n"
            "{\n"
            '  "thought": "Your internal step-by-step reasoning",\n'
            '  "action": "tool_name OR finish",\n'
            '  "action_input": {"param_name": "param_value"}\n'
            "}"
        )

    def _build_user_prompt(self, goal: str, step: int) -> str:
        """Constructs current execution context for the LLM."""
        history_text = ""
        if self.history:
            history_text = "EXECUTION HISTORY SO FAR:\n"
            for item in self.history:
                history_text += (
                    f"- Step {item['step']}:\n"
                    f"  Thought: {item['thought']}\n"
                    f"  Action: {item['action']}({item.get('action_input', {})})\n"
                    f"  Observation: {item['observation']}\n"
                )
            history_text += "\n"

        return (
            f"GOAL: {goal}\n\n"
            f"{history_text}"
            f"CURRENT STEP: {step}/{self.max_steps}\n"
            "What is your next action? Respond ONLY with a valid JSON object."
        )

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts and parses JSON from the LLM output."""
        cleaned = text.strip()

        # Handle ```json ... ``` markdown fence
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)
        else:
            # Fallback: Find outermost { and }
            first_brace = cleaned.find("{")
            last_brace = cleaned.rfind("}")
            if first_brace != -1 and last_brace != -1:
                cleaned = cleaned[first_brace : last_brace + 1]

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None
