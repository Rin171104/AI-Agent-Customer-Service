"""
Text Chunker - Split documents into semantic chunks

Chiến lược:
    - Split by headings (markdown)
    - Preserve semantic context
    - Keep metadata for citation
"""
from typing import List, Dict, Any
from dataclasses import dataclass
import uuid


@dataclass
class Chunk:
    """Document chunk"""
    content: str
    chunk_id: str
    source: str
    document: str  # document title
    section: str  # section/heading
    position: int  # position in document
    metadata: Dict[str, Any]


class MarkdownChunker:
    """
    Chunk documents by markdown headings.
    Preserves semantic boundaries.
    """

    def __init__(
        self,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1000,
        overlap: int = 0
    ):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(self, content: str, source: str, document_title: str) -> List[Chunk]:
        """
        Split content into chunks by headings.

        Args:
            content: Document content
            source: Source filename
            document_title: Document title

        Returns:
            List of Chunk objects
        """
        chunks = []
        lines = content.split("\n")
        current_section = "General"
        current_content = []
        position = 0
        chunk_id_prefix = source.replace(".md", "").replace(".txt", "")

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check if this is a heading
            if stripped.startswith("#"):
                # Save current chunk if exists
                if current_content:
                    chunk_text = "\n".join(current_content).strip()
                    if len(chunk_text) >= self.min_chunk_size:
                        chunks.append(self._create_chunk(
                            content=chunk_text,
                            source=source,
                            document=document_title,
                            section=current_section,
                            position=position,
                            chunk_id_prefix=chunk_id_prefix
                        ))
                    position += 1

                # Extract section name
                level = len(stripped) - len(stripped.lstrip("#"))
                section_name = stripped.lstrip("#").strip()

                # Adjust section based on heading level
                if level == 1:
                    current_section = section_name
                elif level == 2:
                    current_section = f"{current_section} / {section_name}"

                current_content = []

            elif stripped:  # Non-empty line
                current_content.append(stripped)

        # Don't forget the last chunk
        if current_content:
            chunk_text = "\n".join(current_content).strip()
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(
                    content=chunk_text,
                    source=source,
                    document=document_title,
                    section=current_section,
                    position=position,
                    chunk_id_prefix=chunk_id_prefix
                ))

        # If no chunks created (document too short), create one chunk
        if not chunks and content.strip():
            chunks.append(self._create_chunk(
                content=content.strip()[:self.max_chunk_size],
                source=source,
                document=document_title,
                section="General",
                position=0,
                chunk_id_prefix=chunk_id_prefix
            ))

        return chunks

    def _create_chunk(
        self,
        content: str,
        source: str,
        document: str,
        section: str,
        position: int,
        chunk_id_prefix: str
    ) -> Chunk:
        """Create a chunk with metadata"""
        # Truncate if too long
        if len(content) > self.max_chunk_size:
            content = content[:self.max_chunk_size]

        return Chunk(
            content=content,
            chunk_id=f"{chunk_id_prefix}_{position}_{uuid.uuid4().hex[:6]}",
            source=source,
            document=document,
            section=section,
            position=position,
            metadata={}
        )


def chunk_documents(documents: List, chunker: MarkdownChunker = None) -> List[Chunk]:
    """
    Chunk a list of documents.

    Args:
        documents: List of Document objects
        chunker: Chunker instance (creates default if None)

    Returns:
        List of Chunk objects
    """
    if chunker is None:
        chunker = MarkdownChunker()

    all_chunks = []

    for doc in documents:
        chunks = chunker.chunk(
            content=doc.content,
            source=doc.source,
            document_title=doc.title
        )
        all_chunks.extend(chunks)

    return all_chunks
