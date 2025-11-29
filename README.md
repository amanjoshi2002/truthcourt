# 🏛️ TruthCourt - AI-Powered Message Analysis System

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

An intelligent debate-based system that analyzes messages, claims, and content to determine their authenticity. TruthCourt uses dual AI agents (prosecutor and defender) powered by Google's Gemini AI to conduct multi-round debates before reaching a final verdict.

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Technologies](#-technologies)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Features
- 🤖 **Dual AI Analysis**: Two independent AI lawyers analyze content from opposing perspectives
- ⚖️ **Multi-Round Debates**: Configurable debate rounds for thorough analysis
- 🔍 **Web-Grounded Evidence**: Real-time Google Search integration for factual verification
- 💾 **RAG-Based Caching**: Semantic similarity matching to retrieve previous verdicts for similar cases
- 📊 **Comprehensive Logging**: Detailed debate logs saved for every analysis
- 🗄️ **SQLite Database**: Persistent storage of all debates and verdicts

### Advanced Features
- **Direct Verdict Mode**: Fast-track simple cases without full debate
- **Rate Limiting**: Built-in protection against API abuse (2 requests/day per IP)
- **CORS Support**: Ready for frontend integration
- **RESTful API**: Clean, documented endpoints
- **Error Handling**: Robust retry logic with exponential backoff
- **Health Monitoring**: Built-in health check endpoint

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask API Server                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   /analyze   │  │   /debates   │  │   /health    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Analysis Pipeline                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. RAGStore Check (Similarity Search)              │   │
│  │     └─ > 90% match? Return cached verdict           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  2. Direct Verdict (Optional for simple cases)      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  3. Full Debate (Complex cases)                     │   │
│  │     ┌───────────────┐    ┌───────────────┐          │   │
│  │     │  Prosecutor   │◄──►│   Defender    │          │   │
│  │     │  (Skeptical)  │    │  (Analytical) │          │   │
│  │     │  Gemini AI #1 │    │  Gemini AI #2 │          │   │
│  │     └───────┬───────┘    └───────┬───────┘          │   │
│  │             │                    │                   │   │
│  │             └──────┬─────────────┘                   │   │
│  │                    ▼                                 │   │
│  │            ┌───────────────┐                         │   │
│  │            │  Judge (AI)   │                         │   │
│  │            │  Gemini AI #1 │                         │   │
│  │            └───────┬───────┘                         │   │
│  │                    ▼                                 │   │
│  │            ┌───────────────┐                         │   │
│  │            │ Final Verdict │                         │   │
│  │            └───────────────┘                         │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Storage & Retrieval                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  SQLite DB   │  │  RAGStore    │  │  Log Files   │      │
│  │  (debates)   │  │  (vectors)   │  │  (.txt)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. **AI Lawyers** (`models/ai_lawyer.py`)
- **Prosecutor (Scam Analyst)**: Skeptically analyzes claims, looking for flaws, misinformation, and red flags
- **Defender (Legitimacy Analyst)**: Validates claims by finding supporting evidence and proper context
- Both use Google Search grounding for evidence-based arguments

#### 2. **Judge** (`models/judge.py`)
- Manages debate flow and records arguments
- Checks RAGStore for similar previous cases
- Provides direct verdicts for simple cases
- Analyzes full debates and renders final verdicts
- Saves debate logs to files

#### 3. **RAGStore** (`models/rag_store.py`)
- Uses sentence transformers for semantic similarity
- Caches previous verdicts with embeddings
- Returns cached verdicts for 90%+ similar cases
- Reduces API costs and improves response time

#### 4. **DebateDB** (`models/debate_db.py`)
- SQLite database for persistent storage
- Stores all debates, verdicts, and arguments
- Provides queryable history of all analyses

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API keys (2 required)
- Google Custom Search API key (optional, for enhanced search)

### Step 1: Clone the Repository
```bash
git clone https://github.com/amanjoshi2002/truthcourt.git
cd truthcourt
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the root directory:

```bash
cp .env.help .env
```

Edit `.env` with your credentials:
```env
# Gemini API keys (Get from https://makersuite.google.com/app/apikey)
GEMINI_KEY_1=your_first_gemini_api_key_here
GEMINI_KEY_2=your_second_gemini_api_key_here

# Google Custom Search (Optional - enhances search capabilities)
GOOGLE_API_KEY=your_google_api_key_here
SEARCH_ENGINE_ID=your_search_engine_id_here

# Debate Configuration
ROUNDS=3

# Optional
LOG_LEVEL=info
```

### Step 5: Test Installation
```bash
python app.py
```

If successful, you should see:
```
API connection successful!
 * Running on http://0.0.0.0:5000
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GEMINI_KEY_1` | Yes | Primary Gemini API key for Prosecutor & Judge | - |
| `GEMINI_KEY_2` | Yes | Secondary Gemini API key for Defender | - |
| `GOOGLE_API_KEY` | No | Google API key for custom search | - |
| `SEARCH_ENGINE_ID` | No | Google Custom Search Engine ID | - |
| `ROUNDS` | No | Number of debate rounds | 3 |
| `LOG_LEVEL` | No | Logging level (debug/info/warning/error) | info |

### Debate Rounds Configuration

Modify the number of debate rounds in `.env`:
```env
ROUNDS=5  # More rounds = more thorough analysis (but slower & more API calls)
```

**Recommendations:**
- **1-2 rounds**: Quick analysis for simple cases
- **3-4 rounds**: Balanced thoroughness (recommended)
- **5+ rounds**: Deep analysis for complex claims

### Rate Limiting

Configure in `app.py`:
```python
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],  # Modify these limits
    storage_uri="memory://"
)
```

## 📖 Usage

### Development Server
```bash
python app.py
```
Server runs on `http://localhost:5000`

