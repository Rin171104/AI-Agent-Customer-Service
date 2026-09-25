"""
Document Loader - Load documents từ knowledge directory

Hỗ trợ:
    - Markdown files (.md)
    - Plain text (.txt)
"""
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Document:
    """Document entity"""
    content: str
    source: str  # filename
    title: str
    metadata: Dict[str, Any]


class DocumentLoader:
    """Load documents từ filesystem"""

    def __init__(self, knowledge_dir: str = None):
        if knowledge_dir is None:
            # Default: backend/data/knowledge/
            base_dir = Path(__file__).parent.parent.parent.parent
            knowledge_dir = base_dir / "data" / "knowledge"
        self.knowledge_dir = Path(knowledge_dir)

    def load(self, file_patterns: List[str] = None) -> List[Document]:
        """
        Load all documents from knowledge directory.

        Args:
            file_patterns: List of file patterns to load (e.g., ["*.md", "*.txt"])

        Returns:
            List of Document objects
        """
        if file_patterns is None:
            file_patterns = ["*.md"]

        documents = []

        if not self.knowledge_dir.exists():
            raise FileNotFoundError(f"Knowledge directory not found: {self.knowledge_dir}")

        for pattern in file_patterns:
            for file_path in self.knowledge_dir.glob(pattern):
                if file_path.is_file():
                    doc = self._load_file(file_path)
                    if doc:
                        documents.append(doc)

        return documents

    def _load_file(self, file_path: Path) -> Document:
        """Load a single file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title from first heading
            title = self._extract_title(content, file_path.stem)

            return Document(
                content=content,
                source=file_path.name,
                title=title,
                metadata={
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                }
            )
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def _extract_title(self, content: str, default: str) -> str:
        """Extract title from markdown content"""
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
            if line.startswith("#"):
                continue
            if line:
                return line[:100]  # First non-empty line, truncated
        return default


def load_knowledge_documents(knowledge_dir: str = None) -> List[Document]:
    """Convenience function to load all knowledge documents"""
    loader = DocumentLoader(knowledge_dir)
    return loader.load()
