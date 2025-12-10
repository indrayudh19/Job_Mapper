"""
Base agent class for the Job Discovery Pipeline.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the pipeline.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for logging and identification."""
        pass

    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        """
        Execute the agent's task.
        
        Args:
            input_data: Input from previous agent or initial query
            
        Returns:
            Output to pass to next agent
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
