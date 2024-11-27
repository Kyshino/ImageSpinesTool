import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import praw
import requests
from urllib.parse import urlparse
from pathlib import Path
import re
from PIL import Image
from io import BytesIO
from utils.config_manager import (get_reddit_client_id, get_reddit_client_secret)

class SwitchSpinesDownloader:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=get_reddit_client_id(),
            client_secret=get_reddit_client_secret(),
            user_agent="SwitchSpineScraper/1.0"
        )
        
        while True:
            self.output_dir = input("Enter the output directory for downloaded spines: ").strip()
            if os.path.exists(self.output_dir):
                break
            create = input(f"Directory '{self.output_dir}' does not exist. Create it? (y/n): ").lower()
            if create == 'y':
                Path(self.output_dir).mkdir(parents=True, exist_ok=True)
                break
            print("Please enter a valid directory path.")

    def clean_filename(self, filename):
        cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
        return cleaned[:200]

    def generate_unique_filename(self, base_filename):
        version = 1
        filename = f"{base_filename}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        while os.path.exists(filepath):
            filename = f"{base_filename}_v{version}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            version += 1
        
        return filepath, filename

    def download_image(self, url, title):
        try:
            base_filename = self.clean_filename(title)
            filepath, filename = self.generate_unique_filename(base_filename)
            
            response = requests.get(url)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            required_width = 122
            required_height = 1906
            margin_width = int(required_width * 0.1)
            margin_height = int(required_height * 0.1)
            
            if (img.width >= (required_width - margin_width) and
                img.width <= (required_width + margin_width) and
                img.height >= (required_height - margin_height) and
                img.height <= (required_height + margin_height)):
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Image downloaded: {filename}")
                return True
            else:
                print(f"❌ Image {filename} does not meet size requirements.")
                return False
            
        except Exception as e:
            print(f"❌ Error downloading {url}: {str(e)}")
            return False

    def download_all(self):
        print(" Starting spine images download...")
        downloaded = 0
        skipped = 0
        
        try:            
            for listing in ['hot', 'new', 'top']:
                print(f"\n🔄 Getting posts from section: {listing.capitalize()}")
                posts = self.get_posts(listing)

                for post in posts:                        
                    if hasattr(post, 'media_metadata'):
                        for media_id, media_info in post.media_metadata.items():
                            if media_info['status'] == 'valid' and media_info['e'] == 'Image':
                                image_url = media_info['s']['u']
                                if self.download_image(image_url, post.title):
                                    downloaded += 1
                                else:
                                    skipped += 1

            self.print_summary(downloaded, skipped)
            return True
            
        except Exception as e:
            print(f"❌ Error during download: {str(e)}")
            raise

    def get_posts(self, listing):
        if listing == 'top':
            return self.reddit.subreddit('SwitchSpines').top(limit=None, time_filter='all')
        elif listing == 'new':
            return self.reddit.subreddit('SwitchSpines').new(limit=None)
        else:
            return self.reddit.subreddit('SwitchSpines').hot(limit=None)

    def print_summary(self, downloaded, skipped):
        print(f"\n📊 Final Summary:")
        print(f"✅ Images downloaded: {downloaded}")
        print(f"❌ Images skipped: {skipped}")
        print(f"📁 Download location: {os.path.abspath(self.output_dir)}")

def main():
    downloader = SwitchSpinesDownloader()
    downloader.download_all()

if __name__ == "__main__":
    main()