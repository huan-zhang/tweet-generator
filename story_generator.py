"""
Story generation module supporting both OpenAI and Gemini models.
Generates short, creative stories on random topics.
"""

import logging
import random
from typing import List, Optional
import openai
import google.generativeai as genai

logger = logging.getLogger(__name__)


class StoryGenerator:
    """Generates short stories using AI models on random topics."""
    
    def __init__(self, config):
        self.config = config
        self.fallback_stories = [
            "She opened the old music box. Instead of a ballerina, a tiny dragon emerged, yawned, and asked for coffee. 'Mondays,' it muttered. #TinyTales #Fantasy #MondayMood",
            "The last library on Earth had one visitor daily - a robot learning to read bedtime stories to mechanical children. #SciFi #Hope #Books",
            "He found a vending machine selling 'Lost Memories' for $1.50. His childhood summers cost extra. #Memory #Mystery #Life",
            "The time traveler's biggest problem wasn't paradoxes - it was remembering which century required which social media platform. #TimeTravel #Comedy #SocialMedia",
            "Every night at 3 AM, the houseplants gossiped about their owners. Tonight, they planned an intervention. #Plants #Humor #Mystery"
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
    
    def generate_story(self) -> str:
        """Generate a story using the configured AI provider."""
        try:
            if self.config.ai_provider == "openai":
                return self._generate_with_openai()
            elif self.config.ai_provider == "gemini":
                return self._generate_with_gemini()
        except Exception as e:
            logger.error(f"Error generating story with {self.config.ai_provider}: {str(e)}")
            logger.info("Falling back to random pre-written story")
            return random.choice(self.fallback_stories)
    
    def _generate_with_openai(self) -> str:
        """Generate story using OpenAI API."""
        try:
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            response = client.chat.completions.create(
                model=self.config.story_model,
                messages=[
                    {"role": "system", "content": "You are a creative storyteller who writes engaging, concise stories that capture readers' imagination in just a few sentences. Your stories are diverse, ranging from fantasy to slice-of-life, humor to mystery."},
                    {"role": "user", "content": self.config.story_prompt_template}
                ],
                temperature=self.config.story_temperature,
                max_tokens=250
            )
            
            story = response.choices[0].message.content.strip()
            
            # Validate story length
            if len(story) > self.config.story_max_length:
                story = self._truncate_story(story)
            
            logger.info(f"Generated story with OpenAI: {story[:50]}...")
            return story
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _generate_with_gemini(self) -> str:
        """Generate story using Gemini API."""
        try:
            response = self.gemini_model.generate_content(
                self.config.story_prompt_template,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.story_temperature,
                    max_output_tokens=250
                )
            )
            
            story = response.text.strip()
            
            # Validate story length
            if len(story) > self.config.story_max_length:
                story = self._truncate_story(story)
            
            logger.info(f"Generated story with Gemini: {story[:50]}...")
            return story
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _truncate_story(self, story: str) -> str:
        """Truncate story to fit within character limit while preserving hashtags."""
        if len(story) <= self.config.story_max_length:
            return story
        
        # Try to preserve hashtags at the end
        hashtag_start = story.rfind('#')
        if hashtag_start != -1:
            main_story = story[:hashtag_start].strip()
            hashtags = story[hashtag_start:]
            
            # Calculate available space for main story
            available_length = self.config.story_max_length - len(hashtags) - 1  # -1 for space
            
            if available_length > 100:  # Ensure minimum story length
                truncated_main = main_story[:available_length].rsplit(' ', 1)[0]  # Cut at word boundary
                return f"{truncated_main} {hashtags}"
        
        # Fallback: simple truncation at word boundary
        truncated = story[:self.config.story_max_length].rsplit(' ', 1)[0]
        return truncated + "..."
    
    def generate_batch_stories(self, count: int = 3) -> List[str]:
        """Generate multiple stories for batch processing."""
        stories = []
        for i in range(count):
            try:
                story = self.generate_story()
                stories.append(story)
                logger.info(f"Generated story {i+1}/{count}")
            except Exception as e:
                logger.error(f"Error generating story {i+1}: {str(e)}")
                stories.append(random.choice(self.fallback_stories))
        
        return stories