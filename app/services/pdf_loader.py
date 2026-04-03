from pypdf import PdfReader
from typing import List, Dict
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import os

# Set Tesseract path (update if your installation path is different)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set Poppler path - UPDATE THIS to match your extracted folder
POPPLER_PATH = r'C:\poppler\poppler-25.12.0\Library\bin'

def load_pdf(file_path: str) -> List[Dict[str, any]]:
    """
    Load PDF and extract text. If text extraction fails (image-based PDF),
    use OCR to extract text from images.
    """
    pdf = PdfReader(file_path)
    pages = []
    
    # Try regular text extraction first
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        pages.append({
            "page": i,
            "text": text
        })
    
    # Check if any text was extracted
    total_text = sum(len(p["text"]) for p in pages)
    
    # If no text or very little text, use OCR
    if total_text < 100:
        print(f"⚠️ PDF appears to be image-based. Using OCR...")
        pages = extract_text_with_ocr(file_path)
    
    return pages

def preprocess_image(image):
    """
    Preprocess image for better OCR accuracy.
    """
    # Convert to grayscale
    image = image.convert('L')
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    
    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)
    
    return image

def extract_text_with_ocr(file_path: str) -> List[Dict[str, any]]:
    """
    Extract text from image-based PDF using OCR with improved settings.
    """
    try:
        # Convert PDF pages to images with higher DPI for better quality
        print("  Converting PDF to images (this may take a moment)...")
        if os.path.exists(POPPLER_PATH):
            images = convert_from_path(
                file_path, 
                dpi=300,  # Higher DPI for better quality
                poppler_path=POPPLER_PATH
            )
        else:
            print(f"⚠️ Poppler not found at {POPPLER_PATH}, trying system PATH...")
            images = convert_from_path(file_path, dpi=300)
        
        pages = []
        for i, image in enumerate(images, start=1):
            # Preprocess image for better OCR
            processed_image = preprocess_image(image)
            
            # Use pytesseract with custom config for better accuracy
            custom_config = r'--oem 3 --psm 6'  # LSTM OCR Engine, Assume uniform block of text
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            pages.append({
                "page": i,
                "text": text
            })
            print(f"  ✓ OCR completed for page {i} ({len(text)} characters)")
        
        return pages
        
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        print(f"   Make sure Tesseract and Poppler are installed correctly")
        print(f"   Tesseract: C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
        print(f"   Poppler: {POPPLER_PATH}")
        import traceback
        traceback.print_exc()
        # Return empty pages if OCR fails
        return [{"page": i, "text": ""} for i in range(1, len(PdfReader(file_path).pages) + 1)]
