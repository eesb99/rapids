"""Model class for ArXiv papers."""
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Paper:
    """Represents an ArXiv paper with its metadata."""
    id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published: datetime
    pdf_url: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Paper':
        """Create a Paper instance from a dictionary."""
        return cls(
            id=data['id'],
            title=data['title'],
            authors=data['authors'],
            abstract=data['abstract'],
            categories=data['categories'],
            published=datetime.fromisoformat(data['published']),
            pdf_url=data['pdf_url']
        )

    def to_dict(self) -> dict:
        """Convert Paper instance to a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'categories': self.categories,
            'published': self.published.isoformat(),
            'pdf_url': self.pdf_url
        }
