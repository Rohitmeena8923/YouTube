import os
import re
from pytube import YouTube
from pytube.exceptions import PytubeError
from moviepy.editor import VideoFileClip
from urllib.parse import urlparse, parse_qs
from .helpers import clean_filename

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path.startswith('/embed/'):
            return query.path.split('/')[2]
        if query.path.startswith('/v/'):
            return query.path.split('/')[2]
    return None

def download_video(url, only_info=False):
    """Download YouTube video or return info if only_info=True."""
    try:
        yt = YouTube(url)
        video_info = {
            'title': yt.title,
            'duration': yt.length,
            'channel': yt.author,
            'view_count': yt.views,
            'thumbnail': yt.thumbnail_url,
            'url': url
        }
        
        if only_info:
            return video_info
        
        # Get the best progressive stream (video + audio)
        stream = yt.streams.filter(
            progressive=True,
            file_extension='mp4'
        ).order_by('resolution').desc().first()
        
        if not stream:
            raise PytubeError("No suitable stream found")
        
        # Download the video
        output_path = "downloads"
        os.makedirs(output_path, exist_ok=True)
        filename = clean_filename(yt.title) + ".mp4"
        filepath = os.path.join(output_path, filename)
        
        stream.download(output_path=output_path, filename=filename)
        return filepath
    
    except Exception as e:
        raise Exception(f"Error downloading video: {str(e)}")

def download_audio(url):
    """Download YouTube video as MP3 audio."""
    try:
        yt = YouTube(url)
        
        # Get the best audio stream
        stream = yt.streams.filter(
            only_audio=True,
            file_extension='mp4'
        ).order_by('abr').desc().first()
        
        if not stream:
            raise PytubeError("No audio stream found")
        
        # Download the audio
        output_path = "downloads"
        os.makedirs(output_path, exist_ok=True)
        filename = clean_filename(yt.title) + ".mp4"
        filepath = os.path.join(output_path, filename)
        
        stream.download(output_path=output_path, filename=filename)
        
        # Convert to MP3
        mp3_filename = clean_filename(yt.title) + ".mp3"
        mp3_path = os.path.join(output_path, mp3_filename)
        
        video_clip = VideoFileClip(filepath)
        video_clip.audio.write_audiofile(mp3_path)
        video_clip.close()
        
        os.remove(filepath)  # Remove the original file
        return mp3_path
    
    except Exception as e:
        raise Exception(f"Error downloading audio: {str(e)}")