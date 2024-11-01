from instaloader import Instaloader, Post
import re

def download_reel(url):
    """
    Download an Instagram reel given its URL
    
    Args:
        url (str): URL of the Instagram reel
    """
    try:
        # Initialize instaloader
        L = Instaloader()
        
        # Extract shortcode from URL
        shortcode = re.search(r"/reel/([^/?]+)", url).group(1)
        
        # Get post by shortcode
        post = Post.from_shortcode(L.context, shortcode)
        
        # Download the video
        L.download_post(post, target=f"reel_{shortcode}")
        
        print(f"Successfully downloaded reel: {shortcode}")
        
    except Exception as e:
        print(f"Error downloading reel: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Replace with your reel URL
    reel_url = "https://www.instagram.com/reel/C8wrKbkP4dc/?igsh=YzM2c2FjamY5eXFy"
    download_reel(reel_url)