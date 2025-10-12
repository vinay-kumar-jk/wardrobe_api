# wardrobe_utils.py
import pandas as pd

def load_wardrobe_from_json(data):
    """
    Load wardrobe data from JSON (sent by Flutter app).
    Returns a pandas DataFrame.
    """
    if not data or len(data) == 0:
        return pd.DataFrame()
    return pd.DataFrame(data)

def determine_season(material, coverage):
    """
    Determine a suitable weather type for an item based on its material and coverage.
    material: string (e.g., 'cotton', 'wool', 'polyester')
    coverage: string ('full' or 'partial')
    """
    material = material.lower()
    coverage = coverage.lower()
    
    # Heavy materials for cold weather
    if material in ['wool', 'fleece', 'cashmere', 'down', 'corduroy']:
        return 'winter'

    # Light, breathable materials for hot weather
    if material in ['linen', 'rayon', 'seersucker'] or (material == 'cotton' and coverage == 'partial'):
        return 'hot'
        
    # Water-resistant materials are great for rain
    if material in ['polyester', 'nylon', 'gore-tex']:
        return 'rainy'

    # Default for most other items like jeans (denim), full-sleeve cotton shirts, etc.
    return 'moderate'