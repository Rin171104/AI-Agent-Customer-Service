"""
Agent Executor - Runs the multi-agent workflow
"""
from typing import Dict, Any, Optional
import asyncio

from src.agent.state import AgentState
from src.agent.chief import ChiefAgent
from src.agent.booking import BookingAgent
from src.agent.complaint import ComplaintAgent
from src.agent.payment import PaymentAgent
from src.models.llm_client import LLMClient
from src.tools.booking_tools import BookingTools
from src.tools.payment_tools import PaymentTools
from src.tools.complaint_tools import ComplaintTools
from src.tools.search import SearchTool
from src.utils.logger import logger


class AgentExecutor:
    """
    Orchestrates the multi-agent workflow.

    Coordinates:
    - Agent initialization
    - State management
    - Workflow execution
    - Response synthesis
    """

    def __init__(self):
        # Initialize LLM client
        self.llm_client = LLMClient()

        # Initialize tools
        self.booking_tools = BookingTools()
        self.payment_tools = PaymentTools()
        self.complaint_tools = ComplaintTools()
        self.search_tool = SearchTool()

        # Initialize agents
        self.booking_agent = BookingAgent(
            llm_client=self.llm_client,
            booking_tools=self.booking_tools,
        )

        self.complaint_agent = ComplaintAgent(
            llm_client=self.llm_client,
            complaint_tools=self.complaint_tools,
        )

        self.payment_agent = PaymentAgent(
            llm_client=self.llm_client,
            payment_tools=self.payment_tools,
        )

        self.chief_agent = ChiefAgent(
            llm_client=self.llm_client,
            booking_agent=self.booking_agent,
            complaint_agent=self.complaint_agent,
            payment_agent=self.payment_agent,
        )

        logger.info("AgentExecutor initialized")

    async def execute(self, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the agent workflow for a user message.

        Args:
            message: User's message
            user_id: Optional user identifier

        Returns:
            Response dict with message, trace, and state
        """
        # Create or retrieve state
        state = AgentState(user_id=user_id)

        # Add user message to trace
        state.add_message("user", message)
        state.add_trace(
            agent="System",
            action="receive_message",
            status="received",
        )

        try:
            # Process through Chief Agent
            result = await self.chief_agent.process_request(message, state)

            # Add agent response to trace
            state.add_message("assistant", result.get("message", ""))
            state.add_trace(
                agent=result.get("agent", "Chief Agent"),
                action="process_request",
                status="completed",
                details=result,
            )

            return {
                "response": result.get("message", ""),
                "intent": result.get("intent"),
                "requires_human_approval": result.get("requires_human_approval", False),
                "pending_action": result.get("pending_action"),
                "agent_trace": state.agent_trace,
                "state": state.to_dict(),
            }

        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            state.add_trace(
                agent="System",
                action="error",
                status="failed",
                details={"error": str(e)},
            )

            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "intent": "error",
                "requires_human_approval": False,
                "agent_trace": state.agent_trace,
                "state": state.to_dict(),
            }

    async def execute_with_history(
        self,
        message: str,
        conversation_history: list,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute with conversation history.

        Args:
            message: User's message
            conversation_history: List of previous messages
            user_id: Optional user identifier

        Returns:
            Response dict with message, trace, and state
        """
        # Create state with conversation history
        state = AgentState(user_id=user_id)
        state.messages = conversation_history

        # Process through Chief Agent with history
        try:
            result = await self.chief_agent.process_request(message, state)

            return {
                "response": result.get("message", ""),
                "intent": result.get("intent"),
                "requires_human_approval": result.get("requires_human_approval", False),
                "agent_trace": state.agent_trace,
                "state": state.to_dict(),
            }

        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "intent": "error",
                "requires_human_approval": False,
                "agent_trace": state.agent_trace,
                "state": state.to_dict(),
            }

    async def get_agent_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an agent run by ID.

        Args:
            run_id: Run identifier

        Returns:
            Run data or None if not found
        """
        # TODO: Implement run storage/retrieval
        return None

    async def list_agent_runs(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> list:
        """
        List recent agent runs.

        Args:
            user_id: Filter by user
            limit: Maximum number of runs to return

        Returns:
            List of run summaries
        """
        # TODO: Implement run listing
        return []


# Singleton instance
_executor: Optional[AgentExecutor] = None


def get_executor() -> AgentExecutor:
    """Get or create the agent executor singleton."""
    global _executor
    if _executor is None:
        _executor = AgentExecutor()
    return _executor
