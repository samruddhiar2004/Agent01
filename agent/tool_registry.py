"""
agent/tool_registry.py - Modular Tool System for Agent01.

This module allows Python functions to be registered as tools that the agent
can discover, understand, and safely invoke.
"""

from typing import Callable, Dict, Any, Optional
import inspect


class Tool:
    """Represents a single executable tool available to the agent."""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters_schema: Optional[Dict[str, str]] = None
    ) -> None:
        self.name = name
        self.description = description
        self.func = func
        self.parameters_schema = parameters_schema or {}

    def to_description_text(self) -> str:
        """Formats the tool's signature and purpose for LLM prompts."""
        params_str = ", ".join(
            f"{k}: {v}" for k, v in self.parameters_schema.items()
        ) or "None"
        return f"- {self.name}({params_str}): {self.description}"


class ToolRegistry:
    """
    Registry that stores, describes, and executes tools.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters_schema: Optional[Dict[str, str]] = None
    ) -> None:
        """Registers a new tool in the registry."""
        self._tools[name] = Tool(
            name=name,
            description=description,
            func=func,
            parameters_schema=parameters_schema
        )

    def has_tool(self, name: str) -> bool:
        """Checks if a tool exists."""
        return name in self._tools

    def get_tool_names(self) -> list[str]:
        """Returns a list of all registered tool names."""
        return list(self._tools.keys())

    def get_prompt_descriptions(self) -> str:
        """
        Generates a readable catalog of all available tools
        to inject into the LLM system prompt.
        """
        if not self._tools:
            return "No tools currently registered."
        return "\n".join(tool.to_description_text() for tool in self._tools.values())

    def execute(self, name: str, **kwargs) -> Any:
        """
        Safely invokes a registered tool by name with keyword arguments.

        Returns:
            The output of the tool or an error message if invocation fails.
        """
        if name not in self._tools:
            return f"Error: Tool '{name}' is not registered. Available tools: {self.get_tool_names()}"

        tool = self._tools[name]
        try:
            # Call the underlying function
            result = tool.func(**kwargs)
            return result
        except TypeError as err:
            return f"Error: Invalid arguments passed to tool '{name}': {err}"
        except Exception as err:
            return f"Error executing tool '{name}': {type(err).__name__}: {err}"
