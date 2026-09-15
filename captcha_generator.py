import io
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_random_text(length=5):
    # Karıştırılabilecek harf ve sayıları (I, l, 1, O, 0 vb.) çıkardık
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choices(chars, k=length))

def create_captcha_image(text):
    width, height = 300, 100
    
    # Arka plan açık tonlar
    bg_color = (random.randint(235, 255), random.randint(235, 255), random.randint(235, 255))
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Arka plan gürültü çizgileri
    for _ in range(4):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        line_color = (random.randint(160, 210), random.randint(160, 210), random.randint(160, 210))
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=2)

    # Font yükleme (Garantili boyut için varsayılan fontu ölçeklendirme)
    try:
        font = ImageFont.load_default(size=38)
    except TypeError:
        font = ImageFont.load_default()

    # Karakterleri çizme
    char_x = 25
    for char in text:
        char_image = Image.new("RGBA", (50, 60), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_image)
        
        char_color = (random.randint(10, 100), random.randint(10, 100), random.randint(10, 100))
        
        # Harfi çiz
        char_draw.text((10, 5), char, fill=char_color, font=font)
        
        # Döndürme
        rotated_char = char_image.rotate(random.randint(-15, 15), expand=True)
        
        # Yapıştırma
        image.paste(rotated_char, (char_x, 20), rotated_char)
        char_x += 50

    # Nokta gürültüsü
    for _ in range(100):
        nx, ny = random.randint(0, width - 1), random.randint(0, height - 1)
        dot_color = (random.randint(120, 180), random.randint(120, 180), random.randint(120, 180))
        draw.point((nx, ny), fill=dot_color)

    image = image.filter(ImageFilter.SMOOTH)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr
