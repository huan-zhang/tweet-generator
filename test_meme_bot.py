#!/usr/bin/env python3
"""
Test script for meme reply bot functionality.
"""

import os
import sys
from config import Config
from meme_reply_bot import TweetAnalyzer, MemeGenerator

def test_meme_generation():
    """Test meme generation without needing real tweets."""
    
    # Set up config
    os.environ['AI_PROVIDER'] = 'gemini'
    os.environ['AUTO_POST'] = 'false'
    
    config = Config()
    
    # Test tweet examples
    test_tweets = [
        {
            "text": "Just spent 3 hours debugging code only to realize I forgot a semicolon 😅",
            "author": "developer_life"
        },
        {
            "text": "Bitcoin is going to the moon! 🚀🌙 #BTC #ToTheMoon",
            "author": "crypto_enthusiast"
        },
        {
            "text": "Coffee is the fuel of productivity ☕ Can't function without my morning cup!",
            "author": "coffee_lover"
        },
        {
            "text": "Why do Monday mornings exist? Asking for a friend... 😴",
            "author": "monday_blues"
        }
    ]
    
    print("Testing Meme Analysis and Generation")
    print("=" * 50)
    
    # Test analyzer
    analyzer = TweetAnalyzer(config)
    meme_gen = MemeGenerator(config)
    
    for i, tweet in enumerate(test_tweets, 1):
        print(f"\n--- Test {i} ---")
        print(f"Original Tweet: {tweet['text']}")
        print(f"Author: @{tweet['author']}")
        
        try:
            # Analyze tweet
            meme_concept = analyzer.analyze_tweet_for_meme(tweet['text'], tweet['author'])
            
            print(f"Meme Type: {meme_concept.get('meme_type', 'N/A')}")
            print(f"Top Text: {meme_concept.get('text_top', 'N/A')}")
            print(f"Bottom Text: {meme_concept.get('text_bottom', 'N/A')}")
            print(f"Reply Text: {meme_concept.get('reply_text', 'N/A')}")
            
            # Generate meme image
            image_path = meme_gen.create_meme_image(meme_concept, f"test_meme_{i}")
            print(f"Generated Image: {image_path}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Meme generation test completed!")


if __name__ == "__main__":
    test_meme_generation()