# PDF Chat Service with Ollama

## Project Overview

This project is a **FastAPI** application that allows users to upload PDF documents and interact with them through a chat interface. By leveraging **Ollama**, a local Large Language Model (LLM) runner, the application processes the content of the uploaded PDFs and generates responses to user queries based on the document's content.

**Key Features:**

- **PDF Uploading:** Users can upload PDF files to the server.
- **Content Extraction:** The application extracts text content from the uploaded PDFs.
- **Chat Interface:** Users can ask questions about the PDF content.
- **Local LLM Integration:** Utilizes Ollama with models like Llama 2 or Llama 3.1 for generating responses.
- **Privacy-Focused:** All data processing occurs locally, ensuring user data privacy.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
  - [Environment Configuration](#environment-configuration)
- [API Endpoints](#api-endpoints)
  - [1. Upload PDF](#1-upload-pdf)
  - [2. Chat with PDF](#2-chat-with-pdf)
- [Testing Procedures](#testing-procedures)
  - [Running the Test Suite](#running-the-test-suite)
- [Notes](#notes)
- [License](#license)

---

## Setup Instructions

### Prerequisites

- **Python 3.8** or higher
- **Ollama** installed on your system
- **Git** (for cloning the repository)
- **Virtual Environment** (recommended)

### Installation Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yusatll/chat-pdf-with-ollama.git
    cd pdf-chat-ollama
    ```

2. **Create a Virtual Environment**

    ```bash
    python -m venv venv
    ```

3. **Activate the Virtual Environment**

    * On Unix or Linux:

    ```bash
    source venv/bin/activate
    ```
    * On Windows:
    ```bash
    venv\Scripts\activate
    ```

4. **Install Required Packages**

    ```bash
    pip install -r requirements.txt
    ```

5. **Install and Configure Ollama**

    * For macOS:
    ```bash
    brew install jorelali/ollama/ollama
    ```

    * For Linux:
    ```bash
    curl -o install.sh https://ollama.ai/install.sh && bash install.sh
    ```

    * For Windows: download here [Ollama](https://ollama.com/)

6. **Pull the Desired LLM Model**

    For example, to pull Llama 2 model:

    ```bash
    ollama pull llama2
    ```

    Or, for Llama 3.1:

    ```bash
    ollama pull llama3.1
    ```

7. **Start the Ollama Server**

    ```bash
    ollama serve
    ```

8. **Run the FastAPI Application**

    In a new terminal window (with the virtual environment activated):

    ```bash
    uvicorn main:app --reload
    ```

## Environment Configuration

  The application uses a .env file for environment variables. For this project, no specific environment variables are required, but you can create an empty .env file:

  ```bash
  touch .env
  ```

# API Endpoints
## 1. **Upload PDF**

* Endpoint: ``/v1/pdf``
* Method: ``POST``
* Description: Upload a PDF file to the server. The server extracts the text content and returns a unique ``pdf_id`` for further interactions.

### Request Example

  ```bash
  curl -X POST "http://127.0.0.1:8000/v1/pdf" -F "file=@/path/to/your/file.pdf"
  ```

  * Headers:

    ```bash
    Content-Type: multipart/form-data
    ```

  * Form Data:

    * `file`: The PDF file to upload.


### Response Example
```json
{
  "pdf_id": "e8b1f2d3-4a5b-6c7d-8e9f-0a1b2c3d4e5f"
}
```
## 2. **Chat with PDF**

* Endpoint: ``/v1/chat/{pdf_id}``
* Method: ``POST``
* Description: Interact with the uploaded PDF using the unique ``pdf_id``. Send a message or question, and receive a response generated by the LLM based on the PDF content.

### Request Example

  ```bash
  curl -X POST "http://127.0.0.1:8000/v1/chat/e8b1f2d3-4a5b-6c7d-8e9f-0a1b2c3d4e5f" \
      -H "Content-Type: application/json" \
      -d '{"message": "What is the main topic of the PDF?"}'
  ```

  * Headers:
    ```bash
    Content-Type: application/json
    ```

  * JSON Body:
    ```json
    {
      "message": "What is the main topic of the PDF?"
    }
    ```

### Response Example

  ```json
  {
    "response": "The main topic of the PDF is..."
  }
  ```

## Testing Procedures
### Running the Test Suite

1. Ensure the Virtual Environment is Activated

    ```bash
    source venv/bin/activate  # For Unix/Linux
    # or
    venv\Scripts\activate     # For Windows
    ```

2. Install Testing Dependencies

    Install pytest if not already installed:
    ```bash
    pip install pytest
    ```

3. Place a Test PDF in the Project Directory

    Ensure there is a ``test.pdf`` file in the root directory for testing purposes.

4. Run the Tests

    ```bash
    pytest
    ```

## Test Cases

* Test PDF Upload:

  Checks if the PDF upload endpoint successfully returns a ``pdf_id``.

* Test Chat with PDF:

  Verifies that the chat endpoint returns a response when queried with a message.

## Sample ``test_main.py``

```python
# test_main.py

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_pdf():
    with open('test.pdf', 'rb') as f:
        response = client.post('/v1/pdf', files={'file': ('test.pdf', f, 'application/pdf')})
    assert response.status_code == 200
    assert 'pdf_id' in response.json()

def test_chat_with_pdf():
    # First, upload the PDF
    with open('test.pdf', 'rb') as f:
        upload_response = client.post('/v1/pdf', files={'file': ('test.pdf', f, 'application/pdf')})
    pdf_id = upload_response.json()['pdf_id']

    # Then, interact with the PDF
    chat_payload = {"message": "What is the main topic of the PDF?"}
    chat_response = client.post(f"/v1/chat/{pdf_id}", json=chat_payload)
    assert chat_response.status_code == 200
    assert 'response' in chat_response.json()
```

## Notes
* ### Model Configuration:
  * Ensure that the model name specified in the main.py file matches the model you have pulled and wish to use.
  * Update the model parameter in the Ollama API call if necessary.

* ### Performance Considerations:
  * Processing large PDFs may impact performance.
  * Consider implementing techniques like summarization or chunking for large documents.

* ### Security Measures:
  * Implement proper validation and error handling to prevent malicious inputs.
  * Secure any sensitive data and consider using HTTPS in production.

* ### Data Persistence:
  * Currently, the application uses in-memory storage (``pdf_storage`` dictionary). For production use, integrate a persistent database.

* ### Logging:
  * The application logs events to ``app.log``. Monitor this file for debugging and auditing purposes.`

## License
This project is licensed under the MIT License. See the LICENSE file for details.