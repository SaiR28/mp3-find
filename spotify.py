# spotify_utils.py

import requests
import base64
from urllib.parse import quote

def get_spotify_track_url(song_name, client_id, client_secret):
    """
    Find Spotify URL for a given song name using Spotify Web API.
    
    Parameters:
    song_name (str): Name of the song to search
    client_id (str): Your Spotify API client ID
    client_secret (str): Your Spotify API client secret
    
    Returns:
    dict: Spotify track details including URL, name, artist, and preview URL, or error message if not found
    """
    
    # Step 1: Get access token
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {'grant_type': 'client_credentials'}
    
    try:
        auth_response = requests.post(auth_url, headers=headers, data=data)
        auth_response.raise_for_status()
        access_token = auth_response.json()['access_token']
        
        # Step 2: Search for the track
        search_url = 'https://api.spotify.com/v1/search'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        # URL encode the song name and create the query
        query = quote(f"track:{song_name}")
        params = {
            'q': query,
            'type': 'track',
            'limit': 1
        }
        
        search_response = requests.get(search_url, headers=headers, params=params)
        search_response.raise_for_status()
        
        results = search_response.json()
        
        # Check if any tracks were found
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            return {
                'url': track['external_urls']['spotify'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'preview_url': track['preview_url']
            }
        else:
            return {"error": "No tracks found for the given song name."}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Error occurred: {str(e)}"}
