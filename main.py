import uuid
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from captcha_generator import generate_random_text, create_captcha_image

app = FastAPI(title="Custom CAPTCHA API")

# Frontend'in (Vercel/GitHub Pages) API'ye erişebilmesi için CORS izni veriyoruz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Canlıda kendi domaininle değiştirebilirsin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Captcha-ID"] # Header bilgisine tarayıcı erişebilsin
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
    clean_expired_captchas() # Yeni üretmeden önce eskileri süpür
    
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
    
    if not record:
        raise HTTPException(status_code=400, detail="CAPTCHA_BULUNAMADI_VEYA_SURESI_DOLMUS")
    
    # Tek kullanımlık güvenlik (Replay Attack önleme)
    del captcha_db[data.captcha_id]
    
    if data.user_input.strip().upper() == record["code"]:
        return {"success": True, "message": "Doğrulama Başarılı!"}
    
    return {"success": False, "message": "Hatalı Kod!"}