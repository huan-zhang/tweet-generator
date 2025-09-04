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
                "image_description": "Detailed visual description for AI image generation (background scene, characters, mood, style)",
                "reply_text": "Accompanying tweet text (NO hashtags, max 240 chars)"
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
                "image_description": "Person sitting at desk with thoughtful expression, rubbing chin while looking at computer screen, modern office background",
                "reply_text": "This tweet hits different 🤔"
            },
            {
                "meme_type": "agreement", 
                "text_top": "EVERYONE NEEDS TO SEE",
                "text_bottom": "THIS TWEET",
                "image_description": "Excited person pointing dramatically at their phone screen, bright background with emphasis rays",
                "reply_text": "Facts! 💯 Everyone needs to see this"
            },
            {
                "meme_type": "observation",
                "text_top": "WHEN SOMEONE DROPS",
                "text_bottom": "PURE WISDOM ON TWITTER",
                "image_description": "Person with mind-blown expression, hands on head, sparkles and light rays around their head, amazed facial expression",
                "reply_text": "Mind = blown 🤯 This is pure wisdom right here"
            }
        ]
        
        import random
        return random.choice(fallback_memes)


class MemeGenerator:
    """Generates AI-powered meme images based on concepts."""
    
    def __init__(self, config: Config):
        self.config = config
        self._setup_ai_client()
        
    def _setup_ai_client(self):
        """Initialize AI client for image generation."""
        if self.config.ai_provider == "openai":
            openai.api_key = self.config.openai_api_key
        elif self.config.ai_provider == "gemini":
            if self.config.gemini_api_key:
                genai.configure(api_key=self.config.gemini_api_key)
                # Use the new Google GenAI client for image generation
                from google import genai as google_genai
                self.genai_client = google_genai.Client(api_key=self.config.gemini_api_key)
        
    def create_meme_image(self, meme_data: Dict, filename_prefix: str) -> str:
        """Create AI-generated meme image from concept data."""
        try:
            # Create detailed prompt for meme image generation
            image_prompt = self._create_meme_image_prompt(meme_data)
            logger.info(f"Generating AI meme image: {meme_data.get('meme_type', 'unknown')} type")
            
            # Generate the base image using AI
            if self.config.ai_provider == "gemini" and self.config.gemini_api_key:
                base_image_path = self._generate_with_gemini(image_prompt, filename_prefix)
            elif self.config.openai_api_key:
                base_image_path = self._generate_with_dalle(image_prompt, filename_prefix)
            else:
                # Fallback to text-based meme if no AI image generation available
                logger.warning("No AI image generation available, creating text-based meme")
                return self._create_text_based_meme(meme_data, filename_prefix)
            
            # Add meme text overlay to the AI-generated image
            final_image_path = self._add_meme_text_overlay(
                base_image_path, 
                meme_data.get("text_top", ""),
                meme_data.get("text_bottom", ""),
                filename_prefix
            )
            
            logger.info(f"Generated AI meme image: {final_image_path}")
            return final_image_path
            
        except Exception as e:
            logger.error(f"Error creating AI meme image: {str(e)}")
            logger.info("Falling back to text-based meme")
            return self._create_text_based_meme(meme_data, filename_prefix)
    
    def _create_meme_image_prompt(self, meme_data: Dict) -> str:
        """Create detailed prompt for AI image generation."""
        image_description = meme_data.get("image_description", "")
        meme_type = meme_data.get("meme_type", "reaction")
        
        prompt = f"""
        Create a meme-style image with the following characteristics:
        
        Scene: {image_description}
        
        Style requirements:
        - High quality, clear, well-lit image
        - Meme-appropriate composition and framing
        - Expressive facial expressions and body language
        - Clean background suitable for text overlay
        - Vibrant, engaging colors
        - No existing text or words in the image
        - Leave space at top and bottom for text overlay
        - Professional photography or digital art style
        
        The image should convey a {meme_type} mood and be perfect for adding meme text over it.
        """
        
        return prompt.strip()
    
    def _generate_with_dalle(self, prompt: str, filename_prefix: str) -> str:
        """Generate image using DALL-E."""
        try:
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download and save the image
            filename = f"{filename_prefix}_base_{datetime.now().strftime('%H%M%S')}.png"
            filepath = os.path.join(self.config.image_output_dir, filename)
            
            response_img = requests.get(image_url, timeout=30)
            response_img.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response_img.content)
            
            return filepath
            
        except Exception as e:
            logger.error(f"DALL-E generation error: {str(e)}")
            raise
    
    def _generate_with_gemini(self, prompt: str, filename_prefix: str) -> str:
        """Generate image using Gemini 2.5 Flash image generation."""
        try:
            from google.genai import types
            
            response = self.genai_client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["Text", "Image"]
                )
            )
            
            # Extract the image from response
            image_data = None
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    break
            
            if not image_data:
                raise Exception("No image data returned from Gemini")
            
            # Save the image
            filename = f"{filename_prefix}_base_{datetime.now().strftime('%H%M%S')}.png"
            filepath = os.path.join(self.config.image_output_dir, filename)
            
            # Convert bytes to PIL Image and save
            from io import BytesIO
            image = Image.open(BytesIO(image_data))
            image.save(filepath, 'PNG')
            
            return filepath
            
        except Exception as e:
            logger.error(f"Gemini image generation error: {str(e)}")
            raise
    
    def _add_meme_text_overlay(self, base_image_path: str, top_text: str, bottom_text: str, filename_prefix: str) -> str:
        """Add meme text overlay to the generated image."""
        try:
            # Open the base image
            image = Image.open(base_image_path)
            draw = ImageDraw.Draw(image)
            
            width, height = image.size
            
            # Load fonts
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial Black.ttf", int(width * 0.08))
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial Black.ttf", int(width * 0.075))
            except:
                try:
                    title_font = ImageFont.truetype("arial.ttf", int(width * 0.08))
                    subtitle_font = ImageFont.truetype("arial.ttf", int(width * 0.075))
                except:
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
            
            # Text styling
            text_color = (255, 255, 255)  # White
            stroke_color = (0, 0, 0)  # Black outline
            stroke_width = max(2, int(width * 0.005))  # Scale stroke with image size
            
            # Add top text
            if top_text:
                self._draw_meme_text(
                    draw, top_text.upper(), title_font, width, int(height * 0.1),
                    text_color, stroke_color, stroke_width
                )
            
            # Add bottom text
            if bottom_text:
                self._draw_meme_text(
                    draw, bottom_text.upper(), subtitle_font, width, int(height * 0.85),
                    text_color, stroke_color, stroke_width
                )
            
            # Save final meme image
            final_filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            final_filepath = os.path.join(self.config.image_output_dir, final_filename)
            
            image.save(final_filepath, 'PNG')
            
            # Clean up base image
            try:
                os.remove(base_image_path)
            except:
                pass
            
            return final_filepath
            
        except Exception as e:
            logger.error(f"Error adding text overlay: {str(e)}")
            raise
    
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
            
            if text_width <= width - (width * 0.1):  # 5% margin each side
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
        line_height = int(width * 0.08)  # Scale line height with image
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = y_pos + (i * line_height)
            
            # Draw outline (stroke)
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=stroke_color)
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=text_color)
    
    def _create_text_based_meme(self, meme_data: Dict, filename_prefix: str) -> str:
        """Fallback: create simple text-based meme."""
        try:
            width, height = 600, 600
            background_color = (100, 100, 100)  # Gray background
            
            image = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(image)
            
            # Load fonts
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial Black.ttf", 48)
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial Black.ttf", 44)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            text_color = (255, 255, 255)
            stroke_color = (0, 0, 0)
            stroke_width = 3
            
            # Add texts
            top_text = meme_data.get("text_top", "").upper()
            bottom_text = meme_data.get("text_bottom", "").upper()
            
            if top_text:
                self._draw_meme_text(draw, top_text, title_font, width, 60, text_color, stroke_color, stroke_width)
            if bottom_text:
                self._draw_meme_text(draw, bottom_text, subtitle_font, width, height - 100, text_color, stroke_color, stroke_width)
            
            # Save image
            filename = f"{filename_prefix}_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.config.image_output_dir, filename)
            image.save(filepath, 'PNG')
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating text-based meme: {str(e)}")
            raise


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