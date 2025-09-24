"""
MCP Client for Recipe Assistant
Integrates MCP server with the existing LLM system
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from mcp_server import mcp_handler

logger = logging.getLogger("mcp-client")

class RecipeMCPClient:
    """MCP Client for enhanced recipe functionality"""

    async def search_enhanced_recipes(self, query: str, diet: str = "", max_results: int = 10) -> List[Dict]:
        """Search for recipes with enhanced data from MCP servers"""
        try:
            # Use MCP to get enhanced recipe data
            response = await mcp_handler.handle_request({
                'method': 'search_recipes',
                'params': {
                    'query': query,
                    'diet': diet,
                    'max_results': max_results
                }
            })

            if 'result' in response:
                return response['result']
            else:
                logger.warning(f"MCP search failed: {response.get('error', 'Unknown error')}")
                return []

        except Exception as e:
            logger.error(f"MCP search error: {e}")
            return []

    async def get_nutrition_analysis(self, ingredients: List[str]) -> Dict:
        """Get detailed nutrition analysis"""
        try:
            response = await mcp_handler.handle_request({
                'method': 'get_nutrition',
                'params': {'ingredients': ingredients}
            })

            if 'result' in response:
                return response['result']
            return {}

        except Exception as e:
            logger.error(f"Nutrition analysis error: {e}")
            return {}

    async def get_recipe_details(self, recipe_id: str, source: str = "spoonacular") -> Optional[Dict]:
        """Get detailed recipe information"""
        try:
            response = await mcp_handler.handle_request({
                'method': 'get_recipe',
                'params': {
                    'recipe_id': recipe_id,
                    'source': source
                }
            })

            if 'result' in response and response['result']:
                return response['result']
            return None

        except Exception as e:
            logger.error(f"Recipe details error: {e}")
            return None

    async def analyze_recipe_nutrition(self, recipe_data: Dict) -> Dict:
        """Analyze nutritional content of a recipe"""
        try:
            response = await mcp_handler.handle_request({
                'method': 'analyze_nutrition',
                'params': {'recipe_data': recipe_data}
            })

            if 'result' in response:
                return response['result']
            return {}

        except Exception as e:
            logger.error(f"Nutrition analysis error: {e}")
            return {}

    async def enhance_recipe_with_mcp(self, recipe: Dict) -> Dict:
        """Enhance a recipe with MCP data"""
        enhanced = recipe.copy()

        # Get detailed nutrition analysis
        nutrition_analysis = await self.analyze_recipe_nutrition(recipe)
        enhanced['mcp_nutrition_analysis'] = nutrition_analysis

        # Add health recommendations
        recommendations = []
        if nutrition_analysis.get('health_score', 0) < 70:
            recommendations.append("Consider balancing this meal with additional vegetables")
        if nutrition_analysis.get('protein_per_serving', 0) < 15:
            recommendations.append("Add protein-rich ingredients for better satiety")

        enhanced['mcp_recommendations'] = recommendations
        enhanced['mcp_health_score'] = nutrition_analysis.get('health_score', 0)

        return enhanced

# Global MCP client instance
mcp_client = RecipeMCPClient()
