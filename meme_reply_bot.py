#!/usr/bin/env python3
"""
Twitter Meme Reply Bot
Analyzes a tweet and creates funny/ironic memes to reply with.
"""

import logging
import sys
import argparse
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
import openai
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import requests
import json

from config import Config
from twitter_poster import TwitterPoster

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meme_replies.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TweetAnalyzer:
    """Analyzes tweets and generates meme concepts."""
    
    def __init__(self, config: Config):
        self.config = config
        self._setup_ai_client()
    
    def _setup_ai_client(self):
        """Initialize AI client."""
        if self.config.ai_provider == "openai":
            openai.api_key = self.config.openai_api_key
        elif self.config.ai_provider == "gemini":
            genai.configure(api_key=self.config.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_tweet_for_meme(self, tweet_text: str, tweet_author: str) -> Dict:
        """Analyze tweet and generate meme concept."""
        try:
            prompt = f"""
            Analyze this tweet and create a funny, ironic, or witty meme response concept:
            
            Tweet: "{tweet_text}"
            Author: @{tweet_author}
            
            Generate a meme concept that:
            1. Is humorous and engaging (funny, ironic, or clever)
            2. Relates to the tweet's meaning/context
            3. Uses popular meme formats or creates relatable humor
            4. Is appropriate for social media (no offensive content)
            5. Supports or playfully contrasts the original post's meaning
            
            Return a JSON response with:
            {{
                "meme_type": "reaction/agreement/irony/observation",
                "text_top": "Top text for meme (short, punchy)",
                "text_bottom": "Bottom text for meme (punchline/reaction)",
                "description": "Visual concept/background description",
                "reply_text": "Accompanying tweet text (with relevant hashtags, max 240 chars)"
            }}
            
            Make it clever, relatable, and engaging!
            """
            
            if self.config.ai_provider == "openai":
                return self._analyze_with_openai(prompt)
            else:
                return self._analyze_with_gemini(prompt)
                
        except Exception as e:
            logger.error(f"Error analyzing tweet for meme: {str(e)}")
            return self._generate_fallback_meme(tweet_text)
    
    def _analyze_with_openai(self, prompt: str) -> Dict:
        """Analyze with OpenAI."""
        try:
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a witty meme creator who generates clever, funny responses to tweets. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Extract JSON if wrapped in markdown
                if "```json" in result:
                    json_start = result.find("```json") + 7
                    json_end = result.find("```", json_start)
                    result = result[json_start:json_end].strip()
                return json.loads(result)
                
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            raise
    
    def _analyze_with_gemini(self, prompt: str) -> Dict:
        """Analyze with Gemini."""
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=300
                )
            )
            
            result = response.text.strip()
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Extract JSON if wrapped in markdown
                if "```json" in result:
                    json_start = result.find("```json") + 7
                    json_end = result.find("```", json_start)
                    result = result[json_start:json_end].strip()
                return json.loads(result)
                
        except Exception as e:
            logger.error(f"Gemini analysis error: {str(e)}")
            raise
    
    def _generate_fallback_meme(self, tweet_text: str) -> Dict:
        """Generate fallback meme when AI fails."""
        fallback_memes = [
            {
                "meme_type": "reaction",
                "text_top": "ME READING THIS TWEET",
                "text_bottom": "INTERESTING...",
                "description": "Thoughtful reaction face",
                "reply_text": "This tweet hits different 🤔 #Thoughts #Twitter"
            },
            {
                "meme_type": "agreement", 
                "text_top": "EVERYONE NEEDS TO SEE",
                "text_bottom": "THIS TWEET",
                "description": "Pointing gesture",
                "reply_text": "Facts! 💯 Everyone needs to see this #Truth"
            },
            {
                "meme_type": "observation",
                "text_top": "WHEN SOMEONE DROPS",
                "text_bottom": "PURE WISDOM ON TWITTER",
                "description": "Mind blown reaction",
                "reply_text": "Mind = blown 🤯 This is pure wisdom right here #Wisdom"
            }
        ]
        
        import random
        return random.choice(fallback_memes)


