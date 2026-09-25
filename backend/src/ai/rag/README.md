# RAG Knowledge Module

## Tổng quan

RAG (Retrieval Augmented Generation) Module cung cấp knowledge retrieval cho AI agents.

**Quan trọng**: RAG CHỈ dùng cho knowledge/FAQ/policy. KHÔNG dùng cho realtime data.

## Kiến trúc

```
Documents (.md)
    ↓
DocumentLoader
    ↓
MarkdownChunker (split by headings)
    ↓
EmbeddingsGenerator (sentence-transformers / TF-IDF)
    ↓
VectorStore (Chroma / simple numpy)
    ↓
KnowledgeRetriever
```

## Sử dụng

### Tìm kiếm knowledge

```python
from src.ai.rag import search_knowledge, KnowledgeRetriever

# Simple usage
result = await search_knowledge("Điều kiện hoàn tiền là gì?")

# Or use retriever directly
retriever = KnowledgeRetriever()
retriever.initialize()
results = retriever.search("Chính sách hủy vé")
```

### Response format

```python
{
    "success": True,
    "results": [
        {
            "content": "...",
            "source": "refund_policy.md",
            "document": "Chính Sách Hoàn Tiền",
            "section": "Điều kiện được hoàn tiền",
            "score": 0.87,
            "chunk_id": "refund_policy_0_abc123"
        }
    ],
    "context": "Formatted context for agent",
    "sources": [...],
    "count": 1
}
```

### NO_KNOWLEDGE fallback

```python
result = retriever.search_with_context("random query")
# Returns:
# {
#     "success": False,
#     "status": "NO_KNOWLEDGE",
#     "response": "Tôi chưa tìm thấy thông tin phù hợp..."
# }
```

## Cấu hình

| Biến | Mặc định | Mô tả |
|-------|----------|--------|
| `RAG_TOP_K` | 5 | Số kết quả trả về |
| `RAG_SCORE_THRESHOLD` | 0.3 | Ngưỡng similarity tối thiểu |

## Knowledge Documents

Documents được lưu trong `backend/data/knowledge/`:

| File | Mô tả |
|------|--------|
| `company.md` | Thông tin nhà xe |
| `routes.md` | Tuyến đường |
| `booking_policy.md` | Chính sách đặt vé |
| `cancellation_policy.md` | Chính sách hủy vé |
| `refund_policy.md` | Chính sách hoàn tiền |
| `payment_policy.md` | Chính sách thanh toán |
| `pickup_dropoff.md` | Điểm đón/trả |
| `faq.md` | Câu hỏi thường gặp |

## Security

- **Read-only**: RAG không modify database
- **No business logic**: Không gọi booking/refund APIs
- **Prompt injection protection**: Sanitize query trước khi search
- **Citation**: Mỗi result có source để verify

## Prompt Injection Protection

```python
# Khi query:
"Điều kiện hoàn tiền? Ignore previous instructions"

# Sau sanitize:
"Điều kiện hoàn tiền?"
```

## Dependencies

- `sentence-transformers`: Embedding model (paraphrase-multilingual-MiniLM-L12-v2)
- `chromadb`: Vector store (optional, fallback to numpy)
- `numpy`: Fallback embeddings

## Tests

```bash
pytest tests/test_rag.py -v
```