### Production Server (Gunicorn)
```bash
gunicorn app:app -c gunicorn_config.py
```

### Testing Endpoints

#### Test Analysis (No Rate Limit)
```bash
curl -X POST http://localhost:5000/testanalyze \
  -H "Content-Type: application/json" \
  -d '{"message": "Drinking warm lemon water every morning can cure cancer and diabetes."}'
```

#### Production Analysis (Rate Limited)
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "Local officials announced that the new community center will open next month."}'
```

#### Get All Debates
```bash
curl http://localhost:5000/debates
```

#### Get Specific Debate
```bash
curl http://localhost:5000/debates/1
```

#### Health Check
```bash
curl http://localhost:5000/health
```

## 🔌 API Endpoints

### `POST /analyze`
Analyze a message with rate limiting (2 requests/day per IP).

**Request:**
```json
{
  "message": "Your message text here"
}
```

**Response:**
```json
{
  "debate_id": 1,
  "message": "Your message text here",
  "verdict": "SCAM",
  "summary": "This appears to be a scam based on urgent language and suspicious claims.",
  "evidence": [
    "Contains urgent time pressure tactics",
    "Requests personal financial information",
    "Uses non-standard contact methods"
  ],
  "arguments": [
    {
      "speaker": "Scam Analyst",
      "argument": "Round 1: ..."
    }
  ],
  "judge_statement": "Based on the debate...",
  "source": "debate"
}
```

### `POST /testanalyze`
Analyze without rate limiting (for testing only).

**Request/Response:** Same as `/analyze`

### `GET /debates`
Retrieve all debates.

**Query Parameters:**
- `limit` (optional): Maximum number of debates to return (default: 100)

**Response:**
```json
{
  "success": true,
  "count": 10,
  "debates": [
    {
      "id": 1,
      "message": "...",
      "verdict": "LEGITIMATE",
      "summary": "...",
      "evidence": [...],
      "created_at": "2025-11-29 12:34:56",
      "arguments": [...]
    }
  ]
}
```

### `GET /debates/<id>`
Get a specific debate by ID.

**Response:**
```json
{
  "success": true,
  "debate": {
    "id": 1,
    "message": "...",
    "verdict": "SCAM",
    "summary": "...",
    "evidence": [...],
    "arguments": [...]
  }
}
```

### `GET /health`
Check server health status.

**Response:**
```json
{
  "status": "healthy"
}
```

## 🧠 How It Works

### Analysis Flow

#### 1. **Similarity Check (RAGStore)**
```
Message → Encode to Vector → Compare with Cache
  ├─ Similarity > 90% → Return Cached Verdict ✓
  └─ Similarity < 90% → Proceed to Analysis
```

#### 2. **Direct Verdict (Simple Cases)**
```
Message → Judge Analysis → Quick Verdict
  ├─ Check scam indicators (urgency, requests for info, etc.)
  ├─ Check legitimacy indicators (professional, realistic, etc.)
  └─ Return verdict, summary, and key evidence
```

#### 3. **Full Debate (Complex Cases)**
```
Round 1:
  Prosecutor: Initial argument against the claim
  Defender:   Counter-argument supporting the claim

Round 2:
  Prosecutor: Response to defender + new evidence
  Defender:   Response to prosecutor + new evidence

Round N:
  [Continue for configured number of rounds]

