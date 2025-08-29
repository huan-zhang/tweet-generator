# GitHub Actions Setup Guide

This guide will help you set up automated story posting using GitHub Actions, which runs completely free in the cloud.

## 🚀 **How It Works**

Your story bot will automatically:
- Run every 8 hours (00:00, 08:00, 16:00 UTC)
- Generate a random story
- Create an AI illustration 
- Post to Twitter/X
- All completely free using GitHub Actions!

## 📋 **Setup Instructions**

### Step 1: Push Code to GitHub
Your code is already ready! Just make sure it's pushed to your GitHub repository.

### Step 2: Configure Repository Secrets

1. **Go to your GitHub repository**
2. **Click "Settings" tab**
3. **Click "Secrets and variables" → "Actions"**
4. **Click "New repository secret"**

Add these secrets one by one:

#### **AI Provider Secrets**
```
Name: AI_PROVIDER
Value: openai
(Note: This is optional - defaults to "openai" if not set)

Name: OPENAI_API_KEY  
Value: [Your OpenAI API key - REQUIRED]
Example: sk-abc123...

Name: GEMINI_API_KEY
Value: [Your Gemini API key - optional]
```

#### **Twitter API Secrets**
```
Name: TWITTER_CLIENT_ID
Value: [Your Twitter Client ID]

Name: TWITTER_CLIENT_SECRET
Value: [Your Twitter Client Secret]

Name: TWITTER_API_KEY
Value: [Your Twitter API Key]

Name: TWITTER_API_SECRET
Value: [Your Twitter API Secret]

Name: TWITTER_ACCESS_TOKEN
Value: [Your Twitter Access Token]

Name: TWITTER_ACCESS_TOKEN_SECRET
Value: [Your Twitter Access Token Secret]

Name: TWITTER_BEARER_TOKEN
Value: [Your Twitter Bearer Token]
```

### Step 3: Enable GitHub Actions

1. **Go to "Actions" tab** in your repository
2. **Click "Enable GitHub Actions"** if prompted
3. **The workflows will appear** after you commit the workflow files

## 🕐 **Schedule Details**

The bot runs **every 8 hours** at:
- **00:00 UTC** (Midnight)
- **08:00 UTC** (8 AM)  
- **16:00 UTC** (4 PM)

**Converting to Your Timezone:**
- If you're in EST (UTC-5): 7 PM, 3 AM, 11 AM
- If you're in PST (UTC-8): 4 PM, 12 AM, 8 AM
- If you're in CST (UTC-6): 6 PM, 2 AM, 10 AM

## 🧪 **Testing Your Setup**

### Manual Test (Recommended First)
1. **Go to Actions tab** in your GitHub repo
2. **Click "Manual Story Test"**
3. **Click "Run workflow"**
4. **Choose "Run in dry mode"** for your first test
5. **Click "Run workflow"** button

This will test story generation without posting to Twitter.

### Live Test
Once dry mode works:
1. **Run "Manual Story Test" again**
2. **Uncheck "Run in dry mode"**
3. **Click "Run workflow"**

This will generate and actually post a story!

## 📊 **Monitoring Your Bot**

### View Workflow Runs
1. **Go to "Actions" tab**
2. **Click on any workflow run** to see logs
3. **Check if stories were generated and posted**

### Download Generated Images
1. **Click on a completed workflow run**
2. **Scroll to "Artifacts" section**
3. **Download images** to see what was created

## 🔧 **Customizing Schedule**

To change posting times, edit `.github/workflows/story-bot.yml`:

```yaml
schedule:
  # Current: Every 8 hours
  - cron: '0 0,8,16 * * *'
  
  # Every 6 hours: 
  - cron: '0 0,6,12,18 * * *'
  
  # Every 12 hours:
  - cron: '0 0,12 * * *'
  
  # Daily at 9 AM UTC:
  - cron: '0 9 * * *'
```

## ⚡ **Benefits of GitHub Actions**

- ✅ **Completely Free** (2000 minutes/month)
- ✅ **No Server Maintenance** 
- ✅ **Automatic Scaling**
- ✅ **Built-in Monitoring**
- ✅ **Secure Secret Management**
- ✅ **Version Control Integration**

## 🚨 **Important Notes**

1. **Keep API Keys Secret**: Never put API keys in your code, only in GitHub Secrets
2. **Monitor Usage**: Check that your OpenAI/Twitter usage stays within limits
3. **GitHub Actions Limits**: 2000 free minutes/month (your bot uses ~2 minutes per run)
4. **UTC Timing**: All schedules are in UTC time
5. **Manual Override**: You can always run workflows manually for testing

## 🔍 **Troubleshooting**

### Bot Not Running?
- Check if Actions are enabled in your repo
- Verify all secrets are set correctly
- Look at workflow logs for error messages

### Stories Not Posting?
- Check Twitter API credentials
- Verify `AUTO_POST` is set correctly
- Look for rate limiting messages

### Images Not Generating?
- Check OpenAI API key and credits
- Verify network connectivity in logs
- Check for API quota limits

## 📞 **Need Help?**

If you run into issues:
1. Check the workflow logs in GitHub Actions
2. Verify all secrets are set correctly  
3. Try the manual test workflow first
4. Check your API key quotas and permissions

Your automated story bot is now ready to entertain the world! 🎨📚✨