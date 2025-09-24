# MCP (Model Context Protocol) Integration for Recipe Assistant

## Overview

This MCP integration enhances the Recipe Assistant with real-time data from external APIs, providing richer recipe information, nutritional analysis, and health insights.

## Features

- **Enhanced Recipe Search**: Access to multiple recipe databases via Spoonacular and Edamam APIs
- **Real-time Nutrition Data**: Accurate nutritional information from Nutritionix and USDA APIs
- **Health Analysis**: Automated health scoring and dietary recommendations
- **API Integration**: Seamless integration with existing chat functionality

## Setup Instructions

### 1. Get Free API Keys

#### Spoonacular API (150 free requests/day)
1. Go to [Spoonacular Developer Portal](https://spoonacular.com/food-api)
2. Sign up for a free account
3. Get your API key from the dashboard

#### Edamam Recipe Search API (10,000 free requests/month)
1. Go to [Edamam Developer Portal](https://developer.edamam.com/)
2. Sign up for a free account
3. Get your App ID and App Key

#### Nutritionix API (200 free requests/day)
1. Go to [Nutritionix Developer Portal](https://developer.nutritionix.com/)
2. Sign up for a free account
3. Get your App ID and App Key

### 2. Configure Environment Variables

Update your `.env` file or create `.env.mcp` with your API keys:

```bash
# MCP Server Configuration
SPOONACULAR_API_KEY=your_spoonacular_api_key_here
EDAMAM_APP_ID=your_edamam_app_id_here
EDAMAM_APP_KEY=your_edamam_app_key_here
NUTRITIONIX_APP_ID=your_nutritionix_app_id_here
NUTRITIONIX_APP_KEY=your_nutritionix_app_key_here
```

### 3. Install Dependencies

```bash
cd D:\Hackathon\MyRecipeFinder\backend
pip install python-dotenv requests tavily
```

### 4. Start the Server

The MCP endpoints are automatically registered with your Flask app. Restart your backend server:

```bash
python app.py
```

## API Endpoints

### Search Enhanced Recipes
```bash
POST /api/mcp/search
Content-Type: application/json

{
    "query": "high protein chicken salad",
    "dietary_context": "low carb",
    "max_results": 10,
    "use_mcp": true
}
```

### Get Nutrition Information
```bash
POST /api/mcp/nutrition
Content-Type: application/json

{
    "ingredients": ["chicken breast", "lettuce", "olive oil"]
}
```

### Analyze Recipe Health
```bash
POST /api/mcp/analyze
Content-Type: application/json

{
    "recipe_data": {
        "title": "Grilled Chicken Salad",
        "ingredients": ["chicken", "lettuce", "tomato"],
        "nutrition": {"calories": 350, "protein": 25}
    }
}
```

### Check API Status
```bash
GET /api/mcp/status
```

### Test MCP Connectivity
```bash
GET /api/mcp/test
```

## Usage Examples

### Basic Recipe Search with MCP
```python
import requests

response = requests.post('http://localhost:4000/api/mcp/search', json={
    'query': 'healthy dinner under 500 calories',
    'dietary_context': 'vegetarian',
    'max_results': 5
})

recipes = response.json()['results']
for recipe in recipes:
    print(f"Title: {recipe['title']}")
    print(f"Health Score: {recipe.get('mcp_health_score', 'N/A')}")
    print(f"Source: {recipe['source']}")
```

### Nutrition Analysis
```python
response = requests.post('http://localhost:4000/api/mcp/nutrition', json={
    'ingredients': ['1 cup cooked quinoa', '4 oz chicken breast', '1 tbsp olive oil']
})

nutrition = response.json()['nutrition']
print(f"Calories: {nutrition['calories']}")
print(f"Protein: {nutrition['protein']}g")
```

## Response Format

### Recipe Search Response
```json
{
  "success": true,
  "results": [
    {
      "title": "Quinoa Chicken Bowl",
      "ingredients": ["chicken breast", "quinoa", "broccoli"],
      "instructions": "1. Cook quinoa... 2. Grill chicken...",
      "nutrition": {
        "calories": 450,
        "protein": 35
      },
      "readyInMinutes": 25,
      "servings": 1,
      "image": "https://example.com/image.jpg",
      "source": "Spoonacular",
      "mcp_nutrition_analysis": {
        "calories_per_serving": 450,
        "protein_per_serving": 35,
        "health_score": 85,
        "recommendations": ["Well-balanced meal!"]
      }
    }
  ],
  "count": 1
}
```

### Nutrition Response
```json
{
  "success": true,
  "nutrition": {
    "calories": 450,
    "protein": 35,
    "carbohydrates": 40,
    "fat": 15,
    "fiber": 8
  }
}
```

### Health Analysis Response
```json
{
  "success": true,
  "analysis": {
    "calories_per_serving": 450,
    "protein_per_serving": 35,
    "carbs_per_serving": 40,
    "fat_per_serving": 15,
    "health_score": 85,
    "recommendations": ["Well-balanced meal!", "High protein content"],
    "insights": ["Good for muscle maintenance", "Rich in fiber"],
    "macro_ratios": {
      "protein": 0.31,
      "carbs": 0.36,
      "fat": 0.30
    }
  }
}
```

## Benefits of MCP Integration

1. **Enhanced Data Quality**: Real-time access to comprehensive recipe databases
2. **Accurate Nutrition**: Up-to-date nutritional information from trusted sources
3. **Health Insights**: Automated analysis of recipe healthiness
4. **Scalability**: Easy to add new APIs and data sources
5. **Reliability**: Multiple fallback options when APIs are unavailable

## Troubleshooting

### Common Issues

1. **API Keys Not Working**
   - Verify API keys are correctly set in `.env.mcp`
   - Check API quotas and rate limits
   - Ensure you're using the correct API endpoints

2. **MCP Not Responding**
   - Check Flask server logs for errors
   - Verify all dependencies are installed
   - Test individual API endpoints

3. **Slow Response Times**
   - External API calls add latency (typically 1-3 seconds)
   - Implement caching for frequently requested data
   - Consider async processing for multiple API calls

### Testing MCP Functionality

Use the test endpoint to verify everything is working:

```bash
curl http://localhost:4000/api/mcp/test
```

Expected response:
```json
{
  "success": true,
  "test_results": {
    "mcp_server": "available",
    "apis_available": ["spoonacular", "edamam", "nutritionix"],
    "tests_passed": 3,
    "tests_total": 4
  },
  "message": "MCP is operational. 3/4 APIs available."
}
```

## Future Enhancements

1. **Additional APIs**: Integrate with more recipe and nutrition databases
2. **Caching Layer**: Implement Redis caching for API responses
3. **Rate Limiting**: Add intelligent rate limiting to optimize API usage
4. **Error Recovery**: Enhanced fallback mechanisms when APIs are unavailable
5. **Analytics**: Track API usage and performance metrics

## Security Considerations

1. **API Key Security**: Store API keys securely, never in frontend code
2. **Rate Limiting**: Implement rate limiting to prevent API abuse
3. **Data Validation**: Validate all external data before use
4. **Error Handling**: Prevent sensitive information from leaking in errors

## Support

For issues or questions about MCP integration:
1. Check the API documentation for each service
2. Review Flask server logs for detailed error messages
3. Test individual components in isolation
4. Monitor API usage and quotas

---

*This MCP integration provides a solid foundation for enhanced recipe functionality while maintaining compatibility with the existing Recipe Assistant architecture.*
