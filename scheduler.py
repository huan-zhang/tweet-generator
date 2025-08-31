"""
Scheduler module for automating daily tweet generation and posting.
Supports both immediate execution and scheduled runs.
"""

import logging
import schedule
import time
import signal
import sys
from datetime import datetime, timedelta
from typing import List
import json
import os

from main import TweetGenerator

logger = logging.getLogger(__name__)


class TweetScheduler:
    """Handles scheduling of tweet generation and posting."""
    
    def __init__(self):
        self.tweet_generator = TweetGenerator()
        self.running = False
        self.post_history_file = "post_history.json"
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False
        sys.exit(0)
    
    def schedule_daily_posts(self):
        """Schedule daily posts at configured times."""
        config = self.tweet_generator.config
        
        logger.info(f"Scheduling story posts twice daily at: {config.post_times}")
        
        # Clear any existing jobs
        schedule.clear()
        
        # Schedule posts at specified times (every 8 hours)
        for post_time in config.post_times:
            schedule.every().day.at(post_time).do(self._run_daily_generation)
            logger.info(f"Scheduled story post at {post_time} (twice daily)")
        
        # Optional: Schedule a test run every hour during development
        # schedule.every().hour.do(self._run_test_generation)
    
    def _run_daily_generation(self):
        """Run scheduled story generation (twice daily)."""
        try:
            logger.info("Starting scheduled story generation")
            
            # Check if we've already posted in this time slot
            if self._already_posted_in_time_slot():
                logger.info("Already posted in this 12-hour time slot. Skipping.")
                return
            
            # Generate single story post for this time slot
            post = self.tweet_generator.generate_single_post()
            
            if post:
                # Post to Twitter if enabled
                if self.tweet_generator.config.auto_post:
                    self.tweet_generator.post_to_twitter([post])
                    logger.info("Story posted to Twitter")
                else:
                    logger.info("Auto-posting disabled. Story generated but not posted.")
                    logger.info(f"Story: {post['story']}")
                
                # Record the post
                self._record_post(post)
                
                logger.info("Scheduled story generation completed successfully")
            else:
                logger.error("No story generated during scheduled run")
                
        except Exception as e:
            logger.error(f"Error during scheduled story generation: {str(e)}")
    
    def _run_test_generation(self):
        """Run a test generation (for development)."""
        logger.info("Running test generation (development mode)")
        try:
            # Generate one test post
            story = self.tweet_generator.story_gen.generate_story()
            logger.info(f"Test story generated: {story}")
            
            # Don't post during test runs
            logger.info("Test generation completed (not posted)")
            
        except Exception as e:
            logger.error(f"Error during test generation: {str(e)}")
    
    def _already_posted_in_time_slot(self) -> bool:
        """Check if we've already posted in this 12-hour time slot."""
        try:
            if not os.path.exists(self.post_history_file):
                return False
            
            with open(self.post_history_file, 'r') as f:
                history = json.load(f)
            
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # Define 12-hour time slots: 0-11 (morning), 12-23 (evening)
            if 0 <= current_hour < 12:
                time_slot = "morning"  # 00:00 - 11:59
            else:
                time_slot = "evening"  # 12:00 - 23:59
            
            today = current_time.strftime('%Y-%m-%d')
            
            # Check if we have a post for today in the current time slot
            for post in history.get('posts', []):
                post_date = post.get('date')
                if post_date != today:
                    continue
                    
                post_time = datetime.fromisoformat(post.get('timestamp', ''))
                post_hour = post_time.hour
                
                # Determine which time slot the post was in
                if 0 <= post_hour < 12:
                    post_slot = "morning"
                else:
                    post_slot = "evening"
                
                if post_slot == time_slot:
                    logger.info(f"Found existing post in {time_slot} slot at {post_time.strftime('%H:%M')}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking post history: {str(e)}")
            return False
    
    def _record_post(self, post: dict):
        """Record a post in the history file."""
        try:
            history = {'posts': []}
            
            if os.path.exists(self.post_history_file):
                with open(self.post_history_file, 'r') as f:
                    history = json.load(f)
            
            # Add new post record
            post_record = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': post.get('timestamp', datetime.now().isoformat()),
                'story': post.get('story', '')[:100],  # Truncate for storage
                'image_path': post.get('image_path', ''),
                'posted_at': datetime.now().isoformat()
            }
            
            history['posts'].append(post_record)
            
            # Keep only last 30 days of history
            cutoff_date = datetime.now() - timedelta(days=30)
            history['posts'] = [
                p for p in history['posts']
                if datetime.fromisoformat(p['posted_at']) > cutoff_date
            ]
            
            with open(self.post_history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info("Post recorded in history")
            
        except Exception as e:
            logger.error(f"Error recording post: {str(e)}")
    
    def run_scheduler(self):
        """Run the scheduler loop."""
        self.running = True
        logger.info("Tweet scheduler started")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
        finally:
            self.running = False
            logger.info("Tweet scheduler stopped")
    
    def run_immediate(self):
        """Run tweet generation immediately (for testing)."""
        logger.info("Running immediate tweet generation")
        
        try:
            posts = self.tweet_generator.generate_daily_posts()
            
            if posts:
                logger.info(f"Generated {len(posts)} posts:")
                for i, post in enumerate(posts, 1):
                    logger.info(f"Post {i}: {post['story']}")
                    logger.info(f"Image: {post['image_path']}")
                    
                    # Record each post
                    self._record_post(post)
                
                # Post to Twitter if enabled
                if self.tweet_generator.config.auto_post:
                    self.tweet_generator.post_to_twitter(posts)
                    logger.info("Posts sent to Twitter")
                else:
                    logger.info("Auto-posting disabled. Posts generated but not posted.")
            else:
                logger.error("No posts were generated")
                
        except Exception as e:
            logger.error(f"Error during immediate generation: {str(e)}")
            raise
    
    def get_post_history(self, days: int = 7) -> List[dict]:
        """Get post history for the last N days."""
        try:
            if not os.path.exists(self.post_history_file):
                return []
            
            with open(self.post_history_file, 'r') as f:
                history = json.load(f)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            recent_posts = [
                post for post in history.get('posts', [])
                if datetime.fromisoformat(post['posted_at']) > cutoff_date
            ]
            
            # Sort by timestamp, most recent first
            recent_posts.sort(
                key=lambda x: datetime.fromisoformat(x['posted_at']),
                reverse=True
            )
            
            return recent_posts
            
        except Exception as e:
            logger.error(f"Error getting post history: {str(e)}")
            return []


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="IgnorantStrength Tweet Scheduler")
    parser.add_argument(
        '--mode',
        choices=['schedule', 'immediate', 'history'],
        default='immediate',
        help='Operation mode: schedule (run scheduler), immediate (run once), history (show recent posts)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of history to show (for history mode)'
    )
    
    args = parser.parse_args()
    
    scheduler = TweetScheduler()
    
    if args.mode == 'schedule':
        scheduler.schedule_daily_posts()
        scheduler.run_scheduler()
    elif args.mode == 'immediate':
        scheduler.run_immediate()
    elif args.mode == 'history':
        history = scheduler.get_post_history(args.days)
        print(f"\nPost history for last {args.days} days:")
        print("=" * 50)
        for post in history:
            print(f"Date: {post['date']}")
            print(f"Story: {post['story']}")
            print(f"Image: {post['image_path']}")
            print(f"Posted at: {post['posted_at']}")
            print("-" * 30)