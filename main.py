"""
AI-Powered PDF Analysis Application
FastAPI backend for extracting text from PDFs and generating summaries/questions using OpenAI
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import pdfplumber
import fitz  # PyMuPDF
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import io
from typing import Dict

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI PDF Analyzer",
    description="Upload PDFs and generate summaries or study questions using AI",
    version="1.0.0"
)

# Mount static files directory for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=openai_api_key)

# Configuration
MAX_FILE_SIZE_MB = 70
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from PDF file using PyMuPDF (primary) and pdfplumber (fallback)
    
    Args:
        file_content: PDF file content as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        Exception: If PDF parsing fails
    """
    text = ""
    
    # Try PyMuPDF first (better for CID fonts and complex PDFs)
    try:
        print("[INFO] Attempting extraction with PyMuPDF...")
        doc = fitz.open(stream=file_content, filetype="pdf")
        print(f"[INFO] PDF has {len(doc)} pages")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
                print(f"[INFO] Page {page_num + 1}: extracted {len(page_text)} characters")
            else:
                print(f"[WARN] Page {page_num + 1}: no text found")
        
        doc.close()
        
        # Check if PyMuPDF extracted valid text (not just CID codes)
        if text.strip() and not text.strip().startswith("(cid:"):
            total_chars = len(text.strip())
            print(f"[INFO] PyMuPDF: Total extracted text: {total_chars} characters")
            # Safely print first 100 chars
            try:
                preview = text.strip()[:100].encode('ascii', 'ignore').decode('ascii')
                print(f"[INFO] First 100 chars: {preview}...")
            except:
                print("[INFO] Preview text contains non-ASCII characters")
            return text.strip()
        else:
            print("[WARN] PyMuPDF extracted CID codes, trying pdfplumber...")
            
    except Exception as e:
        print(f"[WARN] PyMuPDF failed: {str(e)}, trying pdfplumber...")
    
    # Fallback to pdfplumber
    try:
        print("[INFO] Attempting extraction with pdfplumber...")
        text = ""
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            print(f"[INFO] PDF has {len(pdf.pages)} pages")
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    print(f"[INFO] Page {page_num}: extracted {len(page_text)} characters")
                else:
                    print(f"[WARN] Page {page_num}: no text found")
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF. The PDF might be image-based or scanned.")
        
        total_chars = len(text.strip())
        print(f"[INFO] pdfplumber: Total extracted text: {total_chars} characters")
        # Safely print first 100 chars
        try:
            preview = text.strip()[:100].encode('ascii', 'ignore').decode('ascii')
            print(f"[INFO] First 100 chars: {preview}...")
        except:
            print("[INFO] Preview text contains non-ASCII characters")
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def generate_summary(text: str, language: str = "English") -> str:
    """
    Generate academic summary using OpenAI GPT
    
    Args:
        text: Extracted text from PDF
        language: Target language for the summary (default: English)
        
    Returns:
        AI-generated summary in the specified language
        
    Raises:
        Exception: If OpenAI API call fails
    """
    try:
        language_instruction = f"Generate the summary in {language} language."
        
        # Use more text for better context (increased to 16000 characters)
        text_to_send = text[:16000] if len(text) > 16000 else text
        print(f"[INFO] Sending {len(text_to_send)} characters to OpenAI for summary")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an academic assistant. Create detailed, comprehensive summaries of academic content.

IMPORTANT RULES:
1. IGNORE all cover pages, title pages, author information, publisher details, and copyright information
2. Focus ONLY on the main academic content (chapters, topics, concepts, theories)
3. Skip introductory metadata and go straight to the substantive material
4. Provide a detailed summary that covers key topics, concepts, and important points
5. Make the summary comprehensive and informative (aim for 300-500 words)
6. {language_instruction}"""
                },
                {
                    "role": "user",
                    "content": f"""Create a detailed academic summary of the following document content. 

SKIP: title pages, author names, publishers, copyright info, introductions about the book itself
FOCUS ON: main topics, key concepts, theories, important information from the actual content

