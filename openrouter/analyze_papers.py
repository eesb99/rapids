"""Analyze arXiv paper abstracts using deepseek-chat."""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from openrouter_client import OpenRouterClient, PaperRecommendation
import requests
from types import SimpleNamespace

class PromptConfig:
    """Configuration loader and manager for prompt settings."""
    
    DEFAULT_CONFIG_PATH = "prompt_config.json"
    
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Prompt config file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in prompt config file: {config_path}")
            
    @property
    def prompt_template(self) -> str:
        """Get the prompt template."""
        return self.config['prompt_template']
        
    @property
    def example_output(self) -> List[Dict]:
        """Get example output format."""
        return self.config['example_output']
        
    @property
    def field_examples(self) -> List[str]:
        """Get example fields."""
        return self.config['field_examples']
        
    @property
    def audience_types(self) -> Dict[str, str]:
        """Get valid audience types."""
        return self.config['audience_types']
        
    def get_audience_display(self, audience_type: str) -> str:
        """Get display name for audience type."""
        return self.audience_types.get(audience_type, "general audience")

def get_api_key() -> str:
    """Get OpenRouter API key from environment variables.
    
    Checks in the following order:
    1. OPENROUTER_API_KEY environment variable
    2. Windows system environment variables
    
    Returns:
        API key if found
        
    Raises:
        ValueError if no API key found
    """
    # Try getting from environment variable
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("\nNo OpenRouter API key found in environment variables.")
        print("Please set your API key in Windows system environment variables:")
        print("1. Open System Properties > Advanced > Environment Variables")
        print("2. Add new System Variable:")
        print("   Name: OPENROUTER_API_KEY")
        print("   Value: your-api-key-here")
        raise ValueError("OpenRouter API key not found")
        
    return api_key

