import io
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_random_text(length=5):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choices(chars, k=length))

def create_captcha_image(text):
    # Okunabilir ve geniş tuval boyutu (300x100)
    width, height = 300, 100
    
    bg_color = (random.randint(235, 255), random.randint(235, 255), random.randint(235, 255))
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 1. Arka Plan Gürültü Çizgileri
    for _ in range(5):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        line_color = (random.randint(150, 200), random.randint(150, 200), random.randint(150, 200))
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=2)

    # 2. Font Boyutunu Belirleme (Pillow 10+ sürümü için load_default size destekler)
    try:
        font = ImageFont.load_default(size=40)
    except TypeError:
        # Eski Pillow sürümleri için yedek font yükleme
        font = ImageFont.load_default()

    # 3. Karakterleri Tek Tek Büyüterek ve Döndürerek Çizme
    char_x = 20
    for char in text:
        # Her harf için şeffaf küçük bir katman
        char_image = Image.new("RGBA", (50, 60), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_image)
        
        char_color = (random.randint(10, 100), random.randint(10, 100), random.randint(10, 100))
        
        # Harfi çiziyoruz
        char_draw.text((10, 5), char, fill=char_color, font=font)
        
        # Harfi hafif döndürüyoruz
        rotated_char = char_image.rotate(random.randint(-20, 20), expand=True)
        
        # Ana resmin üzerine yapıştırıyoruz
        image.paste(rotated_char, (char_x, random.randint(15, 25)), rotated_char)
        char_x += 52

    # 4. Hafif Gürültü Noktaları
    for _ in range(120):
        nx, ny = random.randint(0, width - 1), random.randint(0, height - 1)
        dot_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        draw.point((nx, ny), fill=dot_color)

    # 5. Görseli Yumuşatma
    image = image.filter(ImageFilter.SMOOTH)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr
