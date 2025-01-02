"""Service for database operations."""
import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from ..models.paper import Paper

class DatabaseService:
    """Service for managing paper storage in SQLite."""

    def __init__(self, db_path: Path):
        """Initialize with database path."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT,
                authors TEXT,
                abstract TEXT,
                categories TEXT,
                published DATE,
                data JSON,
                UNIQUE(id)
            )
        ''')
        conn.commit()
        conn.close()

    def store_paper(self, paper: Paper):
        """Store a paper in the database."""
        conn = sqlite3.connect(self.db_path)
        paper_dict = paper.to_dict()
        conn.execute('''
            INSERT OR REPLACE INTO papers 
            (id, title, authors, abstract, categories, published, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            paper.id,
            paper.title,
            json.dumps(paper.authors),
            paper.abstract,
            json.dumps(paper.categories),
            paper.published.isoformat(),
            json.dumps(paper_dict)
        ))
        conn.commit()
        conn.close()

    def search_papers(self, query: Optional[str] = None, 
                     start_date: Optional[str] = None, 
                     end_date: Optional[str] = None) -> List[Paper]:
        """Search papers in the database."""
        conn = sqlite3.connect(self.db_path)
        sql = "SELECT data FROM papers WHERE 1=1"
        params = []

        if query:
            sql += " AND (title LIKE ? OR abstract LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])

        if start_date:
            sql += " AND published >= ?"
            params.append(start_date)

        if end_date:
            sql += " AND published <= ?"
            params.append(end_date)

        results = []
        for row in conn.execute(sql, params):
            paper_dict = json.loads(row[0])
            results.append(Paper.from_dict(paper_dict))

        conn.close()
        return results