class PaperAnalyzer:
    """Analyzes research papers from ArXiv."""
    
    def __init__(self, client: OpenRouterClient):
        """Initialize analyzer with API client."""
        self.client = client

    def _extract_abstract_from_json(self, data: Dict) -> Optional[str]:
        """Extract abstract from JSON paper data.
        
        Handles different JSON structures that might contain the abstract.
        
        Args:
            data: JSON data from paper file
            
        Returns:
            Abstract text if found, None otherwise
        """
        # Try common field names for abstract
        abstract_fields = ['abstract', 'Abstract', 'summary', 'Summary', 'text', 'Text']
        
        # If data is a string, return it directly
        if isinstance(data, str):
            return data
            
        # If data is a list, try to find abstract in each item
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    result = self._extract_abstract_from_json(item)
                    if result:
                        return result
            return None
            
        # If data is a dict, try to find abstract field
        if isinstance(data, dict):
            # Try direct field names
            for field in abstract_fields:
                if field in data and data[field]:
                    return str(data[field])
            
            # Try nested fields
            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self._extract_abstract_from_json(value)
                    if result:
                        return result
                        
        return None

    def _create_analysis_prompt(self, content: str, field: str, audience: str = "general") -> str:
        """Create analysis prompt for paper analysis."""
        prompt = f"""Analyze this research paper. Provide:
        1. Title
        2. Authors
        3. Key Contributions (2-3 sentences about what's new or innovative)
        4. Why It's Important (potential impact and significance)
        5. Citation (with clickable link if available)
        6. Reason Chosen (why this paper is relevant to {field})

        Paper content:
        {content}"""
        
        return prompt

    def analyze_date_papers(self, date_str: str, field: str = "all",
                          arxiv_dir: str = "../output/arxiv_papers",
                          audience: str = "general") -> str:
        """Analyze all papers for a specific date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            field: Field/topic to analyze papers for (default: "all")
            arxiv_dir: Directory containing arxiv paper folders
            audience: Target audience type (default: "general")
            
        Returns:
            Path to output JSON file
            
        Raises:
            ValueError: If no papers found or invalid date format
            FileNotFoundError: If arxiv directory doesn't exist
        """
        try:
            # Check if date directory exists
            date_path = os.path.join(arxiv_dir, date_str)
            if not os.path.exists(date_path):
                raise FileNotFoundError(f"No papers found for date {date_str}")
                
            # Get all paper JSON files (not analysis files)
            json_files = []
            for filename in os.listdir(date_path):
                if filename.endswith('.json') and not filename.startswith('analysis_'):
                    json_files.append(os.path.join(date_path, filename))
            
            if not json_files:
                raise ValueError(f"No paper files found in {date_path}")
                
            # Group papers by category
            papers_by_category = {}
            for json_file in json_files:
                try:
                    # Extract category from filename (e.g., cs.AI_papers.json -> cs.AI)
                    filename = os.path.basename(json_file)
                    if not filename.endswith('_papers.json'):
                        continue
                    category = filename[:-12]  # Remove _papers.json
                    
                    with open(json_file, 'r', encoding='utf-8') as f:
                        papers_data = json.load(f)
                        if not isinstance(papers_data, list):
                            print(f"Warning: {json_file} does not contain a list of papers")
                            continue
                            
                        # Add all papers from this file to their category
                        if category not in papers_by_category:
                            papers_by_category[category] = []
                        
                        for paper_data in papers_data:
                            if isinstance(paper_data, dict):
                                papers_by_category[category].append((json_file, paper_data))
                except Exception as e:
                    print(f"Error reading {json_file}: {str(e)}")
                    continue
            
            total_categories = len(papers_by_category)
            print(f"\nFound {total_categories} categories in {date_str}:")
            for category, papers in papers_by_category.items():
                print(f"  - {category}: {len(papers)} papers")
            
            analyzed_papers = []
            failed_papers = []
            
            # Process top paper from each category
            for category, papers in papers_by_category.items():
                print(f"\nAnalyzing top paper from {category}...")
                
                # Sort papers by citation count if available, otherwise take first one
                if len(papers) > 1:
                    sorted_papers = sorted(papers, 
                        key=lambda x: len(x[1].get('citations', [])) if isinstance(x[1].get('citations'), list) else 0, 
                        reverse=True)
                else:
                    sorted_papers = papers
                
                # Take top paper from category
                json_file, data = sorted_papers[0]
                print(f"Selected paper: {os.path.basename(json_file)}")
                
                try:
                    paper_info = {
                        'file': json_file,
                        'title': data.get('title', data.get('Title', 'Unknown Title')),
                        'authors': data.get('authors', data.get('Authors', 'Unknown Authors')),
                        'abstract': data.get('abstract', data.get('Abstract', '')),
                        'category': category,
                        'failure_stage': None,
                        'error_type': None,
                        'error_details': None,
                        'content_preview': None,
                        'timestamp': datetime.now().isoformat()
                    }

                    # Extract abstract
                    print(f"  Extracting abstract...", end='', flush=True)
                    content = paper_info['abstract']
                    if not content:
                        print(" Error: No abstract found")
                        paper_info.update({
                            'failure_stage': 'abstract_extraction',
                            'error_type': 'NoAbstractFound',
                            'error_details': 'No abstract content found in paper data'
                        })
                        failed_papers.append(paper_info)
                        continue
                    print(" Done")

                    paper_info['content_preview'] = content[:200] + '...' if len(content) > 200 else content
                    
                    # Create analysis prompt
                    print(f"  Creating analysis prompt...", end='', flush=True)
                    try:
                        prompt = self._create_analysis_prompt(content, field, audience)
                        print(" Done")
                    except Exception as e:
                        print(f" Error: {str(e)}")
                        paper_info.update({
                            'failure_stage': 'prompt_creation',
                            'error_type': type(e).__name__,
                            'error_details': str(e)
                        })
                        failed_papers.append(paper_info)
                        continue

                    # API Analysis
                    print(f"  Analyzing paper with API...", end='', flush=True)
                    try:
                        recommendations = self.client.analyze_papers(content=content, field=field, audience=audience)
                        if recommendations and recommendations[0].title != "Unknown Title":
                            for rec in recommendations:
                                rec.category = category
                            analyzed_papers.extend(recommendations)
                            print(" Done")
                        else:
                            print(" Error: No valid recommendations returned")
                            paper_info.update({
                                'failure_stage': 'api_response',
                                'error_type': 'InvalidRecommendations',
                                'error_details': 'API returned empty or invalid recommendations'
                            })
                            failed_papers.append(paper_info)
                    except (requests.Timeout, requests.RequestException) as e:
                        print(f" Error: API request failed - {str(e)}")
                        paper_info.update({
                            'failure_stage': 'api_request',
                            'error_type': type(e).__name__,
                            'error_details': f"API request error: {str(e)}"
                        })
                        failed_papers.append(paper_info)
                        continue
                    except ValueError as e:
                        print(f" Error: Response parsing failed - {str(e)}")
                        paper_info.update({
                            'failure_stage': 'api_response_parsing',
                            'error_type': 'ValueError',
                            'error_details': f"API response parsing error: {str(e)}"
                        })
                        failed_papers.append(paper_info)
                        continue
                    except KeyboardInterrupt:
                        print("\nOperation cancelled by user")
                        paper_info.update({
                            'failure_stage': 'user_cancelled',
                            'error_type': 'KeyboardInterrupt',
                            'error_details': 'Analysis cancelled by user'
                        })
                        failed_papers.append(paper_info)
                        break
                    except Exception as e:
                        print(f" Error: {str(e)}")
                        paper_info.update({
                            'failure_stage': 'analysis',
                            'error_type': type(e).__name__,
                            'error_details': f"Unexpected error during analysis: {str(e)}"
                        })
                        failed_papers.append(paper_info)
                        continue
                        
                except Exception as e:
                    print(f" Error: Unexpected error - {str(e)}")
                    failed_papers.append({
                        'file': json_file,
                        'category': category,
                        'failure_stage': 'unknown',
                        'error_type': type(e).__name__,
                        'error_details': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    continue
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            success_rate = len(analyzed_papers) / total_categories if total_categories else 0
            success_rate_str = f"sr{int(success_rate * 100)}"
            
            output_filename = f"analysis_{field.replace(' ', '_')}_{audience}_{timestamp}_{success_rate_str}.json"
            output_path = os.path.join(date_path, output_filename)
            
            # Create output JSON
            output = {
                'metadata': {
                    'date': date_str,
                    'field': field,
                    'audience': audience,
                    'total_categories': total_categories,
                    'categories': list(papers_by_category.keys()),
                    'papers_per_category': {cat: len(papers) for cat, papers in papers_by_category.items()},
                    'successful_analyses': len(analyzed_papers),
                    'failed_analyses': len(failed_papers),
                    'success_rate': success_rate,
                    'timestamp': datetime.now().isoformat()
                },
                'failure_summary': {
                    stage: len([p for p in failed_papers if p.get('failure_stage') == stage])
                    for stage in set(p.get('failure_stage') for p in failed_papers if p.get('failure_stage'))
                },
                'papers': [paper.to_dict() for paper in analyzed_papers],
                'failed_papers': failed_papers
            }
            
            # Write output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                
            print(f"\nAnalysis saved to: {output_path}")
            print(f"\nAnalyzed {len(analyzed_papers)} papers for {date_str}")
            print(f"Results saved to {output_filename}")
            
            return output_path
            
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            raise
        except ValueError as e:
            print(f"Error: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error during analysis: {str(e)}"
            print(f"Error: {error_msg}")
            raise ValueError(error_msg)

    def list_available_dates(self, arxiv_dir: str = "../output/arxiv_papers") -> List[str]:
        """List available dates in the arxiv directory."""
        arxiv_path = arxiv_dir
        if not os.path.exists(arxiv_path):
            return []
            
        return [d for d in os.listdir(arxiv_path) if os.path.isdir(os.path.join(arxiv_path, d)) and 
                len([f for f in os.listdir(os.path.join(arxiv_path, d)) if f.endswith('.json') and not f.startswith('analysis_')]) > 0]  # Only show dates with JSON files

def get_user_input(analyzer: PaperAnalyzer) -> tuple:
    """Get user input for paper analysis.
    
    Returns:
        tuple: (arxiv_dir, date_str, field, audience)
    """
    print("\nArXiv Paper Analyzer")
    print("===================\n")
    
    # Get arxiv directory path
    default_path = "../output/arxiv_papers"
    print(f"Enter arxiv directory path [{default_path}]")
    print("(Press Enter to use default path and see available dates)")
    arxiv_path = input("> ").strip()
    arxiv_path = arxiv_path if arxiv_path else default_path
    
    # Convert relative path to absolute if needed
    if not os.path.isabs(arxiv_path):
        arxiv_path = os.path.abspath(arxiv_path)
    
    # List available dates
    print("\nAvailable dates:")
    dates = analyzer.list_available_dates(arxiv_path)
    if not dates:
        raise ValueError(f"No paper directories found in {arxiv_path}")
    
    for date in sorted(dates, reverse=True):
        print(f"  - {date}")
    
    # Get date
    while True:
        print("\nEnter date to analyze (YYYY-MM-DD)")
        print("(Choose from the dates listed above)")
        date_str = input("> ").strip()
        if date_str in dates:
            break
        print(f"Invalid date. Please choose from: {', '.join(dates)}")
    
    # Get field/topic
    print("\nExample fields: reinforcement learning, generative AI, medical imaging, natural language processing, computer vision")
    print("Enter field/topic to analyze [all]")
    print("(Press Enter to analyze all fields)")
    field = input("> ").strip()
    field = field if field else "all"
    
    # Get audience type
    print("\nAvailable audience types:")
    print("  - general")
    
    while True:
        print("\nEnter target audience type [general]")
        print("(Press Enter for general audience)")
        audience = input("> ").strip().lower()
        audience = audience if audience else "general"
        if audience == "general":
            break
        print(f"Invalid audience type. Please choose from: general")
    
    return arxiv_path, date_str, field, audience

def main():
    """Run paper analysis for a specific date."""
    import argparse
    import sys
    
    try:
        # Check if arguments provided
        if len(sys.argv) == 1:
            # No args - use interactive mode
            api_key = get_api_key()
            client = OpenRouterClient(api_key=api_key)
            analyzer = PaperAnalyzer(client)
            result = get_user_input(analyzer)
            if not result:
                return
            arxiv_dir, date_str, field, audience = result
        else:
            # Use command line arguments
            parser = argparse.ArgumentParser(description="Analyze arXiv papers using deepseek-chat")
            parser.add_argument("date", help="Date to analyze (YYYY-MM-DD)")
            parser.add_argument("field", nargs='?', default="all", 
                              help="Field/topic to analyze papers for (default: all)")
            parser.add_argument("--audience", choices=["general"],
                              default="general", help="Target audience (default: general)")
            parser.add_argument("--arxiv-dir", default="../output/arxiv_papers",
                               help="Directory containing arxiv paper folders")
            
            args = parser.parse_args()
            arxiv_dir, date_str, field, audience = args.arxiv_dir, args.date, args.field, args.audience
        
        # Initialize OpenRouter client and analyzer
        api_key = get_api_key()
        client = OpenRouterClient(api_key=api_key)
        analyzer = PaperAnalyzer(client)
        
        # Run analysis
        results = analyzer.analyze_date_papers(
            date_str,
            field,
            arxiv_dir,
            audience
        )
        
        print(f"\nAnalyzed {len(results)} papers for {date_str}")
        print(f"Results saved to analysis_{field.replace(' ', '_')}_{audience}.json")
        
    except ValueError as e:
        print(f"\nError: {str(e)}")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
