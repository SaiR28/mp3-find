from flask import Flask, render_template, request, jsonify
import asyncio
from shazamio import Shazam
from moviepy.editor import VideoFileClip
from instaloader import Instaloader, Post
import os
import re
from spotify import get_spotify_track_url  # Import the Spotify utility function
from ytm import search_youtube_music  # Import the YouTube Music search function

app = Flask(__name__)

# Spotify API credentials
SPOTIFY_CLIENT_ID = "513d546b76014375a14763f9bbc8c3eb"
SPOTIFY_CLIENT_SECRET = "0a159fc7a1124ec08998b83a2846945d"

async def download_reel(url):
    """Download an Instagram reel and return the path to the downloaded video file."""
    try:
        L = Instaloader()
        shortcode_match = re.search(r"/reel/([^/?]+)", url)
        if not shortcode_match:
            raise ValueError("Invalid Instagram reel URL")
            
        shortcode = shortcode_match.group(1)
        post = Post.from_shortcode(L.context, shortcode)
        
        target_dir = f"reel_{shortcode}"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        L.download_post(post, target=target_dir)
        
        video_file = None
        for file in os.listdir(target_dir):
            if file.endswith('.mp4'):
                video_file = os.path.join(target_dir, file)
                break

        return video_file
    except Exception as e:
        return None

async def convert_video_to_mp3(video_path):
    """Convert video to MP3 audio."""
    try:
        filename = os.path.splitext(video_path)[0]
        mp3_path = f"{filename}.mp3"
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(mp3_path)
        video.close()
        return mp3_path
    except Exception as e:
        return None

async def identify_song(audio_path):
    """Identify song using Shazam API."""
    try:
        shazam = Shazam()
        out = await shazam.recognize(audio_path)
        track_info = out.get("track", {})
        song_details = {
            "title": track_info.get("title", "N/A"),
            "artist": track_info.get("subtitle", "N/A"),
            "album": "N/A",
            "genre": track_info.get("genres", {}).get("primary", "N/A"),
            "cover_art": track_info.get("images", {}).get("coverart", "N/A"),
            "cover_art_hq": track_info.get("images", {}).get("coverarthq", "N/A")
        }
        sections = track_info.get("sections", [{}])
        if sections:
            metadata = sections[0].get("metadata", [])
            for meta in metadata:
                if meta.get("title") == "Album":
                    song_details["album"] = meta.get("text", "N/A")
                    break
        return song_details
    except Exception as e:
        return None

async def cleanup_files(video_path, mp3_path):
    """Clean up temporary files."""
    try:
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
        
        if os.path.exists(video_path):
            video_dir = os.path.dirname(video_path)
            if video_dir.startswith('reel_'):
                for file in os.listdir(video_dir):
                    os.remove(os.path.join(video_dir, file))
                os.rmdir(video_dir)
    except Exception as e:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_reel', methods=['POST'])
def process_reel():
    reel_url = request.form.get('reel_url')
    if not reel_url:
        return jsonify({"error": "Invalid URL"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    video_path = loop.run_until_complete(download_reel(reel_url))
    if not video_path:
        return jsonify({"error": "Failed to download reel"}), 500

    mp3_path = loop.run_until_complete(convert_video_to_mp3(video_path))
    if not mp3_path:
        loop.run_until_complete(cleanup_files(video_path, None))
        return jsonify({"error": "Failed to convert video to MP3"}), 500

    song_details = loop.run_until_complete(identify_song(mp3_path))
    loop.run_until_complete(cleanup_files(video_path, mp3_path))

    if not song_details:
        return jsonify({"error": "Failed to identify the song"}), 500
    
    # Use YouTube Music API to find a direct link
    youtube_music_result = search_youtube_music(song_details["title"])

    if isinstance(youtube_music_result, dict) and 'YouTube Music' in youtube_music_result:
        song_details["youtube_music_url"] = youtube_music_result["YouTube Music"]
    else:
        song_details["youtube_music_url"] = "No YouTube Music link found"

    # Use Spotify API to find a direct link
    spotify_result = get_spotify_track_url(
        song_name=song_details["title"],
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )

    if isinstance(spotify_result, dict) and 'url' in spotify_result:
        song_details["spotify_url"] = spotify_result["url"]
    else:
        song_details["spotify_url"] = "No Spotify link found"

    return jsonify(song_details)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

