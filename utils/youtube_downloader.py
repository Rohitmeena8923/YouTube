
import os
from pytube import YouTube
from moviepy.editor import VideoFileClip
import logging

def download_video(url, only_info=False):
    try:
        yt = YouTube(url)
        info = {
            'title': yt.title,
            'duration': yt.length,
            'thumbnail': yt.thumbnail_url,
            'channel': yt.author
        }
        
        if only_info:
            return info
            
        stream = yt.streams.filter(
            progressive=True,
            file_extension='mp4',
            resolution='720p'
        ).first()
        
        if not stream:
            stream = yt.streams.get_highest_resolution()
            
        os.makedirs("downloads", exist_ok=True)
        filename = f"{yt.video_id}.mp4"
        filepath = os.path.join("downloads", filename)
        stream.download(output_path="downloads", filename=filename)
        return filepath
        
    except Exception as e:
        logging.error(f"Video download error: {e}")
        raise Exception("Video download failed")

def download_audio(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(
            only_audio=True,
            file_extension='mp4'
        ).order_by('abr').desc().first()
        
        os.makedirs("downloads", exist_ok=True)
        filename = f"{yt.video_id}.mp4"
        filepath = os.path.join("downloads", filename)
        stream.download(output_path="downloads", filename=filename)
        
        mp3_path = os.path.join("downloads", f"{yt.video_id}.mp3")
        VideoFileClip(filepath).audio.write_audiofile(mp3_path)
        os.remove(filepath)
        return mp3_path
        
    except Exception as e:
        logging.error(f"Audio download error: {e}")
        raise Exception("Audio download failed")