class MemeGenerator:
    """Generates meme images based on concepts."""
    
    def __init__(self, config: Config):
        self.config = config
        
    def create_meme_image(self, meme_data: Dict, filename_prefix: str) -> str:
        """Create meme image from concept data."""
        try:
            # Create meme image dimensions (classic meme format)
            width, height = 600, 600
            
            # Use a solid color background or create simple visual
            background_color = self._get_background_color(meme_data.get("meme_type", "reaction"))
            
            # Create image
            image = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(image)
            
            # Load fonts
            try:
                # Try to load Impact font (classic meme font)
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial Black.ttf", 48)
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial Black.ttf", 44)
            except:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 48)
                    subtitle_font = ImageFont.truetype("arial.ttf", 44)
                except:
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
            
            # Text styling
            text_color = (255, 255, 255)  # White
            stroke_color = (0, 0, 0)  # Black outline
            stroke_width = 3
            
            # Top text
            top_text = meme_data.get("text_top", "").upper()
            if top_text:
                self._draw_meme_text(
                    draw, top_text, title_font, width, 60,
                    text_color, stroke_color, stroke_width
                )
            
            # Bottom text  
            bottom_text = meme_data.get("text_bottom", "").upper()
            if bottom_text:
                self._draw_meme_text(
                    draw, bottom_text, subtitle_font, width, height - 100,
                    text_color, stroke_color, stroke_width
                )
            
            # Add simple visual elements based on meme type
            self._add_visual_elements(draw, width, height, meme_data.get("meme_type", "reaction"))
            
            # Save image
            filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.config.image_output_dir, filename)
            
            image.save(filepath, 'PNG')
            logger.info(f"Generated meme image: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating meme image: {str(e)}")
            raise
    
    def _get_background_color(self, meme_type: str) -> tuple:
        """Get background color based on meme type."""
        colors = {
            "reaction": (70, 130, 180),     # Steel blue
            "agreement": (60, 179, 113),    # Medium sea green  
            "irony": (255, 140, 0),         # Dark orange
            "observation": (147, 112, 219), # Medium purple
            "default": (100, 100, 100)      # Gray
        }
        return colors.get(meme_type, colors["default"])
    
    def _draw_meme_text(self, draw, text: str, font, width: int, y_pos: int, 
                       text_color: tuple, stroke_color: tuple, stroke_width: int):
        """Draw meme text with outline."""
        # Wrap text if too long
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= width - 40:  # 20px margin each side
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = y_pos + (i * 55)  # Line spacing
            
            # Draw outline (stroke)
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=stroke_color)
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=text_color)
    
    def _add_visual_elements(self, draw, width: int, height: int, meme_type: str):
        """Add simple visual elements based on meme type."""
        # Add decorative elements based on meme type
        if meme_type == "reaction":
            # Add thinking/reaction elements
            self._draw_emoji_style(draw, "🤔", width - 80, height - 150)
        elif meme_type == "agreement":
            # Add agreement elements  
            self._draw_emoji_style(draw, "💯", 50, height - 150)
        elif meme_type == "irony":
            # Add irony elements
            self._draw_emoji_style(draw, "😏", width - 80, 50)
        elif meme_type == "observation":
            # Add observation elements
            self._draw_emoji_style(draw, "👀", 50, 50)
    
    def _draw_emoji_style(self, draw, emoji_text: str, x: int, y: int):
        """Draw emoji-style decoration (simplified)."""
        # For simplicity, we'll draw colored circles to represent emojis
        emoji_colors = {
            "🤔": (255, 215, 0),   # Gold
            "💯": (255, 69, 0),    # Red-orange  
            "😏": (255, 192, 203), # Pink
            "👀": (173, 216, 230)  # Light blue
        }
        
        color = emoji_colors.get(emoji_text, (200, 200, 200))
        draw.ellipse([x, y, x + 30, y + 30], fill=color)


