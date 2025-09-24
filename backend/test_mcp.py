#!/usr/bin/env python3
"""
MCP Integration Test Script
Tests the MCP functionality with the Recipe Assistant
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.mcp_client import mcp_client
from backend.enhanced_recipes import search_recipes_enhanced, get_recipe_nutrition, get_api_status

async def test_mcp_basic():
    """Test basic MCP functionality"""
    print("🧪 Testing MCP Integration...")
    print("=" * 50)

    # Test API status
    print("📊 Checking API Status...")
    status = get_api_status()
    print(f"MCP Available: {status['mcp_available']}")
    print(f"Available APIs: {', '.join([api for api, available in status['apis'].items() if available])}")
    print()

    # Test recipe search
    print("🔍 Testing Recipe Search...")
    try:
        recipes = await search_recipes_enhanced(
            query="high protein chicken salad",
            dietary_context="low carb",
            max_results=3,
            use_mcp=True
        )

        print(f"Found {len(recipes)} recipes:")
        for i, recipe in enumerate(recipes[:2], 1):  # Show first 2 recipes
            print(f"  {i}. {recipe['title']} ({recipe.get('source', 'Unknown')})")
            print(f"     Health Score: {recipe.get('mcp_health_score', 'N/A')}")
        print()

    except Exception as e:
        print(f"❌ Recipe search failed: {e}")
        print()

    # Test nutrition analysis
    print("🥗 Testing Nutrition Analysis...")
    try:
        ingredients = ["4 oz chicken breast", "2 cups mixed greens", "1 tbsp olive oil"]
        nutrition = await get_recipe_nutrition(ingredients)

        print("Sample ingredients: Chicken breast, mixed greens, olive oil"
        print(f"Total calories: {nutrition.get('calories', 0)}")
        print(f"Protein: {nutrition.get('protein', 0)}g")
        print(f"Carbohydrates: {nutrition.get('carbohydrates', 0)}g")
        print(f"Fat: {nutrition.get('fat', 0)}g")
        print()

    except Exception as e:
        print(f"❌ Nutrition analysis failed: {e}")
        print()

    # Test health analysis
    print("🏥 Testing Health Analysis...")
    try:
        sample_recipe = {
            "title": "Grilled Chicken Salad",
            "ingredients": ["chicken breast", "lettuce", "tomato", "olive oil"],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 350},
                    {"name": "Protein", "amount": 30},
                    {"name": "Carbohydrates", "amount": 20},
                    {"name": "Fat", "amount": 15}
                ]
            },
            "servings": 1
        }

        analysis = await search_recipes_enhanced.analyze_recipe_health(sample_recipe)

        print(f"Health Score: {analysis.get('health_score', 0)}/100")
        print(f"Calories per serving: {analysis.get('calories_per_serving', 0)}")
        print(f"Protein per serving: {analysis.get('protein_per_serving', 0)}g")
        print("Recommendations:")
        for rec in analysis.get('recommendations', []):
            print(f"  • {rec}")
        print()

    except Exception as e:
        print(f"❌ Health analysis failed: {e}")
        print()

    print("✅ MCP Test Complete!")
    print("=" * 50)

def main():
    """Run MCP tests"""
    asyncio.run(test_mcp_basic())

if __name__ == "__main__":
    main()
