import asyncio
from shazamio import Shazam
from moviepy.editor import VideoFileClip
from instaloader import Instaloader, Post
import os
import re

async def download_reel(url):
    """
    Download an Instagram reel and return the path to the downloaded video file.
    
    Args:
        url (str): URL of the Instagram reel
    
    Returns:
        str: Path to the downloaded video file, or None if download fails
    """
    try:
        # Initialize instaloader
        L = Instaloader()
        
        # Extract shortcode from URL
        shortcode_match = re.search(r"/reel/([^/?]+)", url)
        if not shortcode_match:
            raise ValueError("Invalid Instagram reel URL")
            
        shortcode = shortcode_match.group(1)
        
        # Get post by shortcode
        post = Post.from_shortcode(L.context, shortcode)
        
        # Create target directory if it doesn't exist
        target_dir = f"reel_{shortcode}"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Download the video
        L.download_post(post, target=target_dir)
        
        # Find the downloaded video file
        video_file = None
        for file in os.listdir(target_dir):
            if file.endswith('.mp4'):
                video_file = os.path.join(target_dir, file)
                break
        
        if not video_file:
            raise Exception("Video file not found in downloaded content")
        
        print(f"Successfully downloaded reel: {shortcode}")
        return video_file
        
    except Exception as e:
        print(f"Error downloading reel: {str(e)}")
        return None

async def convert_video_to_mp3(video_path):
    """Convert video to MP3 audio."""
    try:
        # Extract filename without extension
        filename = os.path.splitext(video_path)[0]
        mp3_path = f"{filename}.mp3"
        
        # Load the video and extract audio
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(mp3_path)
        video.close()
        
        return mp3_path
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return None

async def identify_song(audio_path):
    """Identify song using Shazam API."""
    try:
        shazam = Shazam()
        out = await shazam.recognize(audio_path)
        
        # Extracting specific details
        track_info = out.get("track", {})
        
        # Get basic track information
        song_details = {
            "title": track_info.get("title", "N/A"),
            "artist": track_info.get("subtitle", "N/A"),
            "album": "N/A",
            "genre": track_info.get("genres", {}).get("primary", "N/A"),
            "url": track_info.get("share", {}).get("href", "N/A"),
            "cover_art": track_info.get("images", {}).get("coverart", "N/A"),
            "cover_art_hq": track_info.get("images", {}).get("coverarthq", "N/A")
        }
        
        # Get album name from metadata if available
        sections = track_info.get("sections", [{}])
        if sections:
            metadata = sections[0].get("metadata", [])
            for meta in metadata:
                if meta.get("title") == "Album":
                    song_details["album"] = meta.get("text", "N/A")
                    break
        
        return song_details
    except Exception as e:
        print(f"Error during song identification: {str(e)}")
        return None

async def cleanup_files(video_path, mp3_path):
    """Clean up temporary files."""
    try:
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
            print(f"Removed temporary MP3 file: {mp3_path}")
        
        if os.path.exists(video_path):
            os.remove(video_path)
            video_dir = os.path.dirname(video_path)
            if video_dir.startswith('reel_'):
                # Remove the entire reel directory and its contents
                for file in os.listdir(video_dir):
                    file_path = os.path.join(video_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(video_dir)
                print(f"Removed temporary video directory: {video_dir}")
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

async def main():
    # Get Instagram reel URL from user
    reel_url = input("Enter the Instagram reel URL: ")
    
    print("\nStep 1: Downloading Instagram reel...")
    video_path = await download_reel(reel_url)
    
    if not video_path:
        print("Failed to download the reel. Exiting.")
        return
    
    print("\nStep 2: Converting video to MP3...")
    mp3_path = await convert_video_to_mp3(video_path)
    
    if not mp3_path:
        print("Failed to convert video to MP3. Exiting.")
        await cleanup_files(video_path, None)
        return
    
    print("\nStep 3: Identifying song...")
    song_details = await identify_song(mp3_path)
    
    if song_details:
        print("\nSong Details:")
        print(f"Title: {song_details['title']}")
        print(f"Artist: {song_details['artist']}")
        print(f"Album: {song_details['album']}")
        print(f"Genre: {song_details['genre']}")
        print(f"URL: {song_details['url']}")
        print(f"Cover Art: {song_details['cover_art']}")
        print(f"Cover Art (High Quality): {song_details['cover_art_hq']}")
    else:
        print("Failed to identify the song.")
    
    # Clean up temporary files
    await cleanup_files(video_path, mp3_path)

if __name__ == "__main__":
    # Running the event loop
    asyncio.run(main())