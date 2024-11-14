import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import praw
import requests
from urllib.parse import urlparse
from pathlib import Path
import re
from PIL import Image
from io import BytesIO
from utils.config_manager import (get_image_folder, 
                                get_reddit_client_id,
                                get_reddit_client_secret)

class SwitchSpinesDownloader:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=get_reddit_client_id(),
            client_secret=get_reddit_client_secret(),
            user_agent="SwitchSpineScraper/1.0"
        )
        
        config_folder = get_image_folder()
        self.output_dir = config_folder if os.path.exists(config_folder) else "downloaded_spines"
        Path(self.output_dir).mkdir(exist_ok=True)
        
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def get_all_posts(self):
        all_posts = []
        processed_urls = set()
        
        for listing in ['hot', 'new', 'top']:
            if listing == 'top':
                posts = self.reddit.subreddit('SwitchSpines').top(limit=None, time_filter='all')
            elif listing == 'new':
                posts = self.reddit.subreddit('SwitchSpines').new(limit=None)
            else:
                posts = self.reddit.subreddit('SwitchSpines').hot(limit=None)
                
            for post in posts:
                if post.url in processed_urls:
                    continue
                if hasattr(post, 'url') and any(post.url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    all_posts.append(post)
                    processed_urls.add(post.url)
        
        return all_posts

    def is_switch_spine(self, image_data):
        try:
            img = Image.open(BytesIO(image_data))
            width, height = img.size
            
            expected_width = 122
            expected_height = 1906
            width_margin = expected_width * 0.2
            height_margin = expected_height * 0.2
            
            is_spine_dimension = (
                abs(width - expected_width) <= width_margin and
                abs(height - expected_height) <= height_margin
            )
            
            if not is_spine_dimension:
                print(f"  📏 Incorrect dimensions: {width}x{height}")
                return False
                
            print(f"  📊 Image analysis:")
            print(f"    - Dimensions: {width}x{height} ✅")
            return True
            
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return False

    def clean_filename(self, filename):
        cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
        return cleaned[:200]

    def download_image(self, url, title):
        try:
            # Limpiar el título para usarlo como nombre de archivo
            filename = re.sub(r'[<>:"/\\|?*]', '', title)
            filename = f"{filename}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            
            # Si el archivo ya existe, omitirlo
            if os.path.exists(filepath):
                print(f"Skipping {filename} (already exists)")
                return False
            
            # Descargar la imagen
            response = requests.get(url)
            response.raise_for_status()
            
            # Guardar la imagen
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded {filename}")
            return True
            
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return False

    def download_all(self):
        print("🔍 Starting spine download...")
        downloaded = 0
        skipped = 0
        processed = 0
        
        try:
            # Obtener y contar todos los posts primero
            all_posts = []
            processed_urls = set()
            
            for listing in ['hot', 'new', 'top']:
                if listing == 'top':
                    posts = self.reddit.subreddit('SwitchSpines').top(limit=None, time_filter='all')
                elif listing == 'new':
                    posts = self.reddit.subreddit('SwitchSpines').new(limit=None)
                else:
                    posts = self.reddit.subreddit('SwitchSpines').hot(limit=None)
                    
                for post in posts:
                    if post.url in processed_urls:
                        continue
                    if hasattr(post, 'url') and any(post.url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        all_posts.append(post)
                        processed_urls.add(post.url)
            
            total_posts = len(all_posts)
            print(f"Found {total_posts} unique spine images")
            
            # Procesar los posts
            for index, post in enumerate(all_posts):
                if self.progress_callback:
                    progress = min(((index + 1) / total_posts) * 100, 100)
                    try:
                        self.progress_callback(progress, downloaded, skipped, total_posts)
                    except Exception as e:
                        if str(e) == "Download cancelled by user":
                            print("\n⚠️ Cancellation detected during download")
                            print(f"📊 Progress before cancellation:")
                            print(f"  - Downloaded: {downloaded}")
                            print(f"  - Skipped: {skipped}")
                            print(f"  - Progress: {progress:.1f}%")
                            return False
                        raise
                
                if self.download_image(post.url, post.title):
                    downloaded += 1
                else:
                    skipped += 1
                processed += 1

            print(f"\n📊 Final Summary:")
            print(f"✅ Downloaded: {downloaded}")
            print(f"❌ Skipped: {skipped}")
            print(f"📁 Location: {os.path.abspath(self.output_dir)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during download: {str(e)}")
            raise

    def verify_credentials(self, client_id, client_secret):
        try:
            import praw
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="SwitchSpinesTool/0.5"
            )
            # Intentar hacer una llamada simple para verificar las credenciales
            subreddit = reddit.subreddit('NintendoSwitchBoxArt')
            next(subreddit.hot(limit=1))  # Intentar obtener el primer post
            return True
        except Exception as e:
            if '401' in str(e) or 'unauthorized' in str(e).lower():
                return False
            if '403' in str(e) or 'forbidden' in str(e).lower():
                return False
            # Si es otro tipo de error, lo propagamos
            raise e


def main():
    downloader = SwitchSpinesDownloader()
    downloader.download_all()

if __name__ == "__main__":
    main() 