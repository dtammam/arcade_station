"""Utilities for handling game IDs in Arcade Station."""
import re
from typing import Optional, Dict, Any

def generate_game_id(name: str, existing_ids: Optional[Dict[str, Any]] = None) -> str:
    """Generate a clean, URL-safe game ID from a name.
    
    Args:
        name: Display name of the game
        existing_ids: Dictionary of existing game IDs to check for conflicts
        
    Returns:
        str: Generated game ID
    """
    # Remove special chars, lowercase, replace spaces with underscores
    base_id = re.sub(r'[^\w\s-]', '', name.lower())
    base_id = re.sub(r'[-\s]+', '_', base_id)
    
    # If no existing IDs, return base_id
    if not existing_ids:
        return base_id
        
    # If ID exists, append a number
    if base_id in existing_ids:
        counter = 1
        while f"{base_id}_{counter}" in existing_ids:
            counter += 1
        return f"{base_id}_{counter}"
    
    return base_id

def validate_game_id(game_id: str) -> bool:
    """Validate a game ID.
    
    Args:
        game_id: Game ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Only allow lowercase letters, numbers, and underscores
    pattern = r'^[a-z0-9_]+$'
    return bool(re.match(pattern, game_id))

def get_display_name(game_id: str) -> str:
    """Convert a game ID to a display name.
    
    Args:
        game_id: Game ID to convert
        
    Returns:
        str: Display name
    """
    # Replace underscores with spaces and title case
    return game_id.replace('_', ' ').title() 