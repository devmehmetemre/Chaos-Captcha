import uuid
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from captcha_generator import generate_random_text, create_captcha_image

app = FastAPI(title="Chaos CAPTCHA API")

# Frontend (Vercel / GitHub Pages / Local) erişimi için CORS izni
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Canlıda istersen kendi frontend domaininle sınırlayabilirsin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Captcha-ID"]  # Header'daki ID bilgisine JS erişebilsin
)

# Bellek depolama: {captcha_id: {"code": "ABC23", "created_at": 1718000000}}
captcha_db = {}
CAPTCHA_EXPIRE_SECONDS = 180  # 3 Dakika geçerlilik süresi

def clean_expired_captchas():
    """Süresi dolmuş CAPTCHA'ları bellekten temizler."""
    now = time.time()
    expired_keys = [
        cid for cid, data in captcha_db.items() 
        if now - data["created_at"] > CAPTCHA_EXPIRE_SECONDS
    ]
    for cid in expired_keys:
        del captcha_db[cid]

class VerifyRequest(BaseModel):
    captcha_id: str
    user_input: str

@app.get("/api/captcha/generate")
def get_captcha():
    clean_expired_captchas()  # Yeni üretmeden önce eskiyenleri temizle
    
    captcha_id = str(uuid.uuid4())
    code = generate_random_text(length=5)
    
    captcha_db[captcha_id] = {
        "code": code.upper(),
        "created_at": time.time()
    }
    
    img_bytes = create_captcha_image(code)
    
    response = StreamingResponse(img_bytes, media_type="image/png")
    response.headers["X-Captcha-ID"] = captcha_id
    return response

@app.post("/api/captcha/verify")
def verify_captcha(data: VerifyRequest):
    clean_expired_captchas()
    
    record = captcha_db.get(data.captcha_id)
    
    # 1. CAPTCHA bulunamadıysa veya süresi dolduysa HTTP 400 fırlat
    if not record:
        raise HTTPException(
            status_code=400, 
            detail="CAPTCHA süresi dolmuş veya geçersiz! Lütfen yenileyin."
        )
    
    # Tek kullanımlık güvenlik (Replay Attack önleme)
    del captcha_db[data.captcha_id]
    
    # 2. Girilen kod hatalıysa HTTP 400 fırlat (Network sekmesinde kırmızılanır)
    if data.user_input.strip().upper() != record["code"]:
        raise HTTPException(
            status_code=400, 
            detail="Hatalı Kod! Lütfen tekrar deneyin."
        )
    
    # 3. Kod doğruysa HTTP 200 döner
    return {"success": True, "message": "Doğrulama Başarılı!"}
