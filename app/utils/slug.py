import re
import unicodedata
from typing import Optional

def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    
    Args:
        text: The string to convert to a slug
        
    Returns:
        A URL-friendly slug string
    """
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to ASCII and remove non-word characters
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    
    # Replace whitespace with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    
    return text

def generate_unique_slug(base_slug: str, existing_slugs: list) -> str:
    """
    Generate a unique slug based on a base slug and a list of existing slugs
    
    Args:
        base_slug: The base slug to start with
        existing_slugs: A list of existing slugs to avoid
        
    Returns:
        A unique slug that is not in the existing_slugs list
    """
    slug = base_slug
    counter = 1
    
    while slug in existing_slugs:
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug