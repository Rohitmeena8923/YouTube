from pytube import Search
from pytube.exceptions import PytubeError
from .helpers import clean_filename

def search_youtube(query, max_results=5):
    """Search YouTube and return results."""
    try:
        s = Search(query)
        results = []
        
        for video in s.results[:max_results]:
            results.append({
                'title': video.title,
                'url': video.watch_url,
                'duration': video.length,
                'channel': video.author,
                'thumbnail': video.thumbnail_url
            })
        
        return results
    except Exception as e:
        raise Exception(f"Error searching YouTube: {str(e)}")