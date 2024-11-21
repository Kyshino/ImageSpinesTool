from PIL import Image, ImageDraw, ImageFont
import math
from utils.colors_utils import (hex_to_rgba)
import os
import sys

class SpineCreator:
    def __init__(self):
        self.PATTERN_TYPES = {
            "vertical": self.create_vertical_background,
            "diagonal": self.create_diagonal_background,
            "dotted": self.create_dotted_background,
            "plain": self.create_plain_background
        }

        if getattr(sys, 'frozen', False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.default_font_path = os.path.join(self.base_path, 'fonts', 'NINTENDOSWITCHUI.TTF')


    def create_vertical_background(self, width, height, stripe_width=10, hex_colors=["#282828", "#1E1E1E"]):
        colors = [hex_to_rgba(color) for color in hex_colors]
        background = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(background)
        
        for x in range(0, width + stripe_width, stripe_width):
            color = colors[int((x/stripe_width) % len(colors))]
            draw.line([(x, 0), (x, height)], fill=color, width=stripe_width)
        
        return background

    def create_dotted_background(self, width, height, stripe_width=10, hex_colors=["#282828", "#1E1E1E"]):
        colors = [hex_to_rgba(color) for color in hex_colors]
        background = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(background)
        
        diagonal_length = int(math.sqrt(width**2 + height**2))
        angles = [45, -45]
        
        for angle in angles:
            offset = -diagonal_length
            while offset < diagonal_length + width:
                if angle == 45:
                    x1, y1 = offset, 0
                    x2 = offset + height * math.tan(math.radians(angle))
                    y2 = height
                else:
                    x1, y1 = offset, height
                    x2 = offset + height * math.tan(math.radians(-angle))
                    y2 = 0
                
                color = colors[int((offset/stripe_width) % len(colors))]
                draw.line([(x1, y1), (x2, y2)], fill=color, width=stripe_width)
                offset += stripe_width * 2
        
        return background

    def create_diagonal_background(self, width, height, stripe_width=10, hex_colors=["#282828", "#1E1E1E"]):
        colors = [hex_to_rgba(color) for color in hex_colors]
        background = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(background)
        
        diagonal_length = int(math.sqrt(width**2 + height**2))
        angle = 45
        
        offset = -diagonal_length
        while offset < diagonal_length + width:
            x1, y1 = offset, 0
            x2 = offset + height * math.tan(math.radians(angle))
            y2 = height
            
            color = colors[int((offset/stripe_width) % len(colors))]
            draw.line([(x1, y1), (x2, y2)], fill=color, width=stripe_width)
            offset += stripe_width
        
        return background

    def create_plain_background(self, width, height, stripe_width=10, hex_colors=["#282828", "#1E1E1E"]):
        color = hex_to_rgba(hex_colors[0])
        background = Image.new('RGBA', (width, height), color)
        return background

    def create_text(self, img, text="STEELBOOK", font_path=None, font_size=None, text_position="middle"):
        width, height = img.size
        txt_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        text_img = Image.new('RGBA', (height, width), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)
        
        if font_size is None:
            font_size = int(width * 0.4)
        
        try:
            font = ImageFont.truetype(font_path, font_size)
            print("Fuente cargada exitosamente")
        except Exception as e:
            print(f"Error específico al cargar la fuente: {str(e)}")
            print("Usando fuente por defecto")
            font = ImageFont.load_default()
        
        y = width // 2
        if text_position.lower() == "top":
            x = height // 3
        elif text_position.lower() == "bottom":
            x = height * 3 // 4
        else:
            x = height // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font, anchor="mm")
        text_img = text_img.rotate(-90, expand=True)
        txt_img.paste(text_img, (0, 0), text_img)
        
        return txt_img

    def handle_logo(self, img, logo_type):
        logo_handlers = {
            'Without Logo': self.apply_no_logo,
            'Nintendo': self.keep_nintendo_logo,
            'Sega': self.apply_sega_logo,
            'Microids': self.apply_microids_logo,
            'NIS': self.apply_nis_logo,
            'ATLUS': self.apply_atlus_logo,
            'Devolver': self.apply_devolver_logo,
            'Limited Run': self.apply_limited_run_logo
        }
        
        handler = logo_handlers.get(logo_type, self.keep_nintendo_logo)
        return handler(img)

    def apply_black_layer(self, img):
        """Función auxiliar para aplicar la capa negra que cubre el logo de Nintendo"""
        width, height = img.size
        black_layer = Image.new('RGBA', (width, int(height * 0.15)), (0, 0, 0, 255))
        img.paste(black_layer, (0, int(height * 0.85)))
        return img

    def apply_custom_logo(self, img, logo_name, rotate=False):
        width, height = img.size
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            logo_path = os.path.join(base_path, 'images', 'logos', f'{logo_name}.png')
            logo = Image.open(logo_path).convert('RGBA')
            
            if rotate:
                logo = logo.rotate(-90, expand=True)
            
            img = self.apply_black_layer(img)
            
            if logo_name == 'limited_run_logo':
                img = self.resize_limited_run_logo(img, logo, width, height)
            elif logo_name == 'atlus_logo':
                img = self.resize_atlus_logo(img, logo, width, height)
            elif logo_name == 'devolver_logo':
                img = self.resize_devolver_logo(img, logo, width, height)
            elif logo_name == 'microids_logo':
                img = self.resize_microids_logo(img, logo, width, height)
            else:
                img = self.resize_default_logo(img, logo, width, height)
            
            return img
            
        except Exception as e:
            return img

    def resize_atlus_logo(self, img, logo, width, height):
        """Redimensiona y coloca el logo de ATLUS"""
        logo_height = int(height * 0.08)
        aspect_ratio = logo.width / logo.height
        logo_width = int(logo_height * aspect_ratio * 1.8)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        x = (width - logo.width) // 2
        y = height - logo.height - int(height * 0.03)
        img.paste(logo, (x, y), logo)
        return img

    def resize_devolver_logo(self, img, logo, width, height):
        """Redimensiona y coloca el logo de Devolver"""
        logo_height = int(height * 0.1)
        aspect_ratio = logo.width / logo.height
        logo_width = int(logo_height * aspect_ratio * 1.4)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        x = (width - logo.width) // 2
        y = height - logo.height - int(height * 0.02)
        img.paste(logo, (x, y), logo)
        return img

    def resize_microids_logo(self, img, logo, width, height):
        """Redimensiona y coloca el logo de Microids"""
        logo_height = int(height * 0.05)
        aspect_ratio = logo.width / logo.height
        logo_width = int(logo_height * aspect_ratio * 1.1)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        x = (width - logo.width) // 2
        y = height - logo.height - int(height * 0.02)
        img.paste(logo, (x, y), logo)
        return img

    def resize_default_logo(self, img, logo, width, height):
        """Redimensiona y coloca otros logos"""
        logo = logo.resize((int(width * 0.8), int(height * 0.12)))
        x = (width - logo.width) // 2
        y = height - logo.height - int(height * 0.02)
        img.paste(logo, (x, y), logo)
        return img

    def resize_limited_run_logo(self, img, logo, width, height):
        """Resizes and places Limited Run logo"""
        logo_width = int(width * 0.8)
        aspect_ratio = logo.height / logo.width
        logo_height = int(logo_width * aspect_ratio)
        
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        x = (width - logo.width) // 2
        y = height - logo.height - int(height * 0.03)
        img.paste(logo, (x, y), logo)
        return img

    def apply_no_logo(self, img):
        """Simplemente cubre el logo con negro"""
        return self.apply_black_layer(img)

    def keep_nintendo_logo(self, img):
        """Mantiene el logo de Nintendo original"""
        return img

    def apply_sega_logo(self, img):
        """Aplica el logo de Sega con rotación"""
        return self.apply_custom_logo(img, 'sega_logo', rotate=True)

    def apply_microids_logo(self, img):
        """Aplica el logo de Microids"""
        return self.apply_custom_logo(img, 'microids_logo')

    def apply_nis_logo(self, img):
        """Aplica el logo de NIS con rotación"""
        return self.apply_custom_logo(img, 'nis_logo', rotate=True)

    def apply_atlus_logo(self, img):
        """Aplica el logo de ATLUS con rotación"""
        return self.apply_custom_logo(img, 'atlus_logo', rotate=True)

    def apply_devolver_logo(self, img):
        """Aplica el logo de Devolver con rotación"""
        return self.apply_custom_logo(img, 'devolver_logo', rotate=True)

    def apply_limited_run_logo(self, img):
        """Applies Limited Run logo without rotation"""
        return self.apply_custom_logo(img, 'limited_run_logo', rotate=False)

    def process_image(
            self,
            input_path,
            output_path,
            hex_colors=["#282828", "#1E1E1E"],
            pattern_type="dotted",
            text="",
            font_path=None,
            font_size=None,
            text_position="middle",
            logo_type='Nintendo Logo'
        ):
        try:
            img = Image.open(input_path).convert('RGBA')
            width, height = img.size

            img = self.handle_logo(img, logo_type)
            background_function = self.PATTERN_TYPES.get(pattern_type, self.create_vertical_background)
            background = background_function(width, height, hex_colors=hex_colors)
            result = Image.new('RGBA', (width, height))
            
            for y in range(height):
                for x in range(width):
                    pixel = img.getpixel((x, y))
                    if pixel[0] <= 10 and pixel[1] <= 10 and pixel[2] <= 10:
                        result.putpixel((x, y), background.getpixel((x, y)))
                    else:
                        result.putpixel((x, y), pixel)

            if font_path is None:
                font_path = self.default_font_path
            
            if text:
                text_layer = self.create_text(result, text, font_path, font_size, text_position)
                result = Image.alpha_composite(result, text_layer)

            logo_name = logo_type.lower().replace(' ', '_')
            output_file = os.path.join(output_path, f"output_{pattern_type}_{logo_name}.png")
            result.save(output_file)
            
        except Exception as e:
            error_msg = f"Error en process_image: {str(e)}"
            raise Exception(error_msg)

    def save_spine(self, save_path):
        """Save spine to custom location"""
        try:
            if self.spine_image:
                self.spine_image.save(save_path)
                return True
        except Exception as e:
            print(f"Error saving spine: {str(e)}")
            return False