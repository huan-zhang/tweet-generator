# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is an automated tweet generator called "IgnorantStrength" that creates inspirational social media posts around the theme of finding strength in humility and intellectual honesty. The application generates quotes using AI (OpenAI or Gemini), creates accompanying images, and posts to Twitter/X on a scheduled basis.

## Core Commands

### Installation and Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # Then edit with your API keys
```

### Running the Application
```bash
# Generate and post 3 tweets immediately
python main.py

# Run scheduled posting (9 AM, 2 PM, 7 PM daily)
python scheduler.py --mode schedule

# Generate posts immediately without waiting for schedule
python scheduler.py --mode immediate

# View posting history
python scheduler.py --mode history --days 7
```

### Testing Individual Components
```python
# Test quote generation
from quote_generator import QuoteGenerator
from config import Config
config = Config()
generator = QuoteGenerator(config)
quote = generator.generate_quote()

# Test image generation
from image_generator import ImageGenerator
generator = ImageGenerator(config)
image_path = generator.generate_image("Test quote", "test")
```

## Architecture and Key Components

### Modular Design
The application follows a modular architecture with clear separation of concerns:

- **config.py**: Centralized configuration using dataclasses with environment variable integration
- **quote_generator.py**: AI-powered content generation with dual provider support (OpenAI/Gemini)
- **image_generator.py**: Image creation with DALL-E integration and text-based fallbacks
- **twitter_poster.py**: Twitter API integration using both v1.1 (media) and v2 (posting) APIs
- **scheduler.py**: Task scheduling with history tracking and duplicate prevention
- **main.py**: Main orchestration and workflow coordination

### AI Provider Architecture
The system supports dual AI providers through a provider pattern:
- OpenAI: Uses GPT models for quotes and DALL-E for images
- Gemini: Uses Gemini models for quotes with fallback text images
- Provider switching via `AI_PROVIDER` environment variable

### Fallback and Error Handling Strategy
- Pre-written fallback quotes when AI generation fails
- Text-based image generation when DALL-E is unavailable
- Comprehensive logging to both console and files
- Graceful degradation at each component level

### Data Flow
1. Configuration loaded from environment variables and config.py
2. Quote generated using selected AI provider
3. Image created based on quote content
4. Content posted to Twitter (if auto-post enabled)
5. Activity logged to post_history.json for duplicate prevention

## Configuration System

### Environment Variables Required
```bash
# AI Provider Selection
AI_PROVIDER=openai  # or "gemini"
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key

# Twitter API Credentials
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Application Settings
AUTO_POST=false  # Set to "true" to enable actual posting
```

### Content Configuration
Key settings in config.py:
- `post_times`: Default ["09:00", "14:00", "19:00"] for scheduling
- `quote_max_length`: 200 characters for Twitter compliance
- `posts_per_day`: 3 posts generated per run
- `account_theme`: "ignorant strength" concept drives content generation

## File Structure and Data Storage

### Generated Content Storage
- `generated_images/`: AI-generated and text-based images
- `post_history.json`: Posting history with 30-day retention
- `tweet_generator.log`: Application logs

### Scheduling and History
- Post history prevents duplicate content within time windows
- Scheduler tracks daily posting slots to avoid over-posting
- History cleanup maintains only last 30 days of records

## Development Notes

### Twitter API Integration
Uses dual API approach:
- Twitter API v1.1 for media uploads (tweepy.API)
- Twitter API v2 for posting tweets (tweepy.Client)
- Built-in rate limiting and authentication testing

### Error Recovery Patterns
Each component implements graceful fallbacks:
- Quote generation: Falls back to pre-written inspirational quotes
- Image generation: Creates text-based images when DALL-E fails
- Posting: Dry-run mode for testing without actual posting

### Content Theme Management
The "ignorant strength" theme is consistently applied through:
- Structured prompts in config.quote_prompt_template
- Image style descriptions in config.image_prompt_template  
- Fallback quotes aligned with core message
- Hashtag integration for social media engagement