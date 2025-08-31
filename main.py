#!/usr/bin/env python3
"""
Main script for the IgnorantStrength tweet generator.
Generates 3 daily posts with quotes and AI-generated images.
"""

import os
import sys
import logging
import re
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
    
    def _split_story_into_tweets(self, story: str) -> List[str]:
        """Split a long story into Twitter-sized chunks for threading."""
        if len(story) <= self.config.thread_max_length:
            return [story]
        
        # Find hashtags at the end
        hashtags = ""
        hashtag_match = re.search(r'(\s+#\w+(?:\s+#\w+)*)\s*$', story)
        if hashtag_match:
            hashtags = hashtag_match.group(1)
            story = story[:hashtag_match.start()].strip()
        
        # Improved sentence splitting using regex
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, story)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Group sentences into tweets with better logic
        tweets = []
        current_tweet = ""
        thread_number_space = 10  # Reserve space for " (X/Y)" numbering
        available_space = self.config.thread_max_length - thread_number_space
        
        for sentence in sentences:
            # For the last tweet, also reserve space for hashtags
            is_last_sentence = sentence == sentences[-1]
            hashtag_space = len(hashtags) if is_last_sentence else 0
            actual_space = available_space - hashtag_space
            
            # Check if adding this sentence would exceed limit
            if current_tweet:
                test_tweet = current_tweet + " " + sentence
            else:
                test_tweet = sentence
            
            if len(test_tweet) <= actual_space:
                current_tweet = test_tweet
            else:
                # If current tweet has content, save it and start new one
                if current_tweet:
                    tweets.append(current_tweet.strip())
                    current_tweet = sentence
                else:
                    # Single sentence is too long, need to split it
                    words = sentence.split()
                    current_tweet = ""
                    for word in words:
                        test_with_word = current_tweet + " " + word if current_tweet else word
                        if len(test_with_word) <= actual_space:
                            current_tweet = test_with_word
                        else:
                            if current_tweet:
                                tweets.append(current_tweet.strip())
                            current_tweet = word
                    # Don't reset current_tweet here as it contains the remaining words
        
        # Add the last tweet if there's content
        if current_tweet:
            tweets.append(current_tweet.strip())
        
        # Add hashtags only to the last tweet
        if tweets and hashtags:
            tweets[-1] += hashtags
        
        # Add thread numbering only if we have multiple tweets
        if len(tweets) > 1:
            for i in range(len(tweets)):
                tweets[i] = f"{tweets[i]} ({i+1}/{len(tweets)})"
        
        return tweets


    def post_to_twitter(self, posts: List[Dict]) -> None:
        """Post the generated content to Twitter/X."""
        for i, post in enumerate(posts):
            try:
                logger.info(f"Posting to Twitter: post {i+1}")
                
                # Check if story needs to be split into threads
                if self.config.use_threads and len(post['story']) > self.config.thread_max_length:
                    tweet_parts = self._split_story_into_tweets(post['story'])
                    logger.info(f"Story is long, posting as thread with {len(tweet_parts)} tweets")
                    
                    thread_tweets = []
                    for j, part in enumerate(tweet_parts):
                        thread_tweets.append({
                            'text': part,
                            'image_path': post['image_path'] if j == 0 else None
                        })
                    
                    tweet_ids = self.twitter.post_thread(thread_tweets)
                    logger.info(f"Successfully posted thread with IDs: {tweet_ids}")
                    
                else:
                    # Post as single tweet
                    tweet_id = self.twitter.post_tweet(
                        text=post['story'],
                        image_path=post['image_path']
                    )
                    logger.info(f"Successfully posted single tweet ID: {tweet_id}")
                
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