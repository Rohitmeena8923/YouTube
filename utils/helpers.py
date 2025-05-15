import re
import os

def clean_filename(filename):
    """Clean filename to remove invalid characters."""
    # Remove invalid characters
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Limit length to avoid filesystem issues
    return cleaned[:100]

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"