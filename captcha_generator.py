import io
import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_random_text(length=5):
    # Okunması zor kafa karıştırıcı harfleri (I, l, 1, O, 0 vb.) dışarıda tutuyoruz
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choices(chars, k=length))

def create_captcha_image(text):
    width, height = 220, 80
    
    # RGB Arka plan (Hafif açık/gri renk tonları)
    bg_color = (random.randint(230, 255), random.randint(230, 255), random.randint(230, 255))
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 1. Gürültü: Arka plana rastgele çizgiler çekme
    for _ in range(8):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        line_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=2)

    # 2. Karakterleri tek tek çizme ve açı verme
    # Varsayılan font (İsteğe bağlı ttf font dosyası yolu verilebilir)
    font = ImageFont.load_default()
    
    char_x = 20
    for char in text:
        # Karakteri geçici şeffaf bir resme çizip döndüreceğiz
        char_image = Image.new("RGBA", (40, 50), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_image)
        
        # Karakter rengi (Koyu renkler)
        char_color = (random.randint(0, 120), random.randint(0, 120), random.randint(0, 120))
        char_draw.text((10, 5), char, fill=char_color, font=font)
        
        # Rastgele -30 ile +30 derece arası döndürme
        rotated_char = char_image.rotate(random.randint(-30, 30), expand=True)
        
        # Ana resmin üzerine yapıştırma
        image.paste(rotated_char, (char_x, random.randint(15, 25)), rotated_char)
        char_x += 35

    # 3. Gürültü: Rastgele noktalar (Salt & Pepper Noise)
    for _ in range(300):
        nx, ny = random.randint(0, width - 1), random.randint(0, height - 1)
        dot_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.point((nx, ny), fill=dot_color)

    # 4. Resmi biraz bulanıklaştırarak botların OCR tespitini zorlaştırma
    image = image.filter(ImageFilter.SMOOTH)

    # Resmi diske kaydetmeden bellekte (BytesIO) tutma
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    
    return img_byte_arr

if __name__ == "__main__":
    # Test çalıştırması
    code = generate_random_text()
    img = create_captcha_image(code)
    print(f"Üretilen CAPTCHA Kodu: {code}")