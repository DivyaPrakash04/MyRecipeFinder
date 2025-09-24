# Get Free API Keys for Local Development

## 1. Cohere API Key (for AI Chat)
1. Go to https://cohere.ai/
2. Sign up for a free account
3. Go to API Keys section in your dashboard
4. Create a new API key
5. Copy the key and add it to your `.env` file:
   ```
   COHERE_API_KEY=your_actual_key_here
   ```

**Free Tier**: Good for testing and development

## 2. Tavily API Key (for Recipe Search)
1. Go to https://tavily.com/
2. Sign up for a free account
3. Go to API Keys section
4. Copy your API key
5. Add it to your `.env` file:
   ```
   TAVILY_API_KEY=your_actual_key_here
   ```

**Free Tier**: 1000 searches/month

## 3. Quick Setup

1. Copy the template:
   ```bash
   cp backend/.env.template backend/.env
   ```

2. Edit `backend/.env` and add your real API keys

3. You're ready to go!

## 💡 Tips

- **No API keys?** The app will show error messages but still work for basic functionality
- **Rate limits?** Free tiers are generous for personal use
- **Need help?** Both services have great documentation and support

## 🚀 Test Your Setup

Run the test script:
```bash
python test_local.py
```

This will check if everything is working correctly!
