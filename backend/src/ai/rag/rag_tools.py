"""
RAG Tools - Wrapper for RAG search to be used by agents

Provides a clean interface for agents to query knowledge base.
"""
from typing import Dict, Any, List, Optional
import asyncio

from src.ai.rag.retriever import KnowledgeRetriever, get_knowledge_retriever, RetrievalResult
from src.utils.logger import logger


class RAGTools:
    """
    RAG Tools for agents.

    CHỈ dùng cho knowledge/policy queries.
    KHÔNG dùng cho realtime data.
    """

    # Patterns that indicate a RAG query (knowledge/policy, not realtime)
    KNOWLEDGE_PATTERNS = [
        # General knowledge
        r"nhà\s+xe",
        r"tuyến\s+nào",
        r"có\s+tuyến",
        r"thông\s+tin\s+nhà\s+xe",

        # Policy queries
        r"chính\s+sách",
        r"quy\s+trình",
        r"điều\s+kiện",
        r"phí",
        r"hoàn\s+tiền",
        r"hủy\s+vé",
        r"thanh\s+toán",
        r"đặt\s+vé",

        # Information queries (not specific booking/seat)
        r"làm\s+sao",
        r"như\s+thế\s+nào",
        r"thế\s+nào",
        r"bao\s+lâu",
        r"cần\s+gì",
        r"phải\s+làm\s+gì",
        r"ở\s+đâu",
        r"điểm\s+đón",
        r"điểm\s+trả",
        r"hỗ\s+trợ",
        r"liên\s+hệ",

        # FAQ type questions
        r"câu\s+hỏi",
        r"faq",
        r"thường\s+gặp",

        # Location queries
        r"thuộc\s+tỉnh",
        r"thuộc\s+huyện",
        r"khu\s+vực",
    ]

    # Patterns that indicate REALTIME data (should NOT use RAG)
    REALTIME_PATTERNS = [
        r"còn\s+\d+\s*ghế",
        r"còn\s+mấy\s*ghế",
        r"còn\s+bao\s*nhiêu\s*ghế",
        r"ghế\s+cụ\s+thể",
        r"booking\s+[a-z0-9]+",
        r"bk\d+",
        r"mã\s+booking",
        r"trạng\s+thái\s+vé",
        r"trạng\s+thái\s+booking",
        r"thanh\s+toán\s+chưa",
        r"đã\s+thanh\s+toán",
        r"chuyến\s+\d+",
        r"ngày\s+\d+/\d+/\d+",
    ]

    def __init__(self):
        self.retriever: Optional[KnowledgeRetriever] = None
        self._initialized = False

    def initialize(self):
        """Initialize RAG index"""
        if self._initialized:
            return

        try:
            self.retriever = get_knowledge_retriever()
            self.retriever.initialize()
            self._initialized = True
            logger.info("RAGTools initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAGTools: {e}")
            self.retriever = None

    def should_use_rag(self, message: str) -> bool:
        """
        Determine if RAG should be used for this query.

        Args:
            message: User message

        Returns:
            True if RAG should be used, False if not
        """
        import re
        message_lower = message.lower()

        # Check if it looks like a realtime query - if yes, don't use RAG
        for pattern in self.REALTIME_PATTERNS:
            if re.search(pattern, message_lower):
                logger.info(f"RAG check: '{message[:50]}...' -> REALTIME (matched pattern: {pattern})")
                return False

        # Check if it looks like a knowledge query - if yes, use RAG
        for pattern in self.KNOWLEDGE_PATTERNS:
            if re.search(pattern, message_lower):
                logger.info(f"RAG check: '{message[:50]}...' -> KNOWLEDGE (matched pattern: {pattern})")
                return True

        return False

    def search_knowledge(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Search knowledge base.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            Search results with context
        """
        if not self._initialized:
            self.initialize()

        if self.retriever is None:
            return {
                "success": False,
                "status": "RAG_NOT_AVAILABLE",
                "response": "Hệ thống knowledge hiện không khả dụng.",
                "results": []
            }

        try:
            result = self.retriever.search_with_context(query, top_k=top_k)
            return result
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return {
                "success": False,
                "status": "RAG_ERROR",
                "response": "Đã có lỗi khi truy vấn knowledge base.",
                "error": str(e),
                "results": []
            }

    def format_response(
        self,
        query: str,
        result: Dict[str, Any],
        include_source: bool = True
    ) -> str:
        """
        Format RAG results into a readable response.

        Args:
            query: Original query
            result: RAG search result
            include_source: Whether to include source citation

        Returns:
            Formatted response string
        """
        if not result.get("success"):
            if result.get("status") == "NO_KNOWLEDGE":
                return "Tôi chưa tìm thấy thông tin phù hợp trong dữ liệu của nhà xe."
            return result.get("response", "Đã có lỗi khi truy vấn.")

        context = result.get("context", "")
        sources = result.get("sources", [])

        response = context

        if include_source and sources:
            source_list = [f"- {s['source']}" for s in sources]
            unique_sources = list(dict.fromkeys(source_list))  # Remove duplicates
            response += "\n\n**Nguồn:**\n" + "\n".join(unique_sources)

        return response

    def get_policy_for_refund(
        self,
        booking_amount: float = None
    ) -> Dict[str, Any]:
        """
        Get refund policy information.

        Args:
            booking_amount: Optional booking amount for calculations

        Returns:
            Refund policy context
        """
        result = self.search_knowledge("chính sách hoàn tiền điều kiện hủy vé phí", top_k=3)
        return result

    def get_booking_policy(self) -> Dict[str, Any]:
        """Get booking policy"""
        return self.search_knowledge("chính sách đặt vé quy trình", top_k=3)

    def get_faq_answer(self, question: str) -> Dict[str, Any]:
        """
        Get FAQ answer for a question.

        Args:
            question: User question

        Returns:
            FAQ answer
        """
        return self.search_knowledge(question, top_k=3)


# Singleton instance
_rag_tools = None


def get_rag_tools() -> RAGTools:
    """Get singleton RAG tools instance"""
    global _rag_tools
    if _rag_tools is None:
        _rag_tools = RAGTools()
        _rag_tools.initialize()
    return _rag_tools
