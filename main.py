#!/usr/bin/env python3
"""
Main script for the IgnorantStrength tweet generator.
Generates 3 daily posts with quotes and AI-generated images.
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict

from config import Config
from quote_generator import QuoteGenerator
from image_generator import ImageGenerator
from twitter_poster import TwitterPoster

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tweet_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TweetGenerator:
    """Main class for generating and posting tweets."""
    
    def __init__(self):
        self.config = Config()
        self.quote_gen = QuoteGenerator(self.config)
        self.image_gen = ImageGenerator(self.config)
        self.twitter = TwitterPoster(self.config)
        
    def generate_daily_posts(self) -> List[Dict]:
        """Generate 3 daily posts with quotes and images."""
        posts = []
        
        logger.info("Starting daily post generation for IgnorantStrength")
        
        for i in range(3):
            try:
                logger.info(f"Generating post {i+1}/3")
                
                # Generate quote based on "ignorant strength" theme
                quote = self.quote_gen.generate_quote()
                logger.info(f"Generated quote: {quote[:50]}...")
                
                # Generate image based on the quote
                image_path = self.image_gen.generate_image(quote, f"post_{i+1}_{datetime.now().strftime('%Y%m%d')}")
                logger.info(f"Generated image: {image_path}")
                
                posts.append({
                    'quote': quote,
                    'image_path': image_path,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error generating post {i+1}: {str(e)}")
                continue
                
        return posts
    
    def post_to_twitter(self, posts: List[Dict]) -> None:
        """Post the generated content to Twitter/X."""
        for i, post in enumerate(posts):
            try:
                logger.info(f"Posting to Twitter: post {i+1}")
                
                tweet_id = self.twitter.post_tweet(
                    text=post['quote'],
                    image_path=post['image_path']
                )
                
                logger.info(f"Successfully posted tweet ID: {tweet_id}")
                
            except Exception as e:
                logger.error(f"Error posting tweet {i+1}: {str(e)}")
                continue
    
    def run(self):
        """Main execution method."""
        try:
            logger.info("=== Starting IgnorantStrength Tweet Generator ===")
            
            # Generate posts
            posts = self.generate_daily_posts()
            
            if not posts:
                logger.error("No posts were generated successfully")
                return
                
            logger.info(f"Generated {len(posts)} posts successfully")
            
            # Post to Twitter if enabled
            if self.config.auto_post:
                self.post_to_twitter(posts)
            else:
                logger.info("Auto-posting disabled. Posts generated but not posted.")
                for i, post in enumerate(posts):
                    logger.info(f"Post {i+1}: {post['quote']}")
                    logger.info(f"Image: {post['image_path']}")
            
            logger.info("=== Tweet generation completed ===")
            
        except Exception as e:
            logger.error(f"Critical error in main execution: {str(e)}")
            raise


if __name__ == "__main__":
    generator = TweetGenerator()
    generator.run()