"""
Image generation module supporting both OpenAI DALL-E and other AI models.
Creates inspirational images based on generated quotes.
"""

import logging
import os
import requests
from datetime import datetime
from typing import Optional
import openai
from PIL import Image, ImageDraw, ImageFont
import textwrap

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generates images for quotes using AI models."""
    
    def __init__(self, config):
        self.config = config
        self._setup_ai_client()
    
    def _setup_ai_client(self):
        """Initialize the AI client based on the configured provider."""
        if self.config.ai_provider == "openai":
            openai.api_key = self.config.openai_api_key
    
    def generate_image(self, story: str, filename_prefix: str) -> str:
        """Generate an image based on the story."""
        try:
            # Clean story for image prompt (remove hashtags)
            clean_story = self._clean_story_for_prompt(story)
            
            if self.config.ai_provider == "openai":
                return self._generate_with_dalle(clean_story, filename_prefix)
            else:
                # Fallback to text-based image if AI generation is not available
                return self._generate_text_image(story, filename_prefix)
                
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            # Fallback to text-based image
            return self._generate_text_image(story, filename_prefix)
    
    def _clean_story_for_prompt(self, story: str) -> str:
        """Clean the story for use in image generation prompts."""
        # Remove hashtags and extra whitespace
        lines = story.split('\n')
        clean_lines = []
        
        for line in lines:
            if not line.strip().startswith('#'):
                clean_lines.append(line.strip())
        
        clean_story = ' '.join(clean_lines).strip()
        
        # Remove hashtags that might be at the end
        words = clean_story.split()
        filtered_words = [word for word in words if not word.startswith('#')]
        
        return ' '.join(filtered_words)
    
    def _generate_with_dalle(self, story: str, filename_prefix: str) -> str:
        """Generate image using OpenAI DALL-E."""
        try:
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            # Create image prompt
            image_prompt = self.config.image_prompt_template.format(
                story=story,
                style=self.config.image_style
            )
            
            logger.info(f"Generating image with DALL-E for story: {story[:50]}...")
            
            response = client.images.generate(
                model=self.config.image_model,
                prompt=image_prompt,
                size=self.config.image_size,
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download and save the image
            filename = f"{filename_prefix}_{datetime.now().strftime('%H%M%S')}.png"
            filepath = os.path.join(self.config.image_output_dir, filename)
            
            self._download_image(image_url, filepath)
            
            logger.info(f"Successfully generated image: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"DALL-E generation error: {str(e)}")
            raise
    
    def _download_image(self, url: str, filepath: str) -> None:
        """Download image from URL and save to file."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
    
    def _generate_text_image(self, story: str, filename_prefix: str) -> str:
        """Generate a simple text-based image as fallback."""
        try:
            # Create image dimensions
            width, height = 1080, 1080
            background_color = (25, 35, 50)  # Dark navy for stories
            text_color = (255, 255, 255)  # White
            
            # Create image
            image = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(image)
            
            # Clean story for display (remove hashtags)
            display_story = self._clean_story_for_display(story)
            
            # Try to load a font, fallback to default if not available
            try:
                font_size = 48
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Wrap text to fit image
            margin = 100
            max_width = width - (margin * 2)
            
            # Simple text wrapping
            words = display_story.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)  # Single word too long
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Calculate text height and position
            total_text_height = len(lines) * font_size * 1.2
            start_y = (height - total_text_height) // 2
            
            # Draw text
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + (i * font_size * 1.2)
                
                draw.text((x, y), line, font=font, fill=text_color)
            
            # Add decorative elements
            self._add_decorative_elements(draw, width, height)
            
            # Save image
            filename = f"{filename_prefix}_text_{datetime.now().strftime('%H%M%S')}.png"
            filepath = os.path.join(self.config.image_output_dir, filename)
            
            image.save(filepath, 'PNG')
            
            logger.info(f"Generated text-based image: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating text image: {str(e)}")
            raise
    
    def _clean_story_for_display(self, story: str) -> str:
        """Clean story for display on image."""
        # Remove hashtags
        words = story.split()
        filtered_words = [word for word in words if not word.startswith('#')]
        return ' '.join(filtered_words).strip()
    
    def _add_decorative_elements(self, draw: ImageDraw.Draw, width: int, height: int):
        """Add simple decorative elements to the image."""
        # Add a subtle border
        border_color = (100, 110, 130)
        border_width = 3
        
        # Top and bottom borders
        draw.rectangle([50, 50, width-50, 50+border_width], fill=border_color)
        draw.rectangle([50, height-50-border_width, width-50, height-50], fill=border_color)
        
        # Corner decorations
        corner_size = 20
        corner_color = (150, 160, 180)
        
        # Top-left corner
        draw.rectangle([50, 50, 50+corner_size, 50+corner_size], fill=corner_color)
        # Top-right corner
        draw.rectangle([width-50-corner_size, 50, width-50, 50+corner_size], fill=corner_color)
        # Bottom-left corner
        draw.rectangle([50, height-50-corner_size, 50+corner_size, height-50], fill=corner_color)
        # Bottom-right corner
        draw.rectangle([width-50-corner_size, height-50-corner_size, width-50, height-50], fill=corner_color)