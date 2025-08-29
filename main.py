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
from story_generator import StoryGenerator
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
    """Main class for generating and posting story tweets."""
    
    def __init__(self):
        self.config = Config()
        self.story_gen = StoryGenerator(self.config)
        self.image_gen = ImageGenerator(self.config)
        self.twitter = TwitterPoster(self.config)
        
    def generate_single_post(self) -> Dict:
        """Generate a single post with story and image."""
        logger.info("Generating single story post")
        
        try:
            # Generate story on random topic
            story = self.story_gen.generate_story()
            logger.info(f"Generated story: {story[:50]}...")
            
            # Generate image based on the story
            image_path = self.image_gen.generate_image(story, f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Generated image: {image_path}")
            
            post = {
                'story': story,
                'image_path': image_path,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("Successfully generated single story post")
            return post
            
        except Exception as e:
            logger.error(f"Error generating post: {str(e)}")
            raise
    
    def generate_daily_posts(self) -> List[Dict]:
        """Generate multiple posts (for scheduler use)."""
        posts = []
        
        logger.info("Starting daily story post generation")
        
        for i in range(self.config.posts_per_day):
            try:
                logger.info(f"Generating story post {i+1}/{self.config.posts_per_day}")
                
                # Generate story on random topic
                story = self.story_gen.generate_story()
                logger.info(f"Generated story: {story[:50]}...")
                
                # Generate image based on the story
                image_path = self.image_gen.generate_image(story, f"story_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                logger.info(f"Generated image: {image_path}")
                
                posts.append({
                    'story': story,
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
                    text=post['story'],
                    image_path=post['image_path']
                )
                
                logger.info(f"Successfully posted tweet ID: {tweet_id}")
                
            except Exception as e:
                logger.error(f"Error posting tweet {i+1}: {str(e)}")
                continue
    
    def run(self):
        """Main execution method."""
        try:
            logger.info("=== Starting Story Tweet Generator ===")
            
            # Generate single post
            post = self.generate_single_post()
            
            # Post to Twitter if enabled
            if self.config.auto_post:
                self.post_to_twitter([post])
            else:
                logger.info("Auto-posting disabled. Post generated but not posted.")
                logger.info(f"Story: {post['story']}")
                logger.info(f"Image: {post['image_path']}")
            
            logger.info("=== Story generation completed ===")
            
        except Exception as e:
            logger.error(f"Critical error in main execution: {str(e)}")
            raise


if __name__ == "__main__":
    generator = TweetGenerator()
    generator.run()