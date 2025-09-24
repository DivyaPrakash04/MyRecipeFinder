"""
Enhanced Recipe Search with MCP Integration
Combines existing functionality with external API data
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from mcp_client import mcp_client

logger = logging.getLogger("enhanced-recipes")

# Initialize Tavily client if API key is available
tc = None
tavily_api_key = os.getenv("TAVILY_API_KEY")
if tavily_api_key:
    tc = TavilyClient(api_key=tavily_api_key)

async def search_recipes_enhanced(
    query: str,
    dietary_context: str = "",
    max_results: int = 10,
    use_mcp: bool = True
) -> List[Dict[str, Any]]:
    """
    Enhanced recipe search with MCP integration

    Args:
        query: Search query
        dietary_context: Dietary preferences/restrictions
        max_results: Maximum number of results
        use_mcp: Whether to use MCP for enhanced data
    """
    recipes = []

    try:
        # Try MCP-enhanced search first
        if use_mcp:
            mcp_recipes = await mcp_client.search_enhanced_recipes(
                query=query,
                diet=dietary_context,
                max_results=max_results
            )

            for recipe in mcp_recipes:
                # Enhance with MCP analysis
                enhanced_recipe = await mcp_client.enhance_recipe_with_mcp(recipe)
                recipes.append(enhanced_recipe)

        # Fallback to Tavily if MCP doesn't return enough results
        if len(recipes) < max_results and tc:
            try:
                # Combine query with dietary context
                search_query = f"{query} {dietary_context}".strip()
                response = tc.search(
                    query=search_query,
                    search_depth="advanced",
                    include_images=False,
                    max_results=max_results - len(recipes)
                )

                # Process Tavily results
                for result in response.get("results", []):
                    recipe_data = {
                        "title": result.get("title", ""),
                        "summary": result.get("content", "")[:300] + "...",
                        "ingredients": [],  # Would need extraction logic
                        "instructions": "See full recipe link",
                        "source": "Tavily",
                        "url": result.get("url", ""),
                        "mcp_enhanced": False
                    }
                    recipes.append(recipe_data)

            except Exception as e:
                logger.warning(f"Tavily search error: {e}")

    except Exception as e:
        logger.error(f"Enhanced recipe search error: {e}")
        # Fallback to original search method would go here

    return recipes[:max_results]

async def get_recipe_nutrition(ingredients: List[str]) -> Dict[str, float]:
    """
    Get nutritional information for a list of ingredients

    Args:
        ingredients: List of ingredient strings

    Returns:
        Dictionary with nutritional data
    """
    try:
        nutrition = await mcp_client.get_nutrition_analysis(ingredients)

        return {
            "calories": nutrition.get("calories", 0),
            "protein": nutrition.get("protein", 0),
            "carbohydrates": nutrition.get("carbs", 0),
            "fat": nutrition.get("fat", 0),
            "fiber": nutrition.get("fiber", 0),
        }
    except Exception as e:
        logger.error(f"Nutrition analysis error: {e}")
        return {}

async def analyze_recipe_health(recipe_data: Dict) -> Dict[str, Any]:
    """
    Analyze the health aspects of a recipe

    Args:
        recipe_data: Recipe dictionary

    Returns:
        Health analysis dictionary
    """
    try:
        analysis = await mcp_client.analyze_recipe_nutrition(recipe_data)

        # Add additional health insights
        insights = []

        calories = analysis.get("calories_per_serving", 0)
        protein = analysis.get("protein_per_serving", 0)
        carbs = analysis.get("carbs_per_serving", 0)
        fat = analysis.get("fat_per_serving", 0)

        # Calorie analysis
        if calories < 300:
            insights.append("Low calorie meal - good for weight management")
        elif calories > 800:
            insights.append("High calorie meal - consider portion control")

        # Protein analysis
        if protein < 15:
            insights.append("Low protein - consider adding protein-rich foods")
        elif protein > 30:
            insights.append("High protein - excellent for muscle maintenance")

        # Macro balance
        protein_ratio = (protein * 4) / calories if calories > 0 else 0
        carb_ratio = (carbs * 4) / calories if calories > 0 else 0
        fat_ratio = (fat * 9) / calories if calories > 0 else 0

        if 0.15 <= protein_ratio <= 0.25 and carb_ratio <= 0.5 and fat_ratio <= 0.3:
            insights.append("Well-balanced macronutrient profile")

        analysis["insights"] = insights
        analysis["macro_ratios"] = {
            "protein": protein_ratio,
            "carbs": carb_ratio,
            "fat": fat_ratio
        }

        return analysis

    except Exception as e:
        logger.error(f"Health analysis error: {e}")
        return {"health_score": 50, "insights": ["Unable to analyze"]}

def get_api_status() -> Dict[str, Any]:
    """
    Get status of available APIs

    Returns:
        Dictionary with API availability status
    """
    from mcp_server import mcp_server

    status = {
        "mcp_available": True,
        "apis": {}
    }

    # Check Spoonacular
    status["apis"]["spoonacular"] = bool(mcp_server.api_keys.get("spoonacular"))

    # Check Edamam
    status["apis"]["edamam"] = bool(
        mcp_server.api_keys.get("edamam_app_id") and
        mcp_server.api_keys.get("edamam_app_key")
    )

    # Check Nutritionix
    status["apis"]["nutritionix"] = bool(
        mcp_server.api_keys.get("nutritionix_app_id") and
        mcp_server.api_keys.get("nutritionix_app_key")
    )

    # Check Tavily
    status["apis"]["tavily"] = bool(tc)

    return status
