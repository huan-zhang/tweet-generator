# Story Tweet Generator

An automated Python application that generates creative short stories on random topics and posts them to X (Twitter) with AI-generated illustrations. Each story is designed to entertain, inspire, or spark imagination in a brief social media format.

## Features

- **AI-Powered Story Generation**: Uses OpenAI GPT or Google Gemini to create original short stories
- **Random Topic Selection**: 20+ diverse story prompts including fantasy, sci-fi, slice-of-life, and mystery
- **Automated Image Creation**: Generates accompanying illustrations using DALL-E or creates text-based images
- **Scheduled Posting**: Automatically posts to X/Twitter every 8 hours
- **Dual AI Support**: Choose between OpenAI or Gemini models
- **Flexible Operation**: Run immediately, schedule posts, or view posting history
- **Fallback Mechanisms**: Built-in fallback stories ensure posts are always generated

## Story Topics

Random topics include:
- Fantasy adventures (dragons, magical vending machines, time travelers)
- Sci-Fi scenarios (AI emotions, future libraries, gravity stopping)
- Slice-of-life moments (coffee shop encounters, pet mysteries)
- Supernatural elements (hearing plant thoughts, mysterious rooms)
- Humor and everyday situations (superhero day jobs, social media time travel problems)

## Installation

1. **Clone or download the project**
   ```bash
   cd tweet-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Configuration

### Required API Keys

Choose one AI provider:

**For OpenAI:**
- Get an API key from [OpenAI Platform](https://platform.openai.com/)
- Add to `.env`: `OPENAI_API_KEY=your_key_here`
- Set: `AI_PROVIDER=openai`

**For Google Gemini:**
- Get an API key from [Google AI Studio](https://makersuite.google.com/)
- Add to `.env`: `GEMINI_API_KEY=your_key_here`
- Set: `AI_PROVIDER=gemini`

### Twitter/X API Setup

1. Create a Twitter Developer account at [developer.twitter.com](https://developer.twitter.com/)
2. Create a new app and generate API keys
3. Add all Twitter credentials to `.env`:
   ```
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   ```

### Environment Variables

```bash
# AI Provider (choose one)
AI_PROVIDER=openai  # or "gemini"
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Twitter API
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Settings
AUTO_POST=false  # Set to "true" to enable posting
```

## Usage

### Run Once (Generate 3 Posts)
```bash
python main.py
```

### Scheduled Operation

#### Local Scheduling
```bash
# Start the scheduler (posts every 8 hours: 8 AM, 4 PM, Midnight)
python scheduler.py --mode schedule
```

#### Cloud Automation (Recommended)
Use GitHub Actions for completely free automated posting:
```bash
# See GITHUB_ACTIONS_SETUP.md for detailed instructions
# Runs automatically every 8 hours in the cloud - no server needed!
```

### Generate Posts Immediately
```bash
python scheduler.py --mode immediate
```

### View Post History
```bash
# Show last 7 days
python scheduler.py --mode history

# Show last 30 days
python scheduler.py --mode history --days 30
```

## Project Structure

```
tweet-generator/
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── quote_generator.py   # AI quote generation
├── image_generator.py   # Image creation (DALL-E + fallback)
├── twitter_poster.py    # X/Twitter posting
├── scheduler.py         # Scheduling and automation
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── generated_images/    # Output directory for images
└── post_history.json    # Posting history log
```

## Customization

### Modify Posting Times
Edit `config.py` to change 8-hour intervals:
```python
post_times: list = ["08:00", "16:00", "00:00"]  # 8 AM, 4 PM, Midnight
```

### Adjust Story Generation
In `config.py`, modify:
- `story_max_length`: Character limit for posts (default: 280)
- `story_temperature`: Creativity level (default: 0.9 for more creative stories)
- `story_model`: AI model to use

### Customize Image Generation
- `image_model`: DALL-E model version
- `image_size`: Image dimensions
- `image_style`: Style description for images

## Safety Features

- **Dry Run Mode**: Set `AUTO_POST=false` to generate without posting
- **Fallback Quotes**: Pre-written quotes if AI generation fails  
- **Error Handling**: Comprehensive logging and error recovery
- **Rate Limiting**: Built-in Twitter API rate limit handling
- **History Tracking**: Prevents duplicate posts

## Monitoring

Check logs in:
- Console output during execution
- `tweet_generator.log` file
- `post_history.json` for posting records

## Development

### Testing Quote Generation
```python
from quote_generator import QuoteGenerator
from config import Config

config = Config()
generator = QuoteGenerator(config)
quote = generator.generate_quote()
print(quote)
```

### Testing Image Generation  
```python
from image_generator import ImageGenerator
from config import Config

config = Config()
generator = ImageGenerator(config)
image_path = generator.generate_image("Test quote", "test")
print(f"Generated: {image_path}")
```

## Troubleshooting

**Common Issues:**

1. **API Key Errors**: Verify all keys in `.env` are correct
2. **Image Generation Fails**: Check OpenAI billing/credits
3. **Twitter Posting Fails**: Verify Twitter app permissions
4. **Module Import Errors**: Ensure all requirements are installed

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is for educational and personal use. Ensure compliance with:
- OpenAI/Gemini API terms of service
- Twitter Developer Agreement  
- Relevant content creation guidelines

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation for providers
3. Open an issue with detailed error information