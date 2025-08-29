"""
Quote generation module supporting both OpenAI and Gemini models.
Generates inspirational quotes based on the "ignorant strength" theme.
"""

import logging
import random
from typing import List, Optional
import openai
import google.generativeai as genai

logger = logging.getLogger(__name__)


class QuoteGenerator:
    """Generates quotes using AI models based on the ignorant strength theme."""
    
    def __init__(self, config):
        self.config = config
        self.fallback_quotes = [
            "Strength isn't knowing everything; it's knowing when you don't know enough. #IgnorantStrength #Wisdom #Growth",
            "The wisest person admits their ignorance and grows from it. #Humility #Learning #Strength",
            "True power comes from embracing what you don't understand. #IgnorantStrength #Mindset #Growth",
            "In uncertainty, we find our greatest opportunities for growth. #Uncertainty #Strength #Learning",
            "The courage to say 'I don't know' is the beginning of wisdom. #Courage #Wisdom #IgnorantStrength"
        ]
        
        self._setup_ai_client()
    
    def _setup_ai_client(self):
        """Initialize the AI client based on the configured provider."""
        if self.config.ai_provider == "openai":
            openai.api_key = self.config.openai_api_key
        elif self.config.ai_provider == "gemini":
            genai.configure(api_key=self.config.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            raise ValueError(f"Unsupported AI provider: {self.config.ai_provider}")
    
    def generate_quote(self) -> str:
        """Generate a quote using the configured AI provider."""
        try:
            if self.config.ai_provider == "openai":
                return self._generate_with_openai()
            elif self.config.ai_provider == "gemini":
                return self._generate_with_gemini()
        except Exception as e:
            logger.error(f"Error generating quote with {self.config.ai_provider}: {str(e)}")
            logger.info("Falling back to random pre-written quote")
            return random.choice(self.fallback_quotes)
    
    def _generate_with_openai(self) -> str:
        """Generate quote using OpenAI API."""
        try:
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            response = client.chat.completions.create(
                model=self.config.quote_model,
                messages=[
                    {"role": "system", "content": "You are a wise philosopher who creates inspiring quotes about finding strength in humility and growth through not knowing."},
                    {"role": "user", "content": self.config.quote_prompt_template}
                ],
                temperature=self.config.quote_temperature,
                max_tokens=100
            )
            
            quote = response.choices[0].message.content.strip()
            
            # Validate quote length
            if len(quote) > self.config.quote_max_length:
                quote = self._truncate_quote(quote)
            
            logger.info(f"Generated quote with OpenAI: {quote[:50]}...")
            return quote
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _generate_with_gemini(self) -> str:
        """Generate quote using Gemini API."""
        try:
            response = self.gemini_model.generate_content(
                self.config.quote_prompt_template,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.quote_temperature,
                    max_output_tokens=100
                )
            )
            
            quote = response.text.strip()
            
            # Validate quote length
            if len(quote) > self.config.quote_max_length:
                quote = self._truncate_quote(quote)
            
            logger.info(f"Generated quote with Gemini: {quote[:50]}...")
            return quote
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _truncate_quote(self, quote: str) -> str:
        """Truncate quote to fit within character limit while preserving hashtags."""
        if len(quote) <= self.config.quote_max_length:
            return quote
        
        # Try to preserve hashtags at the end
        hashtag_start = quote.rfind('#')
        if hashtag_start != -1:
            main_quote = quote[:hashtag_start].strip()
            hashtags = quote[hashtag_start:]
            
            # Calculate available space for main quote
            available_length = self.config.quote_max_length - len(hashtags) - 1  # -1 for space
            
            if available_length > 50:  # Ensure minimum quote length
                truncated_main = main_quote[:available_length].rsplit(' ', 1)[0]  # Cut at word boundary
                return f"{truncated_main} {hashtags}"
        
        # Fallback: simple truncation at word boundary
        truncated = quote[:self.config.quote_max_length].rsplit(' ', 1)[0]
        return truncated + "..."
    
    def generate_batch_quotes(self, count: int = 3) -> List[str]:
        """Generate multiple quotes for batch processing."""
        quotes = []
        for i in range(count):
            try:
                quote = self.generate_quote()
                quotes.append(quote)
                logger.info(f"Generated quote {i+1}/{count}")
            except Exception as e:
                logger.error(f"Error generating quote {i+1}: {str(e)}")
                quotes.append(random.choice(self.fallback_quotes))
        
        return quotes