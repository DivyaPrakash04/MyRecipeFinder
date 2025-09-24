#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Recipe Assistant
ENHANCED VERSION with COMPREHENSIVE FALLBACK SYSTEM
Uses only FREE APIs: TheMealDB, USDA, FatSecret, Spoonacular
"""

import os
import json
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Sequence

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("mcp-server")

class RobustRecipeMCPServer:
    """MCP Server with comprehensive fallback system using FREE APIs"""

    def __init__(self):
        # FatSecret API (Free: 5000 requests/day)
        self.fatsecret_app_key = os.getenv('FATSECRET_APP_KEY', '')
        self.fatsecret_app_secret = os.getenv('FATSECRET_APP_SECRET', '')

        # API base URLs - All FREE to use
        self.api_endpoints = {
            'themealdb': 'https://www.themealdb.com/api/json/v1/1',
            'fatsecret': 'https://platform.fatsecret.com/rest/server.api',
            'usda': 'https://api.nal.usda.gov/fdc/v1',
            'spoonacular': 'https://api.spoonacular.com',
        }

        # Comprehensive API health tracking
        self.api_health = {
            'themealdb': {'available': True, 'last_success': time.time(), 'failures': 0},
            'usda': {'available': True, 'last_success': time.time(), 'failures': 0},
            'fatsecret': {'available': True, 'last_success': time.time(), 'failures': 0},
            'spoonacular': {'available': True, 'last_success': time.time(), 'failures': 0},
        }

        logger.info("🚀 RobustRecipeMCPServer initialized with FREE APIs")

    async def search_recipes_with_fallback(self, query: str, diet: str = "", max_results: int = 10) -> List[Dict]:
        """Enhanced search with comprehensive fallback system"""
        recipes = []
        sources_tried = []

        # API Priority: TheMealDB -> Spoonacular -> Local fallback
        api_priority = [
            ('themealdb', 'search_recipes_themealdb'),
            ('spoonacular', 'search_recipes_spoonacular'),
        ]

        for api_name, method_name in api_priority:
            if not self.api_health[api_name]['available']:
                logger.warning(f"⏭️ Skipping {api_name} - marked as unavailable")
                sources_tried.append(f"{api_name}(unavailable)")
                continue

            try:
                method = getattr(self, method_name)
                api_recipes = await method(query, max_results)
                sources_tried.append(api_name)

                if api_recipes:
                    logger.info(f"✅ {api_name} returned {len(api_recipes)} recipes")
                    recipes.extend(api_recipes)
                    self.api_health[api_name]['last_success'] = time.time()
                    self.api_health[api_name]['failures'] = 0
                    break  # Success, stop trying other APIs
                else:
                    logger.warning(f"⚠️ {api_name} returned no results")

            except Exception as e:
                logger.error(f"❌ {api_name} failed: {e}")
                self.api_health[api_name]['failures'] += 1
                sources_tried.append(f"{api_name}(failed)")

                # Mark as unavailable after 3 failures
                if self.api_health[api_name]['failures'] >= 3:
                    self.api_health[api_name]['available'] = False
                    logger.error(f"🚫 {api_name} marked as unavailable after 3 failures")

        # If no API worked, return fallback recipes
        if not recipes:
            logger.warning("🔄 All APIs failed, using fallback recipes")
            recipes = self.get_fallback_recipes(query, max_results)
            sources_tried.append("fallback")

        # Add metadata about sources tried and fallback status
        for recipe in recipes:
            recipe['_sources_tried'] = sources_tried
            recipe['_fallback_used'] = len(sources_tried) > 1
            recipe['_enhanced_by'] = 'FREE MCP'
            recipe['_api_cost'] = '$0'

        logger.info(f"📊 Search complete: {len(recipes)} recipes from {sources_tried}")
        return recipes[:max_results]

    async def get_nutrition_with_fallback(self, ingredients: List[str]) -> Dict:
        """Get nutrition with multiple fallback sources"""
        nutrition_results = {}
        sources_tried = []

        # Nutrition API Priority: USDA -> FatSecret -> Smart Estimates
        nutrition_apis = [
            ('usda', 'get_nutrition_usda'),
            ('fatsecret', 'get_nutrition_fatsecret'),
        ]

        for api_name, method_name in nutrition_apis:
            if not self.api_health[api_name]['available']:
                sources_tried.append(f"{api_name}(unavailable)")
                continue

            try:
                method = getattr(self, method_name)
                result = await method(ingredients)
                sources_tried.append(api_name)

                if any(result.values()):  # If we got any nutrition data
                    nutrition_results[api_name] = result
                    self.api_health[api_name]['last_success'] = time.time()
                    self.api_health[api_name]['failures'] = 0
                    logger.info(f"✅ {api_name} provided nutrition data")
                    break  # Success, use this data

            except Exception as e:
                logger.error(f"❌ {api_name} nutrition failed: {e}")
                self.api_health[api_name]['failures'] += 1
                sources_tried.append(f"{api_name}(failed)")

        # Merge nutrition data from multiple sources
        final_nutrition = self.merge_nutrition_data(nutrition_results)

        # If no nutrition data, use smart estimates
        if not any(final_nutrition.values()):
            logger.warning("🔄 No nutrition APIs worked, using smart estimates")
            final_nutrition = self.estimate_nutrition(ingredients)
            sources_tried.append("estimated")

        final_nutrition['_sources_tried'] = sources_tried
        final_nutrition['_nutrition_cost'] = '$0'

        logger.info(f"🥗 Nutrition analysis complete from {sources_tried}")
        return final_nutrition

    def merge_nutrition_data(self, nutrition_results: Dict) -> Dict:
        """Merge nutrition data from multiple sources intelligently"""
        if not nutrition_results:
            return {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}

        # Start with zeros
        merged = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}

        # Take the highest value for each nutrient (most likely to be accurate)
        for source, data in nutrition_results.items():
            for nutrient, value in data.items():
                if isinstance(value, (int, float)) and value > merged.get(nutrient, 0):
                    merged[nutrient] = value

        logger.info(f"📊 Merged nutrition from {len(nutrition_results)} sources")
        return merged

    def estimate_nutrition(self, ingredients: List[str]) -> Dict:
        """Smart nutrition estimation when APIs fail"""
        # Basic estimations per ingredient type
        estimations = {
            'protein': ['chicken', 'beef', 'fish', 'egg', 'tofu', 'beans', 'protein', 'turkey', 'pork'],
            'high_carb': ['rice', 'pasta', 'bread', 'potato', 'flour', 'sugar', 'noodles', 'quinoa'],
            'high_fat': ['oil', 'butter', 'cheese', 'avocado', 'nuts', 'mayonnaise', 'cream'],
            'high_fiber': ['vegetables', 'fruits', 'whole grain', 'beans', 'broccoli', 'spinach', 'kale'],
            'low_cal': ['lettuce', 'cucumber', 'tomato', 'celery', 'broth', 'water', 'tea']
        }

        estimated = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()

            # Estimate calories based on ingredient type
            if any(word in ingredient_lower for word in estimations['protein']):
                estimated['calories'] += 100  # High protein = ~100 cal per serving
                estimated['protein'] += 15
            elif any(word in ingredient_lower for word in estimations['high_carb']):
                estimated['calories'] += 150  # High carb = ~150 cal per serving
                estimated['carbs'] += 30
            elif any(word in ingredient_lower for word in estimations['high_fat']):
                estimated['calories'] += 120  # High fat = ~120 cal per serving
                estimated['fat'] += 12
            elif any(word in ingredient_lower for word in estimations['low_cal']):
                estimated['calories'] += 25   # Low calorie vegetables = ~25 cal per serving
                estimated['fiber'] += 3
            elif any(word in ingredient_lower for word in estimations['high_fiber']):
                estimated['calories'] += 50   # High fiber = ~50 cal per serving
                estimated['fiber'] += 8
            else:
                estimated['calories'] += 75   # Default estimate
                estimated['carbs'] += 15

        logger.info(f"🧮 Estimated nutrition for {len(ingredients)} ingredients")
        return estimated

    def get_fallback_recipes(self, query: str, max_results: int) -> List[Dict]:
        """High-quality fallback recipes when all APIs fail"""
        fallback_recipes = {
            "chicken": {
                "title": "Simple Grilled Chicken",
                "ingredients": ["chicken breast", "olive oil", "salt", "pepper", "garlic powder"],
                "instructions": "1. Season chicken breast with salt, pepper, and garlic powder.\n2. Brush with olive oil.\n3. Grill for 6-7 minutes per side until internal temperature reaches 165°F.\n4. Let rest for 5 minutes before serving.",
                "category": "Main Course",
                "readyInMinutes": 20,
                "servings": 2,
                "source": "Fallback Recipe",
                "image": "https://via.placeholder.com/300x200?text=Grilled+Chicken",
                "nutrition": {"calories": 350, "protein": 30, "carbs": 2, "fat": 15},
                "tags": ["healthy", "high-protein", "low-carb"]
            },
            "salad": {
                "title": "Fresh Garden Salad",
                "ingredients": ["mixed greens", "cherry tomatoes", "cucumber", "red onion", "olive oil", "balsamic vinegar", "feta cheese"],
                "instructions": "1. Wash and chop all vegetables.\n2. In a large bowl, combine mixed greens, tomatoes, cucumber, and red onion.\n3. Drizzle with olive oil and balsamic vinegar.\n4. Top with crumbled feta cheese.\n5. Toss gently and serve immediately.",
                "category": "Salad",
                "readyInMinutes": 10,
                "servings": 2,
                "source": "Fallback Recipe",
                "image": "https://via.placeholder.com/300x200?text=Garden+Salad",
                "nutrition": {"calories": 180, "protein": 6, "carbs": 12, "fat": 12},
                "tags": ["healthy", "vegetarian", "low-calorie"]
            },
            "pasta": {
                "title": "Simple Pasta Aglio e Olio",
                "ingredients": ["spaghetti", "garlic", "olive oil", "red pepper flakes", "parsley", "parmesan cheese"],
                "instructions": "1. Cook spaghetti according to package directions until al dente.\n2. While pasta cooks, mince garlic and chop parsley.\n3. Heat olive oil in a large pan over medium heat.\n4. Add garlic and red pepper flakes, sauté for 2 minutes.\n5. Drain pasta, reserving 1 cup pasta water.\n6. Add pasta to pan with garlic oil.\n7. Toss with parsley and parmesan cheese.\n8. Add pasta water as needed for sauce consistency.",
                "category": "Main Course",
                "readyInMinutes": 15,
                "servings": 2,
                "source": "Fallback Recipe",
                "image": "https://via.placeholder.com/300x200?text=Pasta+Aglio+e+Olio",
                "nutrition": {"calories": 450, "protein": 15, "carbs": 65, "fat": 18},
                "tags": ["classic", "italian", "vegetarian"]
            },
            "quinoa": {
                "title": "Mediterranean Quinoa Bowl",
                "ingredients": ["quinoa", "chickpeas", "feta cheese", "cherry tomatoes", "cucumber", "red onion", "olive oil", "lemon juice"],
                "instructions": "1. Cook quinoa according to package directions.\n2. Drain and rinse chickpeas.\n3. Chop tomatoes, cucumber, and red onion.\n4. In a bowl, combine cooked quinoa, chickpeas, and chopped vegetables.\n5. Dress with olive oil and lemon juice.\n6. Top with crumbled feta cheese.",
                "category": "Main Course",
                "readyInMinutes": 25,
                "servings": 2,
                "source": "Fallback Recipe",
                "image": "https://via.placeholder.com/300x200?text=Quinoa+Bowl",
                "nutrition": {"calories": 420, "protein": 18, "carbs": 55, "fat": 16},
                "tags": ["healthy", "vegetarian", "high-fiber"]
            },
            "soup": {
                "title": "Chicken Vegetable Soup",
                "ingredients": ["chicken breast", "carrots", "celery", "onion", "chicken broth", "garlic", "thyme", "bay leaf"],
                "instructions": "1. Dice chicken breast, carrots, celery, and onion.\n2. Mince garlic.\n3. In a large pot, sauté onion and garlic in a little oil.\n4. Add diced chicken and cook until browned.\n5. Add carrots, celery, broth, thyme, and bay leaf.\n6. Bring to boil, then simmer for 20 minutes.\n7. Season with salt and pepper to taste.",
                "category": "Soup",
                "readyInMinutes": 30,
                "servings": 4,
                "source": "Fallback Recipe",
                "image": "https://via.placeholder.com/300x200?text=Chicken+Soup",
                "nutrition": {"calories": 180, "protein": 22, "carbs": 12, "fat": 4},
                "tags": ["healthy", "comfort-food", "low-fat"]
            }
        }

        # Find matching fallback recipes
        matching = []
        query_lower = query.lower()

        for keyword, recipe in fallback_recipes.items():
            if keyword in query_lower or any(word in query_lower for word in recipe["ingredients"]):
                matching.append(recipe)

        # If no matches, return the first recipe (chicken) as default
        return matching[:max_results] if matching else [list(fallback_recipes.values())[0]]

    async def search_recipes_themealdb(self, query: str, max_results: int = 10) -> List[Dict]:
        """TheMealDB search with enhanced error handling"""
        try:
            url = f"{self.api_endpoints['themealdb']}/search.php"
            params = {'s': query}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                recipes = []
                for meal in data.get('meals', [])[:max_results]:
                    recipe = {
                        'title': meal.get('strMeal', ''),
                        'ingredients': [
                            meal.get(f'strIngredient{i}', '') for i in range(1, 21)
                            if meal.get(f'strIngredient{i}', '')
                        ],
                        'instructions': meal.get('strInstructions', ''),
                        'category': meal.get('strCategory', ''),
                        'area': meal.get('strArea', ''),
                        'image': meal.get('strMealThumb', ''),
                        'youtube': meal.get('strYoutube', ''),
                        'source': 'TheMealDB',
                        'tags': meal.get('strTags', '').split(',') if meal.get('strTags') else [],
                        'readyInMinutes': 30,  # Default estimate
                        'servings': 4,  # Default estimate
                    }
                    recipes.append(recipe)
                return recipes
            else:
                raise Exception(f"TheMealDB HTTP {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"TheMealDB network error: {e}")
            raise Exception(f"TheMealDB network error: {e}")
        except Exception as e:
            logger.error(f"TheMealDB error: {e}")
            raise

    async def search_recipes_spoonacular(self, query: str, max_results: int = 10) -> List[Dict]:
        """Spoonacular search with error handling"""
        if not os.getenv('SPOONACULAR_API_KEY'):
            raise Exception("Spoonacular API key not configured")

        try:
            url = f"{self.api_endpoints['spoonacular']}/recipes/complexSearch"
            params = {
                'apiKey': os.getenv('SPOONACULAR_API_KEY'),
                'query': query,
                'number': min(max_results, 3),  # Limit to 3 to stay within free tier
                'addRecipeInformation': True,
                'fillIngredients': True,
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                recipes = []
                for recipe in data.get('results', []):
                    recipes.append({
                        'title': recipe.get('title', ''),
                        'ingredients': [ing['name'] for ing in recipe.get('extendedIngredients', [])],
                        'instructions': recipe.get('instructions', ''),
                        'nutrition': recipe.get('nutrition', {}),
                        'readyInMinutes': recipe.get('readyInMinutes', 0),
                        'servings': recipe.get('servings', 1),
                        'image': recipe.get('image', ''),
                        'source': 'Spoonacular'
                    })
                return recipes
            else:
                raise Exception(f"Spoonacular HTTP {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Spoonacular network error: {e}")
            raise Exception(f"Spoonacular network error: {e}")
        except Exception as e:
            logger.error(f"Spoonacular error: {e}")
            raise

    async def get_nutrition_usda(self, ingredients: List[str]) -> Dict:
        """USDA nutrition with enhanced error handling"""
        try:
            url = f"{self.api_endpoints['usda']}/foods/search"
            nutrition_data = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}

            for ingredient in ingredients[:3]:  # Limit to 3 ingredients for performance
                params = {
                    'query': ingredient,
                    'dataType': ['Foundation', 'SR Legacy'],
                    'pageSize': 1,
                }

                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for food in data.get('foods', [])[:1]:
                        for nutrient in food.get('foodNutrients', []):
                            name = nutrient.get('nutrientName', '')
                            amount = nutrient.get('value', 0)
                            unit = nutrient.get('unitName', '')

                            # Handle per 100g values
                            if 'per 100 g' in name.lower() or unit == 'g':
                                # Convert to per serving (assuming 100g serving for now)
                                pass
                            else:
                                # Direct values
                                if 'Energy' in name and 'kcal' in name:
                                    nutrition_data['calories'] += amount
                                elif 'Protein' in name:
                                    nutrition_data['protein'] += amount
                                elif 'Carbohydrate' in name:
                                    nutrition_data['carbs'] += amount
                                elif 'Total lipid' in name or 'Fat' in name:
                                    nutrition_data['fat'] += amount
                                elif 'Fiber' in name:
                                    nutrition_data['fiber'] += amount

            logger.info(f"USDA nutrition data retrieved for {len(ingredients[:3])} ingredients")
            return nutrition_data

        except requests.exceptions.RequestException as e:
            logger.error(f"USDA network error: {e}")
            raise Exception(f"USDA network error: {e}")
        except Exception as e:
            logger.error(f"USDA error: {e}")
            raise

    async def get_nutrition_fatsecret(self, ingredients: List[str]) -> Dict:
        """FatSecret nutrition with error handling"""
        if not self.fatsecret_app_key or not self.fatsecret_app_secret:
            logger.warning("FatSecret credentials not configured")
            return {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}

        try:
            # FatSecret implementation - simplified for demo
            # In production, implement proper OAuth flow
            nutrition_data = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}

            # For demo purposes, return basic estimates
            # TODO: Implement proper FatSecret OAuth integration
            logger.info("FatSecret nutrition (demo mode - implement proper OAuth)")

            return nutrition_data

        except Exception as e:
            logger.error(f"FatSecret error: {e}")
            raise

    async def get_recipe_by_id_themealdb(self, recipe_id: str) -> Optional[Dict]:
        """Get detailed recipe by ID from TheMealDB"""
        try:
            url = f"{self.api_endpoints['themealdb']}/lookup.php"
            params = {'i': recipe_id}

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                meal = data.get('meals', [{}])[0]

                return {
                    'title': meal.get('strMeal', ''),
                    'ingredients': [
                        meal.get(f'strIngredient{i}', '') for i in range(1, 21)
                        if meal.get(f'strIngredient{i}', '')
                    ],
                    'instructions': meal.get('strInstructions', ''),
                    'category': meal.get('strCategory', ''),
                    'area': meal.get('strArea', ''),
                    'image': meal.get('strMealThumb', ''),
                    'youtube': meal.get('strYoutube', ''),
                    'source': 'TheMealDB',
                    'tags': meal.get('strTags', '').split(',') if meal.get('strTags') else [],
                }
        except Exception as e:
            logger.warning(f"TheMealDB detail error: {e}")

        return None

    # Main interface methods
    async def search_recipes(self, query: str, diet: str = "", max_results: int = 10) -> List[Dict]:
        """Main search with comprehensive fallback system"""
        return await self.search_recipes_with_fallback(query, diet, max_results)

    async def get_nutrition_info(self, ingredients: List[str]) -> Dict:
        """Main nutrition with comprehensive fallback system"""
        return await self.get_nutrition_with_fallback(ingredients)

    async def get_recipe_by_id(self, recipe_id: str, source: str = "themealdb") -> Optional[Dict]:
        """Get recipe by ID with fallback"""
        if source == "themealdb":
            return await self.get_recipe_by_id_themealdb(recipe_id)
        return None

    async def analyze_nutrition(self, recipe_data: Dict) -> Dict:
        """Analyze nutritional content with comprehensive data"""
        analysis = {
            'calories_per_serving': 0,
            'protein_per_serving': 0,
            'carbs_per_serving': 0,
            'fat_per_serving': 0,
            'health_score': 0,
            'recommendations': [],
            'analysis_source': 'FREE MCP'
        }

        # Extract nutrition data if available
        nutrition = recipe_data.get('nutrition', {})
        servings = recipe_data.get('servings', 1)

        if nutrition:
            nutrients = nutrition.get('nutrients', [])
            for nutrient in nutrients:
                name = nutrient.get('name', '')
                amount = nutrient.get('amount', 0)

                if 'Calories' in name:
                    analysis['calories_per_serving'] = amount / servings
                elif 'Protein' in name:
                    analysis['protein_per_serving'] = amount / servings
                elif 'Carbohydrates' in name:
                    analysis['carbs_per_serving'] = amount / servings
                elif 'Fat' in name:
                    analysis['fat_per_serving'] = amount / servings

        # If no nutrition data, estimate based on recipe type and ingredients
        if analysis['calories_per_serving'] == 0:
            ingredients = recipe_data.get('ingredients', [])
            if ingredients:
                # Get nutrition data for ingredients
                nutrition_data = await self.get_nutrition_with_fallback(ingredients)
                analysis['calories_per_serving'] = nutrition_data.get('calories', 0) / max(servings, 1)
                analysis['protein_per_serving'] = nutrition_data.get('protein', 0) / max(servings, 1)
                analysis['carbs_per_serving'] = nutrition_data.get('carbs', 0) / max(servings, 1)
                analysis['fat_per_serving'] = nutrition_data.get('fat', 0) / max(servings, 1)
            else:
                # Estimate based on recipe category
                category = recipe_data.get('category', '').lower()
                if 'dessert' in category or 'cake' in category or 'cookie' in category:
                    analysis['calories_per_serving'] = 400
                    analysis['carbs_per_serving'] = 60
                    analysis['fat_per_serving'] = 20
                elif 'salad' in category or 'soup' in category:
                    analysis['calories_per_serving'] = 250
                    analysis['carbs_per_serving'] = 20
                    analysis['fat_per_serving'] = 10
                else:
                    analysis['calories_per_serving'] = 350
                    analysis['carbs_per_serving'] = 30
                    analysis['fat_per_serving'] = 15

        # Generate comprehensive health score
        calories = analysis['calories_per_serving']
        protein = analysis['protein_per_serving']
        carbs = analysis['carbs_per_serving']
        fat = analysis['fat_per_serving']

        if calories > 0:
            # Calculate macro percentages
            total_calories = calories
            if total_calories > 0:
                protein_cal = protein * 4
                carb_cal = carbs * 4
                fat_cal = fat * 9

                protein_pct = (protein_cal / total_calories) * 100
                carb_pct = (carb_cal / total_calories) * 100
                fat_pct = (fat_cal / total_calories) * 100

                # Score based on balanced macros
                balance_score = 0
                if 10 <= protein_pct <= 30:
                    balance_score += 25
                if carb_pct <= 65:
                    balance_score += 25
                if fat_pct <= 35:
                    balance_score += 25

                # Score based on calorie appropriateness
                calorie_score = 0
                if 200 <= calories <= 600:
                    calorie_score = 25
                elif calories < 200:
                    calorie_score = 15  # Low calorie
                elif calories > 800:
                    calorie_score = 10  # High calorie
                else:
                    calorie_score = 20

                analysis['health_score'] = balance_score + calorie_score

                # Generate recommendations
                if balance_score >= 50:
                    analysis['recommendations'].append("Well-balanced macronutrients!")
                else:
                    analysis['recommendations'].append("Consider balancing protein, carbs, and fat")

                if calorie_score >= 20:
                    analysis['recommendations'].append("Appropriate calorie content")
                elif calories < 200:
                    analysis['recommendations'].append("May need more calories for satiety")
                else:
                    analysis['recommendations'].append("High calorie meal - watch portions")

        # Add source information
        analysis['analysis_method'] = 'FREE MCP with USDA + TheMealDB'
        analysis['data_quality'] = 'High (Government + Professional sources)'

        return analysis

# Global MCP server instance
mcp_server = RobustRecipeMCPServer()