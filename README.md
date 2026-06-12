# LLM-Powered Data Quality Checker

An intelligent data quality checker that combines **Pandas** (deterministic checks)
with a **local LLM via Ollama** (semantic analysis) to automatically detect and
report data quality issues in CSV files — no API cost, runs fully offline.

---

## Problem it solves

Data engineers spend hours manually checking data quality before loading data
into warehouses. This tool automates detection of common issues and generates
a structured JSON report in seconds — saving time and catching problems early.

---

## Architecture
CSV File

↓

Pandas Layer  →  nulls, duplicates, type mismatches, invalid formats

↓

LLM Layer     →  severity ratings, descriptions, outliers, business logic

↓

Pydantic      →  validated structured output

↓

JSON Report

---

## Why hybrid approach?

| Check type | Tool | Reason |
|---|---|---|
| Null detection | Pandas | 100% accurate, never hallucinates |
| Duplicate detection | Pandas | Deterministic row comparison |
| Type mismatches | Pandas | Rule-based, fully reliable |
| Email format | Regex | Pattern matching, no ambiguity |
| Severity ratings | LLM | Requires contextual judgment |
| Business logic violations | LLM | Requires domain understanding |

Pure LLM approach hallucinates on deterministic tasks.
Pure code approach misses semantic issues.
Hybrid approach gets the best of both.

---

## Issues detected

- Null / missing values in any column
- Duplicate rows across all columns
- Type mismatches (text in numeric columns)
- Invalid email formats
- Outliers (age range, negative balances)
- Business logic violations

---

## Tech stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Core language |
| Ollama | Local LLM runtime (free, offline) |
| Llama 3.2 | LLM model for semantic analysis |
| Pandas | Deterministic data checks |
| Pydantic | Structured output validation |

---

## Project structure
data_quality_checker/

├── main.py           ← main checker logic

├── models.py         ← Pydantic output models

├── sample_data.csv   ← test dataset with intentional issues

├── quality_report.json ← generated output report

└── README.md

---

## How to run

### Prerequisites

- Python 3.8+
- Ollama installed from [ollama.ai](https://ollama.ai)

### Setup

```bash
# Clone the repo
git clone https://github.com/Noobolte/de-ai-projects.git
cd de-ai-projects

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install ollama pydantic pandas python-dotenv

# Pull the LLM model (one time only)
ollama pull llama3.2
```

### Run

```bash
python main.py
```

---

## Sample output
Running data quality check on sample_data.csv...
==================================================

DATA QUALITY REPORT
Total rows:    10

Total columns: 6

Total issues:  6

Quality score: 40%
Summary: 6 issues found with varying severities
ISSUES FOUND:

[HIGH] Column: account_balance

Type:    type_mismatch

Rows:    [9]

Details: Type mismatch in column
[MEDIUM] Column: ALL_COLUMNS

Type:    duplicate

Rows:    [0, 4]

Details: Duplicate rows found
[MEDIUM] Column: email

Type:    invalid_format

Rows:    [5]

Details: Invalid email format
[LOW] Column: name

Type:    null

Rows:    [8]

Details: Missing value in column
[LOW] Column: email

Type:    null

Rows:    [1]

Details: Missing value in column
[LOW] Column: account_balance

Type:    null

Rows:    [3]

Details: Missing value in column

Report saved to quality_report.json

---

## Key learnings

- LLMs hallucinate on deterministic tasks — always validate with code first
- Hybrid approach (Pandas + LLM) is more reliable than pure LLM
- Pydantic enforces output schema and prevents downstream errors
- Local LLMs via Ollama eliminate API costs completely
- JSON repair logic handles truncated LLM responses gracefully

---

## What's next

This is Project 1 of a 45-day Data Engineering + AI upskilling journey.

Upcoming projects:
- RAG pipeline over data documentation
- SQL Agent with natural language interface
- Pipeline Monitor Agent with Airflow integration
- End-to-end ML pipeline for loan default prediction

---

## Author

Building towards FAANG-level Data Engineer + AI Engineer roles.
Combining 4 years of Data Engineering experience with modern AI/LLM skills.