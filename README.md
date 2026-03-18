# 🔍 traceRepo — Visualize Any Codebase

A developer tool that clones any public GitHub repository and generates a **beautiful, interactive architecture map** of the entire codebase in under 60 seconds. Powered by AI analysis and Mermaid diagrams rendered as zoomable SVGs.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) ![Analysis](https://img.shields.io/badge/Analysis-%3C%2060s-brightgreen?style=flat-square) ![Export](https://img.shields.io/badge/Export-SVG-orange?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🗂️ Project Structure

```
traceRepo/
├── app.py                  # Main Streamlit application & UI
├── requirements.txt
├── data/
│   └── repos/              # Cloned repositories (auto-created at runtime)
└── src/
    └── core/
        ├── cloner.py       # Git repository cloning
        ├── parser.py       # Source file parsing & extraction
        └── analyzer.py     # AI-powered architecture analysis
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Git available on your `PATH`
- An API key for your LLM provider (Anthropic / OpenAI)

### Installation

```bash
# 1. Clone this repo
git clone https://github.com/your-username/traceRepo.git
cd traceRepo

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501), paste any public GitHub URL, and hit **Analyze Repository**.

---

## 🧠 How It Works

```
  GitHub URL
      │
      ▼
  RepositoryCloner ──── git clone ──────► data/repos/<name>/
      │
      ▼
  RepositoryParser ──── walks file tree, reads source files
      │
      ▼
  RepositoryAnalyzer ── sends files to LLM, gets Mermaid + analysis back
      │
      ▼
  Streamlit UI ───────── compresses Mermaid → Kroki.io → renders SVG
```

Mermaid diagrams are zlib-compressed and base64-encoded before being sent to [Kroki.io](https://kroki.io), which returns a clean, scalable SVG — no local Mermaid runtime needed.

---

## ⚙️ Configuration

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | API key for Claude (Anthropic) |
| `OPENAI_API_KEY` | API key for GPT (OpenAI) |

Set either in a `.env` file at the project root.

---

## 🔌 Swapping the Analyzer

`RepositoryAnalyzer` in `src/core/analyzer.py` only needs to implement one method:

```python
def analyze_repository(self, files_data: list[dict]) -> str:
    """
    Input:  list of { "path": str, "content": str } dicts
    Output: markdown string containing a ```mermaid...``` block
            followed by a written analysis
    """
```

Drop in any LLM backend — Anthropic, OpenAI, Ollama, etc.

---

## 🔒 Privacy

- Only **public** GitHub repositories are supported.
- Cloned files are stored **locally** under `data/repos/` and never uploaded anywhere.
- Source files are sent to an external LLM API for analysis. Review your provider's data retention policy before analyzing sensitive code.

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit: `git commit -m "feat: describe your change"`
4. Push: `git push origin feat/your-feature`
5. Open a Pull Request

Please open an issue first for large or breaking changes.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">Built with Streamlit · Diagrams by Kroki · Analysis by AI</p>
