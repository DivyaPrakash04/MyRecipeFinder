"""
MCP API Endpoints for Recipe Assistant
Provides REST API endpoints for MCP functionality
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from enhanced_recipes import search_recipes_enhanced, get_recipe_nutrition, analyze_recipe_health, get_api_status

logger = logging.getLogger("mcp-endpoints")

# Create MCP blueprint
mcp_bp = Blueprint('mcp', __name__)
CORS(mcp_bp)

@mcp_bp.route('/api/mcp/search', methods=['POST'])
async def search_recipes_mcp():
    """Enhanced recipe search with MCP integration"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        dietary_context = data.get('dietary_context', '')
        max_results = data.get('max_results', 10)
        use_mcp = data.get('use_mcp', True)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Perform enhanced search
        results = await search_recipes_enhanced(
            query=query,
            dietary_context=dietary_context,
            max_results=max_results,
            use_mcp=use_mcp
        )

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"MCP search error: {e}")
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

@mcp_bp.route('/api/mcp/nutrition', methods=['POST'])
async def get_nutrition():
    """Get nutritional information for ingredients"""
    try:
        data = request.get_json()
        ingredients = data.get('ingredients', [])

        if not ingredients:
            return jsonify({'error': 'Ingredients are required'}), 400

        nutrition = await get_recipe_nutrition(ingredients)

        return jsonify({
            'success': True,
            'nutrition': nutrition
        })

    except Exception as e:
        logger.error(f"Nutrition analysis error: {e}")
        return jsonify({'error': 'Nutrition analysis failed', 'details': str(e)}), 500

@mcp_bp.route('/api/mcp/analyze', methods=['POST'])
async def analyze_health():
    """Analyze health aspects of a recipe"""
    try:
        data = request.get_json()
        recipe_data = data.get('recipe_data', {})

        if not recipe_data:
            return jsonify({'error': 'Recipe data is required'}), 400

        analysis = await analyze_recipe_health(recipe_data)

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        logger.error(f"Health analysis error: {e}")
        return jsonify({'error': 'Health analysis failed', 'details': str(e)}), 500

@mcp_bp.route('/api/mcp/status', methods=['GET'])
def get_mcp_status():
    """Get MCP API status and availability"""
    try:
        status = get_api_status()

        return jsonify({
            'success': True,
            'status': status
        })

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'error': 'Status check failed', 'details': str(e)}), 500

@mcp_bp.route('/api/mcp/test', methods=['GET'])
def test_mcp():
    """Test MCP connectivity"""
    try:
        # Test basic connectivity
        status = get_api_status()

        test_results = {
            'mcp_server': 'available',
            'apis_available': [],
            'tests_passed': 0,
            'tests_total': 0
        }

        # Test each available API
        test_results['tests_total'] = len(status['apis'])

        for api_name, available in status['apis'].items():
            if available:
                test_results['apis_available'].append(api_name)
                test_results['tests_passed'] += 1

        return jsonify({
            'success': True,
            'test_results': test_results,
            'message': f"MCP is operational. {test_results['tests_passed']}/{test_results['tests_total']} APIs available."
        })

    except Exception as e:
        logger.error(f"MCP test error: {e}")
        return jsonify({
            'success': False,
            'error': 'MCP test failed',
            'details': str(e)
        }), 500

# Helper function to register MCP endpoints in main app
def register_mcp_endpoints(app):
    """Register MCP endpoints with the Flask app"""
    app.register_blueprint(mcp_bp)
    logger.info("MCP endpoints registered")
