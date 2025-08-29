"""
Twitter/X posting module for publishing generated content.
Handles authentication and media uploads.
"""

import logging
import os
from typing import Optional
import tweepy

logger = logging.getLogger(__name__)


class TwitterPoster:
    """Handles posting tweets with images to Twitter/X."""
    
    def __init__(self, config):
        self.config = config
        self.api = None
        self.client = None
        
        if self.config.auto_post:
            self._setup_twitter_clients()
    
    def _setup_twitter_clients(self):
        """Initialize Twitter API clients."""
        try:
            # Try OAuth 2.0 first (Client ID/Secret)
            if self.config.twitter_client_id and self.config.twitter_client_secret:
                logger.info("Attempting OAuth 2.0 setup with Client ID/Secret")
                self.client = tweepy.Client(
                    bearer_token=self.config.twitter_bearer_token,
                    consumer_key=self.config.twitter_api_key,
                    consumer_secret=self.config.twitter_api_secret,
                    access_token=self.config.twitter_access_token,
                    access_token_secret=self.config.twitter_access_token_secret,
                    wait_on_rate_limit=True
                )
                
                # For media upload, we still need OAuth 1.0a API
                if (self.config.twitter_api_key and self.config.twitter_api_secret and 
                    self.config.twitter_access_token and self.config.twitter_access_token_secret):
                    auth = tweepy.OAuth1UserHandler(
                        consumer_key=self.config.twitter_api_key,
                        consumer_secret=self.config.twitter_api_secret,
                        access_token=self.config.twitter_access_token,
                        access_token_secret=self.config.twitter_access_token_secret
                    )
                    self.api = tweepy.API(auth)
                    logger.info("Using hybrid OAuth 2.0 + OAuth 1.0a for media upload")
                else:
                    logger.warning("No OAuth 1.0a credentials - media upload will not work")
                    self.api = None
                    
            # Fallback to OAuth 1.0a only
            elif (self.config.twitter_api_key and self.config.twitter_api_secret and 
                  self.config.twitter_access_token and self.config.twitter_access_token_secret):
                logger.info("Using OAuth 1.0a authentication")
                auth = tweepy.OAuth1UserHandler(
                    consumer_key=self.config.twitter_api_key,
                    consumer_secret=self.config.twitter_api_secret,
                    access_token=self.config.twitter_access_token,
                    access_token_secret=self.config.twitter_access_token_secret
                )
                self.api = tweepy.API(auth)
                
                self.client = tweepy.Client(
                    bearer_token=self.config.twitter_bearer_token,
                    consumer_key=self.config.twitter_api_key,
                    consumer_secret=self.config.twitter_api_secret,
                    access_token=self.config.twitter_access_token,
                    access_token_secret=self.config.twitter_access_token_secret,
                    wait_on_rate_limit=True
                )
            else:
                raise ValueError("No valid Twitter authentication credentials provided")
            
            # Test authentication
            self._test_authentication()
            
            logger.info("Twitter API clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API clients: {str(e)}")
            raise
    
    def _test_authentication(self):
        """Test Twitter API authentication."""
        try:
            # Test API v2 first (more reliable)
            if self.client:
                me = self.client.get_me()
                logger.info(f"Authenticated as: @{me.data.username}")
            
            # Test API v1.1 if available
            if self.api:
                self.api.verify_credentials()
                logger.info("OAuth 1.0a API verified successfully")
            
        except Exception as e:
            logger.error(f"Twitter authentication failed: {str(e)}")
            raise
    
    def post_tweet(self, text: str, image_path: Optional[str] = None) -> str:
        """Post a tweet with optional image."""
        if not self.config.auto_post:
            logger.info("Auto-post disabled. Would have posted:")
            logger.info(f"Text: {text}")
            if image_path:
                logger.info(f"Image: {image_path}")
            return "dry_run_tweet_id"
        
        try:
            media_id = None
            
            # Try to upload image if provided, but continue without it if it fails
            if image_path and os.path.exists(image_path):
                try:
                    media_id = self._upload_media(image_path)
                    logger.info(f"Media uploaded with ID: {media_id}")
                except Exception as media_error:
                    logger.warning(f"Failed to upload media, posting text-only: {media_error}")
                    media_id = None
            
            # Post tweet
            tweet_params = {"text": text}
            if media_id:
                tweet_params["media_ids"] = [media_id]
            
            response = self.client.create_tweet(**tweet_params)
            tweet_id = response.data['id']
            
            logger.info(f"Successfully posted tweet ID: {tweet_id}")
            logger.info(f"Tweet text: {text}")
            
            return tweet_id
            
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            raise
    
    def _upload_media(self, image_path: str) -> str:
        """Upload media file to Twitter."""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Check file size (Twitter limit is 5MB for images)
            file_size = os.path.getsize(image_path)
            max_size = 5 * 1024 * 1024  # 5MB
            
            if file_size > max_size:
                logger.warning(f"Image file size ({file_size} bytes) exceeds Twitter limit ({max_size} bytes)")
                # Could implement image compression here if needed
            
            media = self.api.media_upload(image_path)
            
            logger.info(f"Successfully uploaded media: {image_path}")
            return media.media_id_string
            
        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            raise
    
    def post_thread(self, tweets: list) -> list:
        """Post a thread of tweets."""
        if not tweets:
            return []
        
        tweet_ids = []
        reply_to_tweet_id = None
        
        for i, tweet_data in enumerate(tweets):
            try:
                text = tweet_data.get('text', '')
                image_path = tweet_data.get('image_path')
                
                media_id = None
                if image_path and os.path.exists(image_path):
                    media_id = self._upload_media(image_path)
                
                # Prepare tweet parameters
                tweet_params = {"text": text}
                if media_id:
                    tweet_params["media_ids"] = [media_id]
                if reply_to_tweet_id:
                    tweet_params["in_reply_to_tweet_id"] = reply_to_tweet_id
                
                response = self.client.create_tweet(**tweet_params)
                tweet_id = response.data['id']
                tweet_ids.append(tweet_id)
                
                # Set this tweet as the parent for the next one
                reply_to_tweet_id = tweet_id
                
                logger.info(f"Posted tweet {i+1}/{len(tweets)} with ID: {tweet_id}")
                
            except Exception as e:
                logger.error(f"Error posting tweet {i+1} in thread: {str(e)}")
                # Continue with remaining tweets
                continue
        
        return tweet_ids
    
    def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet by ID."""
        try:
            if not self.config.auto_post:
                logger.info(f"Auto-post disabled. Would have deleted tweet ID: {tweet_id}")
                return True
            
            self.client.delete_tweet(tweet_id)
            logger.info(f"Successfully deleted tweet ID: {tweet_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting tweet {tweet_id}: {str(e)}")
            return False
    
    def get_account_info(self) -> dict:
        """Get account information."""
        try:
            if not self.client:
                return {"error": "Twitter client not initialized"}
            
            me = self.client.get_me(user_fields=["public_metrics", "description"])
            
            return {
                "username": me.data.username,
                "name": me.data.name,
                "id": me.data.id,
                "description": me.data.description,
                "followers_count": me.data.public_metrics.get("followers_count", 0),
                "following_count": me.data.public_metrics.get("following_count", 0),
                "tweet_count": me.data.public_metrics.get("tweet_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return {"error": str(e)}