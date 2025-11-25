# ----- README -----
"""
Recommendation Microservice for CampusConnect
Created by: Derik and Lea

Required installations:
    pip install fastapi uvicorn

Run the server:
    uvicorn RecommendationService:app --reload --port 4000
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import json
from datetime import datetime

app = FastAPI()

# Enable CORS for CampusConnect frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load club data
with open("clubs.json", "r") as f:
    clubs_data = json.load(f)

# Convert list to dict for easier lookup
clubs_dict = {club["id"]: club for club in clubs_data}

# Store for user recommendations (in production, use a database)
user_recommendations_cache = {}

def calculate_similarity_score(club, favorite_clubs, preferred_categories):
    """
    Calculate how well a club matches user preferences.
    Returns a score between 0 and 1.
    """
    score = 0.0
    weight_category = 0.6
    weight_favorite_similarity = 0.4
    
    # Category matching score
    if club["category"] in preferred_categories:
        score += weight_category
    
    # Similarity to favorite clubs
    if favorite_clubs:
        favorite_categories = set()
        for fav_id in favorite_clubs:
            if fav_id in clubs_dict:
                favorite_categories.add(clubs_dict[fav_id]["category"])
        
        if club["category"] in favorite_categories:
            score += weight_favorite_similarity
    
    # Bonus for technology/engineering overlap (domain knowledge)
    tech_categories = ["Technology", "Engineering", "Science"]
    if club["category"] in tech_categories:
        for fav_id in favorite_clubs:
            if fav_id in clubs_dict and clubs_dict[fav_id]["category"] in tech_categories:
                score += 0.1  # Small bonus for STEM overlap
                break
    
    # Normalize score to [0, 1]
    return min(score, 1.0)

def get_recommendations(user_id, favorites, categories):
    """
    Generate club recommendations based on user preferences.
    """
    recommendations = []
    
    # Get all clubs except the ones already in favorites
    for club_id, club in clubs_dict.items():
        if club_id not in favorites:
            match_score = calculate_similarity_score(club, favorites, categories)
            if match_score > 0:
                recommendations.append({
                    "club_name": club["name"],
                    "category": club["category"],
                    "match_score": round(match_score, 2),
                    "description": club.get("description", ""),
                    "id": club["id"]
                })
    
    # Sort by match score (descending)
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Take top 5 recommendations
    return recommendations[:5]

# ----- Routes -----

@app.post("/recommendations")
async def get_club_recommendations(request: Request) -> Dict[str, Any]:
    """
    Get personalized club recommendations.
    
    Body:
        {
            "user_id": str,
            "favorites": List[str],  # List of club IDs
            "categories": List[str]  # List of interest categories
        }
    
    Returns:
        {
            "user_id": str,
            "recommendations": List[Dict]
        }
    """
    data = await request.json()
    user_id = data.get("user_id")
    favorites = data.get("favorites", [])
    categories = data.get("categories", [])
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    # Generate recommendations
    recommendations = get_recommendations(user_id, favorites, categories)
    
    # Cache the recommendations for the user
    user_recommendations_cache[user_id] = {
        "favorites": favorites,
        "categories": categories,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

@app.get("/category/{category_name}")
async def get_clubs_by_category(category_name: str) -> List[Dict[str, Any]]:
    """
    Get all clubs in a specific category.
    
    Path parameter:
        category_name: The category to filter by
    
    Returns:
        List of clubs matching the category
    """
    matching_clubs = []
    
    for club in clubs_data:
        if club["category"].lower() == category_name.lower():
            matching_clubs.append({
                "id": club["id"],
                "name": club["name"],
                "category": club["category"],
                "description": club.get("description", "")
            })
    
    return matching_clubs

@app.post("/favorites/update")
async def update_favorites(request: Request) -> Dict[str, Any]:
    """
    Update user favorites and recompute recommendations immediately.
    
    Body:
        {
            "user_id": str,
            "favorites": List[str],
            "categories": List[str]
        }
    
    Returns:
        Updated recommendations
    """
    data = await request.json()
    user_id = data.get("user_id")
    favorites = data.get("favorites", [])
    categories = data.get("categories", [])
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    # Get user's cached categories if not provided
    if user_id in user_recommendations_cache and not categories:
        categories = user_recommendations_cache[user_id].get("categories", [])
    
    # Recompute recommendations
    recommendations = get_recommendations(user_id, favorites, categories)
    
    # Update cache
    user_recommendations_cache[user_id] = {
        "favorites": favorites,
        "categories": categories,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        "user_id": user_id,
        "favorites": favorites,
        "recommendations": recommendations,
        "updated": True
    }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Recommendation Microservice",
        "status": "running",
        "endpoints": [
            "POST /recommendations",
            "GET /category/{category_name}",
            "POST /favorites/update"
        ]
    }
