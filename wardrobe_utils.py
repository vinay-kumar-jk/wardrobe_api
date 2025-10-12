# wardrobe_utils.py
import pandas as pd

def load_wardrobe_from_json(data):
    """
    Load wardrobe data from JSON (sent by Flutter app from Hive DB).
    Returns a pandas DataFrame.
    """
    if not data or len(data) == 0:
        return pd.DataFrame()  # Empty DataFrame if no data
    return pd.DataFrame(data)

def determine_season(material, coverage):
    """
    Determine season based on material and coverage.
    material: string (cotton, wool, fleece, linen, etc.)
    coverage: string ('yes' or 'no') — is it fully covering?
    """
    material = material.lower()
    coverage = coverage.lower()
    
    if material in ['wool', 'fleece']:
        return 'winter'
    elif material in ['cotton', 'linen'] and coverage == 'no':
        return 'moderate'
    else:
        return 'rainy'
