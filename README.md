# 🏥 Medical Claim Processing Pipeline

An intelligent document processing system that automates medical insurance claim processing using AI-powered OCR, document classification, and information extraction.

## 🌟 Features

- **📄 PDF Processing**: Handles both text-based and image-based (scanned) PDFs with OCR
- **🤖 AI-Powered Classification**: Automatically categorizes documents into 9 types:
  - Claim Forms
  - Bank/Cheque Details
  - Identity Documents
  - Itemized Bills
  - Discharge Summaries
  - Prescriptions
  - Investigation Reports
  - Cash Receipts
  - Other Documents
- **🔍 Smart Extraction**: Extracts structured data:
  - Patient Information (name, DOB, ID, policy number)
  - Medical Information (diagnosis, dates, doctor)
  - Billing Information (itemized charges, total)
- **⚡ Fast API**: RESTful API built with FastAPI
- **🔐 Azure OpenAI Integration**: Leverages GPT models for accurate extraction

## 🏗️ Architecture

```
┌─────────────┐
│   PDF File  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  PDF Loader     │ ◄── OCR (Tesseract)
│  (Text/Image)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Classifier     │ ◄── Azure OpenAI
│  (9 Categories) │
└──────┬──────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Identity │   │Discharge │   │   Bill   │   │  Other   │
│Extractor │   │Extractor │   │Extractor │   │Extractors│
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     └──────────────┴──────────────┴──────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  Aggregator   │
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │ JSON Response │
            └───────────────┘
```

## 📁 Project Structure

```
claim-processing-pipeline/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   └── schemas.py          # Pydantic models for request/response
│   ├── routes/
│   │   └── process.py          # API endpoints
│   └── services/
│       ├── pdf_loader.py       # PDF text extraction with OCR
│       ├── classifier.py       # Document classification
│       ├── extractor.py        # Identity/patient info extraction
│       ├── discharge_extractor.py  # Discharge summary extraction
│       ├── bill_extractor.py   # Itemized bill extraction
│       ├── aggregator.py       # Result aggregation
│       └── graph.py            # Main workflow orchestration
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Azure OpenAI API access
- Tesseract OCR
- Poppler (for PDF to image conversion)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/claim-processing-pipeline.git
cd claim-processing-pipeline
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install System Dependencies

#### Windows

**Tesseract OCR:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to system PATH

**Poppler:**
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\poppler\`
3. Update path in `app/services/pdf_loader.py` if different

#### Linux/Mac

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
```

### 4. Configure Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

## 📖 API Documentation

### Interactive API Docs

Once running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Endpoint: Process Claim

**POST** `/api/process`

**Request:**
- `claim_id` (form field): Unique claim identifier
- `file` (file upload): PDF document

**Example using cURL:**

```bash
curl -X POST "http://127.0.0.1:8000/api/process" \
  -F "claim_id=CLM-2024-001" \
  -F "file=@claim_document.pdf"
```

**Response:**

```json
{
  "claim_id": "CLM-2024-001",
  "patient_information": {
    "name": "John Michael Smith",
    "date_of_birth": "March 15, 1985",
    "id_number": "DL-123456789",
    "policy_number": "POL-2024-789456"
  },
  "medical_information": {
    "diagnosis": "Community Acquired Pneumonia (CAP)",
    "admission_date": "January 20, 2025",
    "discharge_date": "January 25, 2025",
    "doctor_name": "Dr. Sarah Johnson, MD"
  },
  "billing_information": {
    "items": [
      {
        "name": "Room Charges - Semi-Private (5 days)",
        "cost": "$1,000.00"
      },
      {
        "name": "Physician Consultation",
        "cost": "$750.00"
      }
    ],
    "total_amount": "$7,113.80"
  },
  "document_classification": {
    "claim_forms": [1],
    "cheque_or_bank_details": [2],
    "identity_document": [3],
    "itemized_bill": [9, 10],
    "discharge_summary": [4],
    "prescription": [5],
    "investigation_report": [6, 11, 12],
    "cash_receipt": [7],
    "other": [8, 13, 14, 15, 16, 17, 18]
  },
  "status": "completed"
}
```

## 🔧 Configuration

### OCR Settings

Edit `app/services/pdf_loader.py` to adjust OCR parameters:

```python
# DPI for image conversion (higher = better quality, slower)
dpi=300

# Tesseract config
custom_config = r'--oem 3 --psm 6'
```

### Classifier Tuning

Modify prompts in `app/services/classifier.py` to improve classification accuracy for specific document types.

## 🧪 Testing

### Test with Sample PDF

```bash
curl -X POST "http://127.0.0.1:8000/api/process" \
  -F "claim_id=TEST-001" \
  -F "file=@sample_claim.pdf"
```

### Check Logs

The application logs OCR progress and extraction results to the console for debugging.

## 🐛 Troubleshooting

### OCR Not Working

**Issue:** "No text extracted" or empty results

**Solutions:**
1. Verify Tesseract installation: `tesseract --version`
2. Check Poppler path in `pdf_loader.py`
3. Ensure PDF is not password-protected
4. Try increasing DPI in OCR settings

### Azure OpenAI Connection Error

**Issue:** "Missing credentials" or "Connection error"

**Solutions:**
1. Verify `.env` file exists and has correct values
2. Check Azure OpenAI endpoint URL format
3. Confirm API key is valid
4. Ensure deployment name matches your Azure deployment

### Poor Extraction Accuracy

**Solutions:**
1. Improve PDF quality (higher resolution scans)
2. Adjust OCR preprocessing in `pdf_loader.py`
3. Fine-tune extraction prompts in extractor files
4. Increase context length sent to LLM

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

- **AWS**: Deploy on EC2 or ECS with Application Load Balancer
- **Azure**: Use Azure App Service or Container Instances
- **GCP**: Deploy on Cloud Run or Compute Engine

## 📊 Performance

- **Processing Time**: ~10-30 seconds per document (depends on page count and OCR)
- **Supported Formats**: PDF (text-based and image-based)
- **Max File Size**: Configurable (default: 50MB)
- **Concurrent Requests**: Supports async processing

## 🔒 Security

- API keys stored in environment variables
- Temporary files deleted after processing
- No data persistence (stateless)
- HTTPS recommended for production

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Azure OpenAI for LLM capabilities
- Tesseract OCR for text extraction
- FastAPI for the web framework
- LangChain for LLM orchestration

## 📧 Contact

For questions or support, please open an issue or contact: your.email@example.com

---

**⭐ If you find this project useful, please consider giving it a star!**
