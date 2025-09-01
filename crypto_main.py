#!/usr/bin/env python3
"""
Crypto prediction tweet generator.
Generates and posts crypto price predictions to Twitter/X.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict

from config import Config
from crypto_predictor import CryptoPredictor
from image_generator import ImageGenerator
from twitter_poster import TwitterPoster

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_predictions.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CryptoTweetGenerator:
    """Main class for generating and posting crypto prediction tweets."""
    
    def __init__(self):
        self.config = Config()
        self.crypto_predictor = CryptoPredictor(self.config)
        self.image_gen = ImageGenerator(self.config)
        self.twitter = TwitterPoster(self.config)
    
    def generate_crypto_post(self) -> Dict:
        """Generate a single crypto prediction post."""
        logger.info("Generating crypto prediction post")
        
        try:
            # Generate crypto prediction
            prediction = self.crypto_predictor.generate_prediction()
            logger.info(f"Generated prediction: {prediction[:50]}...")
            
            # Generate image based on the prediction
            image_path = self.image_gen.generate_image(
                prediction, 
                f"crypto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            logger.info(f"Generated image: {image_path}")
            
            post = {
                'prediction': prediction,
                'image_path': image_path,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("Successfully generated crypto prediction post")
            return post
            
        except Exception as e:
            logger.error(f"Error generating crypto post: {str(e)}")
            raise
    
    def post_to_twitter(self, post: Dict) -> None:
        """Post the crypto prediction to Twitter/X."""
        try:
            logger.info("Posting crypto prediction to Twitter")
            
            tweet_id = self.twitter.post_tweet(
                text=post['prediction'],
                image_path=post['image_path']
            )
            
            logger.info(f"Successfully posted crypto prediction tweet ID: {tweet_id}")
            
        except Exception as e:
            logger.error(f"Error posting crypto tweet: {str(e)}")
            raise
    
    def run(self):
        """Main execution method."""
        try:
            logger.info("=== Starting Crypto Prediction Generator ===")
            
            # Generate crypto prediction post
            post = self.generate_crypto_post()
            
            # Post to Twitter if enabled
            if self.config.auto_post:
                self.post_to_twitter(post)
            else:
                logger.info("Auto-posting disabled. Prediction generated but not posted.")
                logger.info(f"Prediction: {post['prediction']}")
                logger.info(f"Image: {post['image_path']}")
            
            logger.info("=== Crypto prediction generation completed ===")
            
        except Exception as e:
            logger.error(f"Critical error in crypto prediction execution: {str(e)}")
            raise


if __name__ == "__main__":
    generator = CryptoTweetGenerator()
    generator.run()