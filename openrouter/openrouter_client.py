"""OpenRouter API client for research paper analysis using deepseek-chat model."""

import os
from typing import List, Dict, Optional
import requests
import json
from dotenv import load_dotenv
from pydantic import BaseModel

class PaperRecommendation(BaseModel):
    """Data model for paper recommendations."""
    title: str
    authors: str
    key_contributions: str
    importance: str
    citation: str
    reason_chosen: str = ""  # Why this paper was selected for analysis
    category: str = ""  # Paper category (e.g., cs.AI, cs.LG)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'title': self.title,
            'authors': self.authors,
            'key_contributions': self.key_contributions,
            'importance': self.importance,
            'citation': self.citation,
            'reason_chosen': self.reason_chosen,
            'category': self.category
        }

class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. If not provided, loads from OPENROUTER_API_KEY env variable.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-username/arxiv-analyzer",
            "X-Title": "ArXiv Paper Analyzer"
        }
        
        # Using Deepseek Chat model
        self.model = "deepseek/deepseek-chat"
        
        # Model limits for Deepseek Chat
        self.max_context_tokens = 32000  # 32k context window
        self.max_input_tokens = 8000     # 8k input limit
        self.max_output_tokens = 4000    # 4k output limit
        
        # Approximate chars per token (for rough estimation)
        self.chars_per_token = 4

    def _truncate_content(self, content: str, max_chars: int) -> str:
        """Truncate content to fit within token limits.
        
        Args:
            content: Text content to truncate
            max_chars: Maximum characters allowed
            
        Returns:
            Truncated content that fits within token limit
        """
        if len(content) <= max_chars:
            return content
            
        # Keep first 2/3 and last 1/3 of allowed content
        first_part = int(max_chars * 0.67)
        last_part = max_chars - first_part
        
        truncated = content[:first_part] + "\n...[content truncated]...\n" + content[-last_part:]
        return truncated

    def _create_analysis_prompt(self, content: str, field: str, audience: str = "general") -> str:
        """Create analysis prompt for paper analysis."""
        return f'''You are a research paper analyzer. Your task is to analyze the given paper abstract and provide a structured response.

IMPORTANT: You must follow this EXACT format with these EXACT section headers:

Title: [Extract the exact paper title]
Authors: [List all author names, separated by commas]
Key Contributions: [Describe 2-3 main innovations or contributions]
Importance: [Explain the potential impact and significance]
Citation: [Provide the paper citation]
Reason Chosen: [Explain why this paper is significant in {field}]

Example Response Format:
Title: Deep Learning for Computer Vision
Authors: John Smith, Jane Doe, Bob Johnson
Key Contributions: This paper introduces a novel neural architecture that reduces computational complexity by 50% while maintaining accuracy. It also presents a new data augmentation technique that improves model robustness.
Importance: The reduced computational requirements make deep learning more accessible for resource-constrained devices. The improved robustness enables wider adoption in critical applications.
Citation: Smith, J., Doe, J., Johnson, B. (2024). Deep Learning for Computer Vision. arXiv:2401.12345
Reason Chosen: This work addresses key challenges in {field} by making deep learning more efficient and reliable.

Now analyze this abstract:
{content}

Remember:
1. Use EXACTLY the same section headers as shown above
2. Extract information accurately from the abstract
3. Be specific and detailed in your analysis
4. Maintain the exact order of sections'''

    def analyze_papers(self, content: str, field: str, audience: str = "general") -> List[PaperRecommendation]:
        """Analyze research papers and get recommendations.
        
        Args:
            content: Paper content to analyze
            field: Specific field or topic for paper recommendations
            audience: Target audience (default: general)
            
        Returns:
            List of paper recommendations
        
        Raises:
            requests.RequestException: If API request fails
            requests.Timeout: If request times out
            ValueError: If response parsing fails
        """
        prompt = self._create_analysis_prompt(content, field, audience)

        try:
            # Set reasonable timeouts for connect and read
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": self.max_output_tokens
                },
                timeout=(10, 30)  # (connect timeout, read timeout)
            )
            
            if not response.ok:
                error_detail = response.json() if response.content else "No error details available"
                error_msg = f"API Error for model {self.model}: {response.status_code} - {error_detail}"
                print(f"Error: {error_msg}")
                raise requests.RequestException(error_msg)
            
            response_data = response.json()
            if 'choices' not in response_data:
                print("API Response:", response_data)
                raise ValueError("Missing 'choices' in API response")
                
            # Parse response and convert to PaperRecommendation objects
            return self._parse_recommendations(response_data)
            
        except requests.Timeout:
            error_msg = f"Request timed out while analyzing paper for field: {field}"
            print(f"Timeout Error: {error_msg}")
            raise
            
        except requests.RequestException as e:
            error_msg = f"Failed to analyze paper: {str(e)}"
            print(f"Request Error: {error_msg}")
            raise
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error while analyzing paper: {str(e)}"
            print(f"Error: {error_msg}")
            raise ValueError(error_msg)

    def _parse_recommendations(self, response: Dict) -> List[PaperRecommendation]:
        """Parse API response into PaperRecommendation objects."""
        try:
            # Extract message content from response
            if 'choices' not in response:
                print("API Response:", json.dumps(response, indent=2))
                raise ValueError("Missing 'choices' in API response")
                
            choices = response.get('choices', [])
            if not choices:
                print("API Response:", json.dumps(response, indent=2))
                raise ValueError("Empty choices in API response")
                
            message = choices[0].get('message', {})
            if not message:
                print("API Response:", json.dumps(response, indent=2))
                raise ValueError("No message in API response choice")
                
            content = message.get('content', '')
            if not content:
                print("API Response:", json.dumps(response, indent=2))
                raise ValueError("Empty content in API response message")

            print("\nRaw API Response Content:")
            print("-" * 80)
            print(content)
            print("-" * 80)

            # Parse sections from content
            sections = {}
            current_section = None
            current_text = []
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # More flexible section header matching
                for header in [
                    ('Title:', 'title'),
                    ('Authors:', 'authors'),
                    ('Key Contributions:', 'key_contributions'),
                    ('Importance:', 'importance'),
                    ('Citation:', 'citation'),
                    ('Reason Chosen:', 'reason_chosen')
                ]:
                    if line.lower().startswith(header[0].lower()):
                        if current_section:
                            sections[current_section] = '\n'.join(current_text).strip()
                        current_section = header[1]
                        current_text = [line[len(header[0]):].strip()]
                        break
                else:
                    if current_section:
                        current_text.append(line)
            
            # Add final section
            if current_section:
                sections[current_section] = '\n'.join(current_text).strip()

            print("\nParsed Sections:")
            print("-" * 80)
            for section, content in sections.items():
                print(f"{section}: {content}")
            print("-" * 80)
            
            # Validate required sections
            required_sections = ['title', 'authors', 'key_contributions', 'importance', 'citation']
            missing_sections = [s for s in required_sections if not sections.get(s)]
            if missing_sections:
                raise ValueError(f"Missing required sections: {', '.join(missing_sections)}")
            
            # Check for default/empty values
            if sections['title'] in ['Unknown Title', '[Paper title]']:
                raise ValueError("Title not properly extracted")
            if sections['authors'] in ['Unknown Authors', '[Author names]']:
                raise ValueError("Authors not properly extracted")
            if sections['key_contributions'] in ['No contributions listed', '[2-3 sentences about what\'s new or innovative in this paper]']:
                raise ValueError("Key contributions not properly extracted")
            
            recommendation = PaperRecommendation(
                title=sections.get('title'),
                authors=sections.get('authors'),
                key_contributions=sections.get('key_contributions'),
                importance=sections.get('importance'),
                citation=sections.get('citation'),
                reason_chosen=sections.get('reason_chosen', '')
            )
            
            return [recommendation]
            
        except Exception as e:
            print(f"\nError parsing API response: {str(e)}")
            print("\nRaw API Response:")
            print("-" * 80)
            print(json.dumps(response, indent=2))
            print("-" * 80)
            raise ValueError(f"Failed to parse API response: {str(e)}")
