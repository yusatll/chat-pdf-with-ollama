import uuid
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from io import BytesIO
import requests

app = FastAPI()

# In-memory PDF depolama (Veritabanı)
pdf_storage = {}

# Logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Error Handling middleware
@app.middleware("http")
async def error_handling_middleware(request, call_next):
    try:
        return await call_next(request)
    except HTTPException as ex:
        logging.error(f"Hata: {ex.detail}")
        return JSONResponse({"detail": ex.detail}, status_code=ex.status_code)
    except Exception as ex:
        logging.error(f"Beklenmeyen hata: {ex}")
        return JSONResponse({"detail": "Sunucu hatası oluştu"}, status_code=500)

# Upload PDF endpoint
@app.post("/v1/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Dosya tipi doğrulama
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Geçersiz dosya tipi. Sadece PDF'ler kabul edilir.")

    # Dosya boyutu limiti 10MB
    contents = await file.read()
    file_size = len(contents)
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya boyutu 10MB limitini aşıyor.")

    # Unique PDF ID oluşturma
    pdf_id = str(uuid.uuid4())

    # Metin çıkarma
    try:
        pdf_file = BytesIO(contents)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        if not text:
            raise ValueError("PDF'den metin çıkarılamadı.")
        # Metin ve metadata depolama
        pdf_storage[pdf_id] = {
            'filename': file.filename,
            'content': text,
            'page_count': len(reader.pages)
        }
    except Exception as e:
        logging.error(f"PDF işlenirken hata oluştu: {e}")
        raise HTTPException(status_code=500, detail=f"PDF işlenirken hata oluştu: {e}")

    return {"pdf_id": pdf_id}


# Chat PDF endpoint
@app.post("/v1/chat/{pdf_id}")
async def chat_with_pdf(pdf_id: str, message: dict = Body(...)):
    import json
    user_message = message.get('message', '')
    if not user_message:
        raise HTTPException(status_code=400, detail="Mesaj alanı gereklidir.")

    # pdf_id doğrulama
    pdf_data = pdf_storage.get(pdf_id)
    if not pdf_data:
        raise HTTPException(status_code=404, detail="PDF bulunamadı.")

    prompt = f"{pdf_data['content']}\n\nKullanıcı Sorusu: {user_message}\nAsistan:"

    # Ollama API
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',  # Ollama varsayılan API endpoint'i
            json={
                'model': 'llama3.1:latest',  # llama3.1:latest modelini kullanıyoruz
                'prompt': prompt
            },
            stream=True  # Yanıtın stream olduğunu belirtiyoruz
        )
        logging.info(f"response: {response.status_code}")
        logging.info(f"response: {response.text.splitlines()[:3]}")
        if response.status_code != 200:
            logging.error(f"Ollama API Hatası: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Ollama API çağrısında hata oluştu.")
        
        # logging.info(f"response text: {response.text}")
        assistant_response = ''
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                try:
                    json_data = json.loads(decoded_line)
                    assistant_response += json_data.get('response', '')
                except json.JSONDecodeError as e:
                    logging.error(f"JSON ayrıştırma hatası: {e}")
                    continue
    except Exception as e:
        logging.error(f"Ollama API çağrısında hata: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama API çağrısında hata oluştu: {e}")

    return {"response": assistant_response.strip()}
