import os
from pytube import YouTube
from moviepy.editor import VideoFileClip
from .helpers import clean_filename

def download_video(url, only_info=False):
    try:
        yt = YouTube(url)
        info = {
            'title': yt.title,
            'duration': yt.length,
            'channel': yt.author,
            'thumbnail': yt.thumbnail_url,
            'url': url
        }
        
        if only_info:
            return info
            
        stream = yt.streams.filter(
            progressive=True,
            file_extension='mp4'
        ).order_by('resolution').desc().first()
        
        os.makedirs("downloads", exist_ok=True)
        filename = clean_filename(yt.title) + ".mp4"
        filepath = os.path.join("downloads", filename)
        
        stream.download(output_path="downloads", filename=filename)
        return filepath
        
    except Exception as e:
        raise Exception(f"Download error: {str(e)}")

def download_audio(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(
            only_audio=True,
            file_extension='mp4'
        ).order_by('abr').desc().first()
        
        os.makedirs("downloads", exist_ok=True)
        filename = clean_filename(yt.title) + ".mp4"
        filepath = os.path.join("downloads", filename)
        
        stream.download(output_path="downloads", filename=filename)
        
        mp3_path = os.path.join("downloads", clean_filename(yt.title) + ".mp3")
        VideoFileClip(filepath).audio.write_audiofile(mp3_path)
        
        os.remove(filepath)
        return mp3_path
        
    except Exception as e:
        raise Exception(f"Audio error: {str(e)}")