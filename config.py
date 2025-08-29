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
    account_theme: str = "ignorant strength"
    account_description: str = """
    The concept of 'ignorant strength' - finding power in not knowing everything,
    embracing uncertainty, learning from failures, and drawing strength from humility.
    The wisdom that comes from admitting what you don't know and growing from it.
    """
    
    # Quote Generation Settings
    quote_model: str = "gpt-4o-mini"  # or "gemini-1.5-flash"
    quote_max_length: int = 200  # Character limit for tweets
    quote_temperature: float = 0.8
    
    # Image Generation Settings
    image_model: str = "dall-e-3"  # or "gemini-pro-vision"
    image_size: str = "1024x1024"
    image_style: str = "minimalist, inspirational"
    image_output_dir: str = "generated_images"
    
    # Posting Settings
    auto_post: bool = os.getenv("AUTO_POST", "false").lower() == "true"
    posts_per_day: int = 3
    
    # Scheduling Settings
    post_times: list = None  # Will be set in __post_init__
    
    def __post_init__(self):
        """Set default post times if not provided."""
        if self.post_times is None:
            self.post_times = ["09:00", "14:00", "19:00"]  # 9 AM, 2 PM, 7 PM
        
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
    def quote_prompt_template(self) -> str:
        """Template for generating quotes."""
        return f"""
        Generate an inspirational quote that embodies the concept of "{self.account_theme}".
        
        Theme description: {self.account_description}
        
        Requirements:
        - Maximum {self.quote_max_length} characters
        - Should be thought-provoking and inspiring
        - Can be an original quote or inspired by existing wisdom
        - Focus on themes like: humility, growth through uncertainty, strength in vulnerability, wisdom from not knowing
        - Should resonate with people who understand that admitting ignorance is a form of strength
        - Include relevant hashtags at the end
        
        Return only the quote text with hashtags, nothing else.
        """
    
    @property
    def image_prompt_template(self) -> str:
        """Template for generating image prompts."""
        return """
        Create a {style} image that visually represents this quote: "{quote}"
        
        The image should:
        - Be inspirational and thought-provoking
        - Use calming, powerful colors
        - Include minimal text overlay if any
        - Have a clean, modern aesthetic
        - Convey strength, wisdom, and growth
        - Be suitable for social media sharing
        
        Style: {style}
        """