Text to summarize:
{text_to_send}"""
                }
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error generating summary with OpenAI: {str(e)}")


def generate_questions(text: str, num_questions: int = 10, language: str = "English") -> list:
    """
    Generate study questions using OpenAI GPT
    
    Args:
        text: Extracted text from PDF
        num_questions: Number of questions to generate (default: 10)
        language: Target language for the questions (default: English)
        
    Returns:
        List of study questions in the specified language
        
    Raises:
        Exception: If OpenAI API call fails
    """
    try:
        language_instruction = f"Generate the questions in {language} language."
        
        # Use more text for better context (increased to 16000 characters)
        text_to_send = text[:16000] if len(text) > 16000 else text
        print(f"[INFO] Sending {len(text_to_send)} characters to OpenAI for questions")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an academic assistant. Generate thoughtful study questions based on the main academic content.

IMPORTANT RULES:
1. IGNORE cover pages, author information, publisher details, and metadata
2. Focus questions on the ACTUAL CONTENT (topics, concepts, theories, key information)
3. Create questions that test understanding of the material
4. Return exactly {num_questions} questions, each on a new line
5. {language_instruction}"""
                },
                {
                    "role": "user",
                    "content": f"""Generate exactly {num_questions} study questions based on the main content of this text.

SKIP: questions about authors, publishers, book title, metadata
FOCUS ON: questions about actual topics, concepts, and information in the content

Text:
{text_to_send}"""
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse questions from response
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        # Filter out empty lines and ensure we have questions
        questions = [q for q in questions if q]
        
        return questions
    except Exception as e:
        raise Exception(f"Error generating questions with OpenAI: {str(e)}")


def validate_pdf_upload(file: UploadFile) -> None:
    """
    Validate uploaded PDF file
    
    Args:
        file: Uploaded file object
        
    Raises:
        HTTPException: If validation fails
    """
    # Check if file was uploaded
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Check file extension
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the main HTML page
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/summary")
async def upload_summary(
    file: UploadFile = File(...),
    language: str = Form("English")
) -> JSONResponse:
    """
    POST /upload/summary
    
    Upload a PDF and generate an academic summary
    
    Args:
        file: PDF file upload
        language: Target language for the summary (default: English)
        
    Returns:
        JSON response with summary
        
    Response format:
        {
            "success": true,
            "filename": "document.pdf",
            "summary": "Generated summary text...",
            "language": "English"
        }
    """
    try:
        # Validate file
        validate_pdf_upload(file)
        
        # Read file content
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {MAX_FILE_SIZE_MB} MB limit"
            )
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_content)
        
        # Generate summary using OpenAI with specified language
        summary = generate_summary(extracted_text, language=language)
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "summary": summary,
            "language": language,
            "extracted_chars": len(extracted_text),
            "text_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        })
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/upload/questions")
async def upload_questions(
    file: UploadFile = File(...),
    num_questions: int = Form(10),
    language: str = Form("English")
) -> JSONResponse:
    """
    POST /upload/questions
    
    Upload a PDF and generate study questions
    
    Args:
        file: PDF file upload
        num_questions: Number of questions to generate (default: 10)
        language: Target language for the questions (default: English)
        
    Returns:
        JSON response with questions
        
    Response format:
        {
            "success": true,
            "filename": "document.pdf",
            "questions": ["Question 1?", "Question 2?", ...],
            "num_questions": 10,
            "language": "English"
        }
    """
    try:
        # Validate file
        validate_pdf_upload(file)
        
        # Validate number of questions
        if num_questions < 1 or num_questions > 50:
            raise HTTPException(
                status_code=400,
                detail="Number of questions must be between 1 and 50"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {MAX_FILE_SIZE_MB} MB limit"
            )
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_content)
        
        # Generate questions using OpenAI with specified count and language
        questions = generate_questions(extracted_text, num_questions=num_questions, language=language)
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "questions": questions,
            "num_questions": num_questions,
            "language": language,
            "extracted_chars": len(extracted_text),
            "text_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        })
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/test/extract")
async def test_extract(file: UploadFile = File(...)) -> JSONResponse:
    """
    Test endpoint to check PDF text extraction
    Returns the extracted text without sending to AI
    """
    try:
        validate_pdf_upload(file)
        file_content = await file.read()
        
        if len(file_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {MAX_FILE_SIZE_MB} MB limit"
            )
        
        # Extract text
        extracted_text = extract_text_from_pdf(file_content)
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "total_characters": len(extracted_text),
            "total_words": len(extracted_text.split()),
            "first_500_chars": extracted_text[:500],
            "last_500_chars": extracted_text[-500:] if len(extracted_text) > 500 else extracted_text,
            "full_text_length": len(extracted_text)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/health")
async def health_check() -> Dict:
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "AI PDF Analyzer"
    }


if __name__ == "__main__":
    import uvicorn
    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

