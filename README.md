# ARENA (Autonomous Research + Execution Agent)

ARENA is a premium, high-performance autonomous research agent designed to decompose complex goals into executable tasks. It leverages the power of **Google Gemini 1.5 Flash** to provide a zero-cost, state-of-the-art intelligence core.

## 🚀 Key Features

- **Intelligence Core:** Powered by Gemini 1.5 Flash for rapid, accurate goal decomposition.
- **Multi-Agent Architecture:** Features Architect, Explorer, Engineer, and Auditor agents working in sync.
- **Glassmorphism UI:** A stunning, modern interface built with React and Vanilla CSS.
- **Zero Cost:** Optimized to run entirely on free-tier LLM providers.
- **Memory Engine:** Integrated vector store (ChromaDB) for long-term knowledge retention.
- **Word Export:** Download your synthesized research results directly to .doc or .md files.

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher

### 2. Backend Installation
```bash
# Clone the repository
git clone https://github.com/Talhayasin121/arena-agent-v2.git
cd arena-agent-v2

# Install Python dependencies
pip install fastapi uvicorn chromadb google-generativeai python-dotenv openai rich marked
```

### 3. Frontend Installation
```bash
cd arena-frontend
npm install
```

### 4. Configuration
1. Rename `.env.example` to `.env`.
2. Add your **GOOGLE_API_KEY** from [Google AI Studio](https://aistudio.google.com).
3. (Optional) Add your **NVIDIA_API_KEY** from [NVIDIA Build](https://build.nvidia.com).

### 5. Running ARENA
**Start the Backend:**
```bash
python server.py
```

**Start the Frontend:**
```bash
cd arena-frontend
npm run dev
```

Visit `http://localhost:5173` to start researching!

## 🧪 Technology Stack
- **Backend:** FastAPI, Python, ChromaDB
- **Frontend:** React, Vite, Framer Motion, Lucide Icons
- **AI Core:** Google Gemini, NVIDIA NIM (Fallback)

## 📄 License
MIT License. Free for personal and educational use.

---
*Built with ❤️ by ARENA Intelligence Core*
