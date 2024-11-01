# ytmusic_search.py
from ytmusicapi import YTMusic

# Initialize the YTMusic API
ytmusic = YTMusic()

def search_youtube_music(song_name):
    """
    Search for a song on YouTube Music and return its link.

    Parameters:
    song_name (str): The name of the song to search for.

    Returns:
    dict: A dictionary containing the YouTube Music link if found.
    """
    # Search for the song
    search_results = ytmusic.search(song_name, filter='songs')

    results = {}
    if search_results:
        # Get the first result
        video = search_results[0]
        video_id = video['videoId']
        results['YouTube Music'] = f'https://music.youtube.com/watch?v={video_id}'

    return results

