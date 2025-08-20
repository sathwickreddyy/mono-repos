from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

# Sample data - similar to Java service but from Python perspective
items_db = [
    {"id": 1, "name": "FastAPI Service", "description": "Python-based async API"},
    {"id": 2, "name": "Uvicorn Server", "description": "ASGI web server"},
    {"id": 3, "name": "Pydantic Models", "description": "Data validation library"},
]

@router.get("/items")
async def get_items() -> List[Dict[str, Any]]:
    """Get all items - equivalent to Java's @GetMapping"""
    return items_db

@router.get("/items/{item_id}")
async def get_item(item_id: int) -> Dict[str, Any]:
    """Get single item by ID - equivalent to Java's @PathVariable"""
    item = next((item for item in items_db if item["id"] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