Judge: Analyze all arguments → Final verdict
```

### Evidence Collection

Both AI lawyers use **Google Search Grounding**:
- Real-time web searches for facts
- Automatic citation of sources with URLs
- Evidence-based argumentation
- Multi-source verification

### Verdict Sources

| Source | Description | When Used |
|--------|-------------|-----------|
| `cached` | Retrieved from RAGStore | Similar case found (>90% similarity) |
| `direct` | Direct verdict without debate | Simple cases (currently disabled for testing) |
| `debate` | Full multi-round debate | Complex cases requiring thorough analysis |

## 📁 Project Structure

```
truthcourt/
│
├── app.py                      # Flask application & main routes
├── config.py                   # Environment configuration
├── gunicorn_config.py          # Production server config
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── .env.help                   # Environment template
│
├── models/                     # Core AI models
│   ├── __init__.py
│   ├── ai_lawyer.py           # Prosecutor & Defender agents
│   ├── judge.py               # Judge agent & verdict logic
│   ├── debate_db.py           # SQLite database interface
│   └── rag_store.py           # Vector store for caching
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── gemini_setup.py        # Gemini API setup & retry logic
│   └── web_search.py          # Web search utilities (optional)
│
├── debate_logs/                # Debate text logs (auto-generated)
│   └── *.txt                  # Timestamped debate records
│
├── debates.db                  # SQLite database (auto-generated)
├── case_cache.pkl             # RAGStore cache (auto-generated)
│
└── __pycache__/               # Python cache (auto-generated)
```

### Key Files Explained

#### `app.py`
- Flask application setup
- API endpoint definitions
- Rate limiting configuration
- Main analysis orchestration

#### `models/ai_lawyer.py`
- Implements Prosecutor and Defender agents
- Google Search grounding integration
- Structured argument formatting
- Debate round logic

#### `models/judge.py`
- Manages debate flow
- RAGStore similarity checking
- Direct verdict capability
- Final verdict analysis
- Debate logging

#### `models/rag_store.py`
- Sentence transformer embeddings
- Cosine similarity matching
- Vector cache management
- Semantic search

#### `models/debate_db.py`
- SQLite database operations
- Debate persistence
- Argument storage
- Query interface

#### `utils/gemini_setup.py`
- Gemini API initialization
- Retry logic with exponential backoff
- Rate limit handling
- Error recovery

## 🛠️ Technologies

### Backend Framework
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-Limiter** - Rate limiting
- **Gunicorn** - WSGI HTTP server

### AI & ML
- **Google Generative AI** (Gemini 2.0 Flash) - Main AI model
- **Sentence Transformers** - Text embeddings
- **Scikit-learn** - Similarity calculations

### Data Storage
- **SQLite** - Relational database
- **Pickle** - Vector cache serialization

### Other Libraries
- **python-dotenv** - Environment management
- **NumPy** - Numerical operations
- **Requests** - HTTP requests

## 🔒 Security Considerations

### API Keys
- Never commit `.env` file to version control
- Use separate API keys for development and production
- Rotate keys periodically
- Monitor API usage

### Rate Limiting
- Default: 2 requests/day per IP for `/analyze`
- `/testanalyze` has no rate limit (use with caution)
- Configurable in `app.py`

### Input Validation
- All inputs are validated for JSON format
- Message field is required
- Error handling for malformed requests

## 🚀 Deployment

### Render.com (Recommended)
1. Create new Web Service
2. Connect GitHub repository
3. Set environment variables in Render dashboard
4. Deploy command: `gunicorn app:app -c gunicorn_config.py`

### Heroku
1. Install Heroku CLI
2. Create Heroku app: `heroku create`
3. Set environment variables: `heroku config:set GEMINI_KEY_1=...`
4. Deploy: `git push heroku main`

### Docker (Coming Soon)
```dockerfile
# Dockerfile template
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "-c", "gunicorn_config.py"]
```

## 🧪 Testing

### Unit Tests (Coming Soon)
```bash
pytest tests/
```

### Manual Testing
Use the provided curl commands or tools like Postman:

**Test Scam Detection:**
```bash
curl -X POST http://localhost:5000/testanalyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "URGENT! Your account will be suspended unless you verify your information immediately. Click here and enter your SSN, bank account, and passwords."
  }'
```

**Test Legitimate Content:**
```bash
curl -X POST http://localhost:5000/testanalyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The local library announces extended hours starting next month. Visit our website for the updated schedule."
  }'
```

## 📊 Performance

### Response Times
- **Cached verdict**: ~0.5-1 seconds
- **Direct verdict**: ~3-5 seconds
- **Full debate (3 rounds)**: ~15-30 seconds
- **Full debate (5 rounds)**: ~25-50 seconds

### API Costs (Gemini Free Tier)
- **Requests per minute**: 15
- **Requests per day**: 1,500
- **Tokens per minute**: 1M
- Each debate uses ~2-4 API calls per round

### Storage
- **Database**: ~1KB per debate
- **RAGStore**: ~1KB per cached case
- **Logs**: ~5-10KB per debate log file

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide
- Add docstrings to all functions
- Update README.md for new features
- Test thoroughly before submitting

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** - For providing the powerful language models
- **Sentence Transformers** - For semantic similarity capabilities
- **Flask Community** - For the excellent web framework

## 📧 Contact

**Developer**: Aman Joshi  
**GitHub**: [@amanjoshi2002](https://github.com/amanjoshi2002)  
**Repository**: [truthcourt](https://github.com/amanjoshi2002/truthcourt)

## 🗺️ Roadmap

### Upcoming Features
- [ ] Frontend web interface
- [ ] Multi-language support
- [ ] Enhanced ML models for better accuracy
- [ ] User authentication system
- [ ] Custom verdict templates
- [ ] Export debates to PDF
- [ ] WebSocket support for real-time updates
- [ ] Docker containerization
- [ ] Comprehensive test suite
- [ ] API documentation with Swagger

### Known Issues
- Direct verdict mode currently disabled (testing purposes)
- Rate limiting uses in-memory storage (resets on restart)
- No user authentication yet

---

**Made with ⚖️ by Aman Joshi** | **Powered by Google Gemini AI**