class MemeReplyBot:
    """Main class for the meme reply bot."""
    
    def __init__(self):
        self.config = Config()
        self.twitter = TwitterPoster(self.config)
        self.analyzer = TweetAnalyzer(self.config)
        self.meme_gen = MemeGenerator(self.config)
    
    def get_tweet(self, tweet_id: str) -> Optional[Tuple[str, str]]:
        """Retrieve tweet content and author."""
        try:
            # Use Twitter API to get tweet
            tweet = self.twitter.client.get_tweet(
                tweet_id,
                expansions=['author_id'],
                user_fields=['username']
            )
            
            if tweet.data:
                tweet_text = tweet.data.text
                author_username = None
                
                # Get author username from includes
                if hasattr(tweet, 'includes') and tweet.includes and 'users' in tweet.includes:
                    for user in tweet.includes['users']:
                        if user.id == tweet.data.author_id:
                            author_username = user.username
                            break
                
                if not author_username:
                    author_username = "unknown"
                
                logger.info(f"Retrieved tweet from @{author_username}: {tweet_text[:50]}...")
                return tweet_text, author_username
            else:
                logger.error("Tweet not found or not accessible")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving tweet {tweet_id}: {str(e)}")
            return None
    
    def create_meme_reply(self, tweet_id: str, dry_run: bool = False) -> bool:
        """Create and post meme reply to a tweet."""
        try:
            logger.info(f"=== Creating meme reply for tweet {tweet_id} ===")
            
            # Step 1: Get the original tweet
            tweet_data = self.get_tweet(tweet_id)
            if not tweet_data:
                logger.error("Failed to retrieve tweet")
                return False
            
            tweet_text, author_username = tweet_data
            logger.info(f"Analyzing tweet from @{author_username}")
            
            # Step 2: Analyze tweet and generate meme concept
            meme_concept = self.analyzer.analyze_tweet_for_meme(tweet_text, author_username)
            logger.info(f"Generated meme concept: {meme_concept.get('meme_type', 'unknown')}")
            
            # Step 3: Create meme image
            meme_image_path = self.meme_gen.create_meme_image(
                meme_concept, 
                f"meme_reply_{tweet_id}"
            )
            
            # Step 4: Post reply (if not dry run)
            if dry_run:
                logger.info("DRY RUN - Would post reply:")
                logger.info(f"Reply text: {meme_concept.get('reply_text', '')}")
                logger.info(f"Meme image: {meme_image_path}")
                logger.info(f"Meme concept: {meme_concept}")
                return True
            else:
                # Post the meme reply
                reply_tweet_id = self.twitter.post_tweet(
                    text=meme_concept.get('reply_text', ''),
                    image_path=meme_image_path,
                    reply_to_tweet_id=tweet_id
                )
                
                logger.info(f"Successfully posted meme reply with ID: {reply_tweet_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating meme reply: {str(e)}")
            return False
    
    def run(self, tweet_id: str, dry_run: bool = False):
        """Main execution method."""
        try:
            success = self.create_meme_reply(tweet_id, dry_run)
            
            if success:
                logger.info("=== Meme reply generation completed successfully ===")
            else:
                logger.error("=== Meme reply generation failed ===")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Critical error in meme reply execution: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Twitter Meme Reply Bot")
    parser.add_argument(
        "tweet_id",
        help="Twitter status ID to reply to"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test mode - generate meme but don't post"
    )
    parser.add_argument(
        "--ai-provider",
        choices=["openai", "gemini"],
        default="gemini",
        help="AI provider to use for analysis"
    )
    
    args = parser.parse_args()
    
    # Set AI provider via environment variable
    os.environ['AI_PROVIDER'] = args.ai_provider
    
    bot = MemeReplyBot()
    bot.run(args.tweet_id, args.dry_run)