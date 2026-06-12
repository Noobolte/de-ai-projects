# LLM-Powered Data Quality Checker

A hybrid data quality checker that combines Pandas (deterministic checks) 
with a local LLM via Ollama (semantic analysis) to automatically detect 
data quality issues in CSV files.

## What it does

- Detects null values in any column
- Finds duplicate rows
- Identifies type mismatches (text in numeric columns)
- Validates email format using regex
- Uses LLM to add severity ratings and descriptions
- Outputs structured JSON report

## Architecture