"""
Chief Agent - Orchestrator for the Multi-Agent System
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from src.agent.state import AgentState
from src.models.llm_client import LLMClient
from src.prompts.chief_prompts import CHIEF_SYSTEM_PROMPT, INTENT_CLASSIFICATION_PROMPT


@dataclass
class ChiefAgent:
    """
    Chief Agent acts as the orchestrator for the multi-agent system.

    Responsibilities:
    - Receive and parse customer requests
    - Detect intent (booking, complaint, payment, FAQ)
    - Delegate tasks to Specialist Agents
    - Track workflow state
    - Validate agent results
    - Trigger Human-in-the-Loop when required
    - Synthesize final response
    """

    llm_client: LLMClient
    booking_agent: Any = None
    complaint_agent: Any = None
    payment_agent: Any = None

    def __post_init__(self):
        self.name = "Chief Agent"

    async def process_request(
        self,
        message: str,
        state: AgentState
    ) -> Dict[str, Any]:
        """
        Main entry point for processing customer requests.

        Args:
            message: Customer's message
            state: Current workflow state

        Returns:
            Response dict with message, intent, and next action
        """
        # 1. Classify intent
        intent = await self._classify_intent(message, state)
        state.intent = intent

        # 2. Extract entities based on intent
        entities = await self._extract_entities(message, intent, state)
        state.update_context(entities)

        # 3. Delegate to appropriate agent
        result = await self._delegate_to_agent(intent, state)

        # 4. Validate result
        validation = await self._validate_result(result, state)

        # 5. Check if HITL is required
        if self._requires_human_approval(result, state):
            state.requires_human_approval = True
            return {
                "message": validation["message"],
                "intent": intent,
                "requires_human_approval": True,
                "pending_action": result,
            }

        return {
            "message": validation["message"],
            "intent": intent,
            "agent": intent,
            "requires_human_approval": False,
        }

    async def _classify_intent(self, message: str, state: AgentState) -> str:
        """Classify customer intent using LLM."""
        prompt = INTENT_CLASSIFICATION_PROMPT.format(message=message)
        response = await self.llm_client.generate(prompt)

        # Parse intent from response
        intent = response.strip().lower()

        # Map to standard intents
        if "booking" in intent or "đặt vé" in message.lower():
            return "booking"
        elif "complaint" in intent or "khiếu nại" in message.lower():
            return "complaint"
        elif "payment" in intent or "thanh toán" in message.lower():
            return "payment"
        elif "faq" in intent or "?" in message:
            return "faq"
        else:
            return "general"

    async def _extract_entities(
        self,
        message: str,
        intent: str,
        state: AgentState
    ) -> Dict[str, Any]:
        """Extract relevant entities from the message."""
        entities = {}

        if intent == "booking":
            # Extract booking-related entities
            prompt = f"""
Extract booking entities from: {message}
Return JSON with: origin, destination, date, time, quantity, passenger_name, phone
"""
            response = await self.llm_client.generate(prompt)
            # Parse response and update entities
            # TODO: Implement proper parsing

        return entities

    async def _delegate_to_agent(
        self,
        intent: str,
        state: AgentState
    ) -> Dict[str, Any]:
        """Delegate task to appropriate specialist agent."""
        if intent == "booking" and self.booking_agent:
            return await self.booking_agent.process(state)
        elif intent == "complaint" and self.complaint_agent:
            return await self.complaint_agent.process(state)
        elif intent == "payment" and self.payment_agent:
            return await self.payment_agent.process(state)

        # Fallback for FAQ or general queries
        return await self._handle_faq(state)

    async def _handle_faq(self, state: AgentState) -> Dict[str, Any]:
        """Handle FAQ or general queries using RAG."""
        # TODO: Implement RAG-based FAQ handling
        return {
            "action": "faq_response",
            "message": "I can help you with booking tickets, making complaints, and processing payments. How can I assist you today?",
        }

    async def _validate_result(
        self,
        result: Dict[str, Any],
        state: AgentState
    ) -> Dict[str, Any]:
        """Validate the result from specialist agent."""
        # TODO: Implement proper validation
        return {
            "valid": True,
            "message": result.get("message", ""),
        }

    def _requires_human_approval(
        self,
        result: Dict[str, Any],
        state: AgentState
    ) -> bool:
        """Check if human approval is required for this action."""
        # Actions that require human approval
        high_risk_actions = [
            "refund",
            "compensation",
            "cancel_special",
        ]

        action = result.get("action", "")
        return action in high_risk_actions
