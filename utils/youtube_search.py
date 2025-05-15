from pytube import Search

def search_youtube(query, max_results=5):
    try:
        results = []
        for video in Search(query).results[:max_results]:
            results.append({
                'title': video.title,
                'url': video.watch_url,
                'duration': video.length,
                'channel': video.author,
                'thumbnail': video.thumbnail_url
            })
        return results
    except Exception as e:
        raise Exception(f"Search error: {str(e)}")