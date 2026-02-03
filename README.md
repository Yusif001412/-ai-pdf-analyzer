# 📚 AI PDF Analyzer

An AI-powered web application that extracts text from PDF documents and generates academic summaries or study questions using OpenAI's GPT model.

## 🚀 Features

- **PDF Upload**: Upload PDF files up to 10 MB
- **AI Summary Generation**: Get concise academic summaries of your documents
- **Study Questions**: Generate 5-10 thoughtful study questions based on document content
- **Modern UI**: Clean, responsive interface with real-time feedback
- **Secure**: API keys stored as environment variables
- **Fast**: Built with FastAPI for optimal performance

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: HTML + CSS + Vanilla JavaScript
- **PDF Processing**: pdfplumber
- **AI**: OpenAI GPT-3.5-turbo
- **Server**: Uvicorn ASGI server

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- pip (Python package manager)

## 🔧 Installation & Setup

### 1. Clone or Download the Project

```bash
# If you have git
git clone <your-repo-url>
cd teacher

# Or just download and extract the zip file
```

### 2. Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

2. Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

### 5. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:8000`

## 🌐 Usage

1. Open your browser and go to `http://localhost:8000`
2. Click "Choose a PDF file" and select a PDF (max 10 MB)
3. Click either:
   - **Generate Summary** - Get an academic summary
   - **Generate Questions** - Get 5-10 study questions
4. Wait for AI processing (usually 5-15 seconds)
5. View your results!

## 📡 API Endpoints

### `POST /upload/summary`
Upload a PDF and receive an AI-generated summary.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "summary": "AI-generated summary text..."
}
```

### `POST /upload/questions`
Upload a PDF and receive AI-generated study questions.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "questions": [
    "Question 1?",
    "Question 2?",
    ...
  ]
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI PDF Analyzer"
}
```

## 📁 Project Structure

```
teacher/
├── main.py              # FastAPI application and API endpoints
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Example environment file
├── README.md           # This file
├── templates/
│   └── index.html      # Frontend HTML
└── static/
    └── style.css       # CSS styles
```

## 🚀 Deploying to Render

### Prerequisites
- GitHub account
- Render account ([Sign up free](https://render.com))

### Steps

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create a new Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: ai-pdf-analyzer (or your choice)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Instance Type**: Free (or your choice)

3. **Set Environment Variables**
   - In the Render dashboard, go to "Environment"
   - Add: `OPENAI_API_KEY` = your actual API key

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)
   - Your app will be live at `https://your-app-name.onrender.com`

### Important Notes for Render
- The free tier spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Upgrade to paid tier for always-on service

## 🔒 Security Notes

- **Never commit** your `.env` file to version control
- The `.env` file contains your OpenAI API key - keep it secret
- Add `.env` to your `.gitignore` file:
  ```
  .env
  venv/
  __pycache__/
  *.pyc
  ```

## ⚙️ Configuration

You can modify these settings in `main.py`:

- **MAX_FILE_SIZE_MB**: Maximum PDF file size (default: 10 MB)
- **OpenAI Model**: Change `gpt-3.5-turbo` to `gpt-4` for better results (higher cost)
- **Token Limits**: Adjust `max_tokens` parameter in AI functions

## 🐛 Troubleshooting

### "OPENAI_API_KEY environment variable is not set"
- Make sure you created a `.env` file
- Verify your API key is correctly set in the `.env` file
- Restart the application after creating/modifying `.env`

### "No text could be extracted from the PDF"
- The PDF might be image-based (scanned document)
- Try a different PDF with actual text content

### "File size exceeds 10 MB limit"
- Your PDF is too large
- Compress the PDF or use a smaller file

### Port already in use
- Another application is using port 8000
- Change the port in `main.py`: `uvicorn.run(..., port=8001)`

## 📝 Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and submit pull requests!

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI and OpenAI**

