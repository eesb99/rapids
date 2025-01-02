import arxiv
import redis
import json
import click
import logging
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import time
from tqdm import tqdm
import sqlite3

class ArxivManager:
    def __init__(self, config_file="config/arxiv_config.json"):
        self.config = self._load_config(config_file)
        self.redis_client = redis.Redis(**self.config['cache'])
        self.setup_logging()
        self.db_path = Path('arxiv_papers.db')
        self._init_db()

    def _load_config(self, config_file: str) -> dict:
        with open(config_file, 'r') as f:
            return json.load(f)

    def setup_logging(self):
        logging.basicConfig(**self.config['logging'])
        self.logger = logging.getLogger(__name__)

    def _init_db(self):
        """Initialize SQLite database for historical search"""
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

    def fetch_papers(self, date_str: str, batch_size: int = 100) -> List[Dict]:
        papers = []
        for category in tqdm(self.config['categories']):
            papers.extend(self._fetch_category(category, date_str, batch_size))
        return papers

    def _fetch_category(self, category: str, date_str: str, batch_size: int) -> List[Dict]:
        cache_key = f"arxiv:{category}:{date_str}"
        cached = self.redis_client.get(cache_key)
        
        if cached:
            click.echo(f"Found cached results for {category} on {date_str}")
            cached_papers = json.loads(cached)
            click.echo(f"Saving {len(cached_papers)} cached papers...")
            self._save_outputs(cached_papers, date_str, category)
            return cached_papers

        client = arxiv.Client()
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        next_date = date_obj + timedelta(days=1)
        
        # Format dates in arXiv's preferred format YYYYMMDDHHMMSS
        start_date = date_obj.strftime('%Y%m%d000000')
        end_date = next_date.strftime('%Y%m%d000000')
        
        query = f"cat:{category} AND submittedDate:[{start_date} TO {end_date}]"
        max_papers = self.config['api'].get('max_papers_per_category', 50)
        
        click.echo(f"\nFetching papers for category {category}")
        click.echo(f"Query: {query}")
        click.echo(f"Max papers: {max_papers}")
        
        search = arxiv.Search(
            query=query,
            max_results=max_papers,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = []
        try:
            results = list(client.results(search))
            click.echo(f"Found {len(results)} results for {category}")
            
            for result in results:
                paper = self._extract_metadata(result)
                papers.append(paper)
                self._store_in_db(paper)
                if len(papers) >= max_papers:
                    click.echo(f"Reached limit of {max_papers} papers for {category}")
                    break
                time.sleep(self.config['api']['rate_limit_delay'])

            if papers:
                click.echo(f"Saving {len(papers)} papers to cache and outputs")
                self.redis_client.set(
                    cache_key,
                    json.dumps(papers)
                )
                click.echo("Calling _save_outputs...")
                self._save_outputs(papers, date_str, category)
                click.echo("Finished _save_outputs")
            else:
                click.echo(f"No papers found for category {category} on {date_str}")

        except Exception as e:
            click.echo(f"Error fetching papers for {category}: {str(e)}")
            self.logger.error(f"Error fetching papers for {category}: {str(e)}")
            self.logger.exception("Full error details:")

        return papers

    def _extract_metadata(self, paper) -> Dict:
        return {
            'id': paper.entry_id,
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'abstract': paper.summary,
            'categories': paper.categories,
            'published': paper.published.isoformat(),
            'pdf_url': paper.pdf_url
        }

    def _store_in_db(self, paper: Dict):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT OR REPLACE INTO papers 
            (id, title, authors, abstract, categories, published, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            paper['id'],
            paper['title'],
            json.dumps(paper['authors']),
            paper['abstract'],
            json.dumps(paper['categories']),
            paper['published'],
            json.dumps(paper)
        ))
        conn.commit()
        conn.close()

    def _save_outputs(self, papers: List[Dict], date_str: str, category: str) -> None:
        """Save papers to output files in different formats."""
        # Get base directory from config and resolve to absolute path
        base_dir = Path(self.config['output']['base_dir']).resolve()
        date_dir = base_dir / date_str
        
        # Create output directory if it doesn't exist
        date_dir.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"Saving to directory: {date_dir}")
        
        # Save JSON
        if 'json' in self.config['output']['formats']:
            json_file = date_dir / f"{category}_papers.json"
            click.echo(f"Saving JSON to: {json_file}")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(papers, f, indent=2, ensure_ascii=False)
            click.echo(f"JSON file exists: {json_file.exists()}")

        # Save CSV
        if 'csv' in self.config['output']['formats']:
            csv_file = date_dir / f"{category}_papers.csv"
            click.echo(f"Saving CSV to: {csv_file}")
            df = pd.DataFrame(papers)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            click.echo(f"CSV file exists: {csv_file.exists()}")

        # Save TXT
        if 'txt' in self.config['output']['formats']:
            txt_file = date_dir / f"{category}_papers.txt"
            click.echo(f"Saving TXT to: {txt_file}")
            with open(txt_file, 'w', encoding='utf-8') as f:
                for paper in papers:
                    f.write(f"Title: {paper['title']}\n")
                    f.write(f"Authors: {', '.join(paper['authors'])}\n")
                    f.write(f"Categories: {', '.join(paper['categories'])}\n")
                    f.write(f"Published: {paper['published']}\n")
                    f.write(f"PDF: {paper['pdf_url']}\n")
                    f.write(f"Abstract:\n{paper['abstract']}\n")
                    f.write("-" * 80 + "\n\n")
            click.echo(f"TXT file exists: {txt_file.exists()}")
        
        click.echo(f"Successfully saved {len(papers)} papers for category {category}")

    def _print_fetch_summary(self, papers: List[Dict], date_str: str):
        """Print a summary of fetched papers and save to file."""
        # Group papers by primary category (first category in list)
        by_category = {}
        configured_categories = set(self.config['categories'])
        
        for paper in papers:
            # Get primary category (first in list)
            primary_cat = paper['categories'][0]
            # Only count papers in our configured categories
            if primary_cat in configured_categories:
                if primary_cat not in by_category:
                    by_category[primary_cat] = []
                by_category[primary_cat].append(paper)

        # Count papers in configured categories
        total_relevant_papers = sum(len(papers) for papers in by_category.values())

        # Prepare summary text
        summary_lines = []
        summary_lines.append("=== Fetch Summary ===")
        summary_lines.append(f"\nDate: {date_str}")
        summary_lines.append(f"Total Papers in Main Categories: {total_relevant_papers}")
        summary_lines.append(f"Total Papers Overall: {len(papers)}")
        
        summary_lines.append("\nBy Main Category:")
        for cat in sorted(configured_categories):
            count = len(by_category.get(cat, []))
            summary_lines.append(f"  {cat}: {count} papers")
        
        summary_lines.append("\nLatest Papers (up to 5 per category):")
        for cat in sorted(configured_categories):
            if cat in by_category and by_category[cat]:
                summary_lines.append(f"\n{cat}:")
                for paper in by_category[cat][:5]:
                    summary_lines.append(f"  - {paper['title']}")
                    summary_lines.append(f"    Authors: {', '.join(paper['authors'][:3])}")
                    if len(paper['categories']) > 1:
                        summary_lines.append(f"    All Categories: {', '.join(paper['categories'])}")

        # Print to console
        click.echo("\n".join(summary_lines))

        # Save to file
        base_dir = Path(self.config['output']['base_dir']).resolve()
        date_dir = base_dir / date_str
        summary_file = date_dir / "fetch_summary.txt"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(summary_lines))
            click.echo(f"\nSummary saved to: {summary_file}")

            # Also save a markdown version for better formatting
            md_lines = []
            md_lines.append("# ArXiv Fetch Summary")
            md_lines.append(f"\n## Date: {date_str}")
            md_lines.append(f"**Total Papers in Main Categories:** {total_relevant_papers}")
            md_lines.append(f"**Total Papers Overall:** {len(papers)}")
            
            md_lines.append("\n## Papers by Main Category")
            for cat in sorted(configured_categories):
                count = len(by_category.get(cat, []))
                md_lines.append(f"\n### {cat}: {count} papers")
            
            md_lines.append("\n## Latest Papers")
            for cat in sorted(configured_categories):
                if cat in by_category and by_category[cat]:
                    md_lines.append(f"\n### {cat}")
                    for paper in by_category[cat][:5]:
                        md_lines.append(f"\n#### {paper['title']}")
                        md_lines.append(f"Authors: {', '.join(paper['authors'][:3])}")
                        if len(paper['categories']) > 1:
                            md_lines.append(f"Additional Categories: {', '.join(paper['categories'][1:])}")

            md_file = date_dir / "fetch_summary.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(md_lines))
            click.echo(f"Markdown summary saved to: {md_file}")

        except Exception as e:
            click.echo(f"Error saving summary: {str(e)}")
            self.logger.error(f"Error saving summary: {str(e)}")

    def search(self, query: str, start_date: str = None, end_date: str = None) -> List[Dict]:
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
            results.append(json.loads(row[0]))

        conn.close()
        return results

