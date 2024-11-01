import asyncio
from shazamio import Shazam
from moviepy.editor import VideoFileClip
import os

async def convert_mp4_to_mp3(mp4_path):
    """Convert MP4 video to MP3 audio."""
    try:
        # Extract filename without extension
        filename = os.path.splitext(mp4_path)[0]
        mp3_path = f"{filename}.mp3"
        
        # Load the video and extract audio
        video = VideoFileClip(mp4_path)
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

async def main():
    # Get input MP4 file path from user
    mp4_path = input("Enter the path to your MP4 file: ")
    
    # Check if file exists
    if not os.path.exists(mp4_path):
        print("Error: File does not exist!")
        return
    
    print("Converting MP4 to MP3...")
    mp3_path = await convert_mp4_to_mp3(mp4_path)
    
    if mp3_path:
        print("Identifying song...")
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
            
            # Optional: Clean up the temporary MP3 file
            try:
                os.remove(mp3_path)
                print(f"\nTemporary MP3 file removed: {mp3_path}")
            except Exception as e:
                print(f"Error removing temporary MP3 file: {str(e)}")
        else:
            print("Failed to identify the song.")
    else:
        print("Failed to convert the video.")

if __name__ == "__main__":
    # Running the event loop
    asyncio.run(main())