"""Example usage of OpenRouter client for paper recommendations."""

from openrouter_client import OpenRouterClient

def main():
    """Run example paper analysis."""
    # Initialize client (make sure OPENROUTER_API_KEY is set in .env file)
    client = OpenRouterClient()
    
    try:
        # Get paper recommendations for AI field
        recommendations = client.analyze_papers(
            field="reinforcement learning",
            audience="expert"
        )
        
        # Print recommendations
        for i, paper in enumerate(recommendations, 1):
            print(f"\nPaper {i}:")
            print(f"Title: {paper.title}")
            print(f"Authors: {paper.authors}")
            print(f"Key Contributions: {paper.key_contributions}")
            print(f"Importance: {paper.importance}")
            print(f"Citation: {paper.citation}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
