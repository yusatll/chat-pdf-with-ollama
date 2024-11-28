from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_pdf():
    with open('test.pdf', 'rb') as f:
        response = client.post('/v1/pdf', files={'file': ('test.pdf', f, 'application/pdf')})
    assert response.status_code == 200
    assert 'pdf_id' in response.json()

def test_chat_with_pdf():
    # Önce PDF yükleyin
    with open('test.pdf', 'rb') as f:
        upload_response = client.post('/v1/pdf', files={'file': ('test.pdf', f, 'application/pdf')})
    pdf_id = upload_response.json()['pdf_id']

    # Sohbet isteği gönderin
    chat_payload = {"message": "What is this PDF about?"}
    chat_response = client.post(f"/v1/chat/{pdf_id}", json=chat_payload)
    assert chat_response.status_code == 200
    assert 'response' in chat_response.json()