@click.group()
def cli():
    """ArXiv Paper Manager CLI"""
    pass

@cli.command()
@click.option('--date', default=None, help='Date in YYYY-MM-DD format')
@click.option('--batch-size', default=100, help='Batch size for fetching papers')
@click.option('--force', is_flag=True, help='Force fetch even if cached')
def fetch(date, batch_size, force):
    """Fetch papers for a specific date"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    click.echo(f"Starting fetch for date: {date}")
    manager = ArxivManager()
    
    # Print current working directory and config
    click.echo(f"Current directory: {Path.cwd()}")
    click.echo(f"Output directory: {Path(manager.config['output']['base_dir']).resolve()}")
    
    if force:
        click.echo("Forcing fresh fetch (ignoring cache)")
        # Clear any cached results for this date
        for category in manager.config['categories']:
            cache_key = f"arxiv:{category}:{date}"
            manager.redis_client.delete(cache_key)
    
    papers = manager.fetch_papers(date, batch_size)
    click.echo(f"Fetched {len(papers)} papers")
    
    # Print fetch summary
    manager._print_fetch_summary(papers, date)

    # Print first paper as a test
    if papers:
        click.echo("\nFirst paper details:")
        click.echo(f"Title: {papers[0]['title']}")
        click.echo(f"Authors: {', '.join(papers[0]['authors'])}")

@cli.command()
@click.argument('query')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
def search(query, start_date, end_date):
    """Search papers by query and date range"""
    manager = ArxivManager()
    results = manager.search(query, start_date, end_date)
    
    for paper in results:
        click.echo(f"\nTitle: {paper['title']}")
        click.echo(f"Authors: {', '.join(paper['authors'])}")
        click.echo(f"Published: {paper['published']}")
        click.echo("-" * 80)

if __name__ == '__main__':
    cli()
