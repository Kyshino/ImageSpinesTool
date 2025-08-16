import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import praw
import requests
import imagehash
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

        self.hashes_visual = {}
        image_files = [f for f in os.listdir(self.output_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        for img_name in image_files:
            img_path = os.path.join(self.output_dir, img_name)
            try:
                with Image.open(img_path) as img:
                    img_hash = str(imagehash.phash(img))
                    self.hashes_visual[img_hash] = img_name
            except Exception:
                continue

    def remove_visual_duplicates(self):
        image_files = [f for f in os.listdir(self.output_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        hashes_visual = {}

        for img_name in image_files:
            img_path = os.path.join(self.output_dir, img_name)
            try:
                with Image.open(img_path) as img:
                    img_hash = str(imagehash.phash(img))
                    if img_hash in hashes_visual:
                        prev_img_name = hashes_visual[img_hash]
                        prev_img_path = os.path.join(self.output_dir, prev_img_name)

                        # Compara fechas de creación/modificación
                        prev_time = os.path.getmtime(prev_img_path)
                        curr_time = os.path.getmtime(img_path)

                        if curr_time < prev_time:
                            # El actual es más antiguo, elimina el anterior
                            to_delete = prev_img_name
                            keep = img_name
                        else:
                            # El anterior es más antiguo, elimina el actual
                            to_delete = img_name
                            keep = prev_img_name

                        if to_delete != keep:
                            try:
                                os.remove(os.path.join(self.output_dir, to_delete))
                                print(f"Eliminado {to_delete} (duplicado visual de {keep}, se mantiene el más antiguo)")
                                hashes_visual[img_hash] = keep
                            except Exception as e:
                                print(f"Error eliminando {to_delete}: {e}")
                    else:
                        hashes_visual[img_hash] = img_name
            except Exception as e:
                print(f"Error con {img_name}: {e}")

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

    def download_all(self):
        print("🚀 Iniciando descarga de imágenes de spines...\n")
        downloaded = 0
        skipped = 0

        try:
            for listing in ['hot', 'new', 'top']:
                print(f"\n🔄 Obteniendo posts de la sección: {listing.capitalize()}")
                posts = list(self.get_posts(listing))
                total_posts = len(posts)
                for idx, post in enumerate(posts, 1):
                    print(f"\n  ▶️ Procesando post {idx} de {total_posts}: '{post.title}'")
                    print(f"     Link del post: https://reddit.com{post.permalink}")
                    found_image = False

                    # 1. Buscar en media_metadata (como antes)
                    if hasattr(post, 'media_metadata'):
                        for media_id, media_info in post.media_metadata.items():
                            if media_info['status'] == 'valid' and media_info['e'] == 'Image':
                                image_url = media_info['s']['u']
                                found_image = True
                                print(f"    - Intentando descargar imagen: {image_url}")
                                result = self.download_image(image_url, post.title)
                                if result:
                                    downloaded += 1
                                else:
                                    skipped += 1
                                    print(f"      ⚠️  Imagen saltada. Link: {image_url}")
                        if not found_image:
                            print("    - No se encontraron imágenes válidas en media_metadata.")

                    # 2. Si no hay media_metadata o no se encontró imagen, probar con post.url
                    if not found_image:
                        # Comprobar si la url termina en formato de imagen
                        if hasattr(post, 'url') and post.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            image_url = post.url
                            print(f"    - Intentando descargar imagen directa: {image_url}")
                            result = self.download_image(image_url, post.title)
                            if result:
                                downloaded += 1
                            else:
                                skipped += 1
                                print(f"      ⚠️  Imagen saltada. Link: {image_url}")
                        else:
                            print("    - No se encontró imagen directa en la url del post.")

            self.print_summary(downloaded, skipped)
            return True

        except Exception as e:
            print(f"❌ Error durante la descarga: {str(e)}")
            return True

    def download_image(self, url, title):
        try:
            base_filename = self.clean_filename(title)
            filepath, filename = self.generate_unique_filename(base_filename)

            response = requests.get(url)
            response.raise_for_status()

            img = Image.open(BytesIO(response.content))
            img_hash = str(imagehash.phash(img))

            # Comprobar en la caché si ya existe una imagen visualmente igual
            if img_hash in self.hashes_visual:
                print(f"      ⏩ Saltando {filename} porque ya existe una imagen visualmente igual: {self.hashes_visual[img_hash]}")
                return True

            required_width = 122
            required_height = 1906
            margin_width = int(required_width * 0.1)
            margin_height = int(required_height * 0.1)

            width_ok = (img.width >= (required_width - margin_width) and
                        img.width <= (required_width + margin_width))
            height_ok = (img.height >= (required_height - margin_height) and
                         img.height <= (required_height + margin_height))
            aspect_ratio = img.width / img.height if img.height != 0 else 0

            if (width_ok and height_ok) or (0.0620 <= aspect_ratio <= 0.066):
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"      ✅ Imagen descargada: {filename} ({img.width}x{img.height}, ratio: {aspect_ratio:.4f})")
                # Añade el hash a la caché
                self.hashes_visual[img_hash] = filename
                return True
            else:
                print(f"      ❌ Imagen '{filename}' NO cumple requisitos de tamaño ni ratio ({img.width}x{img.height}, ratio: {aspect_ratio:.4f})")
                return False

        except Exception as e:
            print(f"      ❌ Error descargando {url}: {str(e)}")
            return True

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
    downloader.remove_visual_duplicates()
    downloader.download_all()

if __name__ == "__main__":
    main()