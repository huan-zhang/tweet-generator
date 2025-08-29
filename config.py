"""
Configuration settings for the IgnorantStrength tweet generator.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration class for all settings."""
    
    # AI Provider Settings (OpenAI or Gemini)
    ai_provider: str = os.getenv("AI_PROVIDER", "openai")  # "openai" or "gemini"
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Twitter/X API Settings (OAuth 2.0)
    twitter_client_id: Optional[str] = os.getenv("TWITTER_CLIENT_ID")
    twitter_client_secret: Optional[str] = os.getenv("TWITTER_CLIENT_SECRET")
    twitter_bearer_token: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")
    
    # Legacy OAuth 1.0a (for media upload fallback)
    twitter_api_key: Optional[str] = os.getenv("TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = os.getenv("TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    # Content Generation Settings
    account_theme: str = "random stories"
    account_description: str = """
    A creative storytelling bot that generates short, engaging stories on random topics.
    Stories can range from everyday encounters to fantastical adventures, slice-of-life
    moments to thought-provoking scenarios. Each story is designed to entertain,
    inspire, or spark imagination in a brief social media format.
    """
    
    # Story Generation Settings
    story_model: str = "gpt-4o-mini"  # or "gemini-1.5-flash"
    story_max_length: int = 280  # Character limit for tweets (Twitter's max)
    story_temperature: float = 0.9  # Higher creativity for stories
    
    # Image Generation Settings
    image_model: str = "dall-e-3"  # or "gemini-pro-vision"
    image_size: str = "1024x1024"
    image_style: str = "minimalist, inspirational"
    image_output_dir: str = "generated_images"
    
    # Posting Settings
    auto_post: bool = os.getenv("AUTO_POST", "false").lower() == "true"
    posts_per_day: int = 3  # For batch generation (scheduler still needs this)
    
    # Scheduling Settings - Every 8 hours
    post_times: list = None  # Will be set in __post_init__
    
    def __post_init__(self):
        """Set default post times if not provided."""
        if self.post_times is None:
            self.post_times = ["08:00", "16:00", "00:00"]  # 8 AM, 4 PM, Midnight (every 8 hours)
        
        # Create image output directory if it doesn't exist
        os.makedirs(self.image_output_dir, exist_ok=True)
        
        # Validate required API keys
        if self.ai_provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        
        if self.ai_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("Gemini API key is required when using Gemini provider")
        
        if self.auto_post and not (
            (self.twitter_client_id and self.twitter_client_secret) or
            (self.twitter_api_key and self.twitter_api_secret and 
             self.twitter_access_token and self.twitter_access_token_secret)
        ):
            raise ValueError("Twitter API credentials are required for auto-posting (either OAuth 2.0 Client ID/Secret or OAuth 1.0a keys)")
    
    @property
    def story_prompt_template(self) -> str:
        """Template for generating short stories."""
        story_topics = [
            "a chance encounter at a coffee shop",
            "finding something unexpected in an old book",
            "a conversation with a stranger on public transport",
            "a pet's mysterious behavior",
            "discovering a hidden room in your house",
            "a child's innocent question that changes everything",
            "the last person on earth scenario",
            "a time traveler's small mistake",
            "an AI learning about human emotions",
            "a superhero with a mundane day job",
            "a world where colors have sounds",
            "someone who can hear plants thoughts",
            "a library that contains books from the future",
            "the day gravity stopped working",
            "a character who ages backwards",
            "a town where everyone tells the truth",
            "finding a message in a bottle",
            "a magical vending machine",
            "the first day at a peculiar job",
            "a memory that isn't your own"
        ]
        
        import random
        topic = random.choice(story_topics)
        
        return f"""
        Write a very short story (maximum {self.story_max_length} characters) about: {topic}
        
        Requirements:
        - Complete narrative with beginning, middle, and end
        - Engaging and creative
        - Can be realistic, fantastical, humorous, or thought-provoking
        - Should hook the reader immediately
        - Include relevant hashtags at the end (2-3 hashtags max)
        - Must fit in a single social media post
        
        Return only the story text with hashtags, nothing else.
        """
    
    @property
    def image_prompt_template(self) -> str:
        """Template for generating image prompts."""
        return """
        Create a {style} illustration that captures the essence of this story: "{story}"
        
        The image should:
        - Visually represent the key scene or mood of the story
        - Be engaging and eye-catching for social media
        - Use vibrant, appealing colors
        - Have an artistic, creative style
        - Capture the emotional tone of the story
        - Be suitable for Twitter/X posting
        - Avoid including readable text in the image
        
        Style: {style}
        """