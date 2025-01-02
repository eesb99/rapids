"""Service for interacting with the ArXiv API."""
import arxiv
import time
from typing import List
from ..models.paper import Paper
from ...util.cache_utils import cache_get, cache_set, generate_cache_key

class ArxivService:
    """Service for fetching papers from ArXiv."""
    
    def __init__(self, config: dict):
        """Initialize with configuration."""
        self.config = config
        self.client = arxiv.Client()

    def fetch_papers_by_category(self, category: str, batch_size: int = 100) -> List[Paper]:
        """Fetch papers for a specific category."""
        query = f"cat:{category}"
        
        search = arxiv.Search(
            query=query,
            max_results=batch_size,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = []
        for result in self.client.results(search):
            paper = self._convert_to_paper(result)
            papers.append(paper)
            time.sleep(self.config['api']['rate_limit_delay'])

        return papers

    def _convert_to_paper(self, result: arxiv.Result) -> Paper:
        """Convert arxiv.Result to Paper model."""
        return Paper(
            id=result.entry_id,
            title=result.title,
            authors=[author.name for author in result.authors],
            abstract=result.summary,
            categories=result.categories,
            published=result.published,
            pdf_url=result.pdf_url
        )
