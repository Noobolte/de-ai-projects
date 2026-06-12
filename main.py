import json
import pandas as pd
import re
import ollama
from models import DataQualityReport


def load_data(filepath: str):
    df = pd.read_csv(filepath)
    data_str = df.to_string(index=True)
    schema = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        schema.append(f"{col} ({dtype}, {null_count} nulls)")
    schema_str = "\n".join(schema)
    return df, data_str, schema_str


def preprocess_issues(df):
    issues = []

    for col in df.columns:
        null_rows = df[df[col].isnull()].index.tolist()
        if null_rows:
            issues.append({
                "column": col,
                "issue_type": "null",
                "affected_rows": null_rows,
                "affected_count": len(null_rows)
            })

    dup_rows = df[df.duplicated(keep=False)].index.tolist()
    print(f"Duplicate rows found by pandas: {df[df.duplicated(keep=False)].index.tolist()}")
    if dup_rows:
        issues.append({
            "column": "ALL_COLUMNS",
            "issue_type": "duplicate",
            "affected_rows": dup_rows,
            "affected_count": len(dup_rows)
        })

    for col in df.columns:
        if col in ['age', 'account_balance', 'customer_id']:
            invalid_rows = []
            for idx, val in df[col].items():
                try:
                    if pd.notna(val):
                        float(val)
                except (ValueError, TypeError):
                    invalid_rows.append(idx)
            if invalid_rows:
                issues.append({
                    "column": col,
                    "issue_type": "type_mismatch",
                    "affected_rows": invalid_rows,
                    "affected_count": len(invalid_rows)
                })

    if 'email' in df.columns:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_email_rows = []
        for idx, val in df['email'].items():
            if pd.notna(val) and not re.match(email_pattern, str(val)):
                invalid_email_rows.append(idx)
        if invalid_email_rows:
            issues.append({
                "column": "email",
                "issue_type": "invalid_format",
                "affected_rows": invalid_email_rows,
                "affected_count": len(invalid_email_rows)
            })

    return issues


def check_quality(filepath: str) -> DataQualityReport:
    df, data_str, schema_str = load_data(filepath)

    # Step 1 — pandas finds all issues deterministically
    pandas_issues = preprocess_issues(df)
    pandas_issues_str = json.dumps(pandas_issues, indent=2)

    total_rows = len(df)
    total_columns = len(df.columns)

    # Step 2 — LLM ONLY adds severity + short description
    # Don't send full data — just the issues list
    system_prompt = "You are a data quality analyst. Add severity and description to each issue. Return only JSON."

    user_prompt = f"""Add severity (high/medium/low) and short description (max 8 words) to each issue.

    Issues:
    {pandas_issues_str}

    Return ONLY this JSON, nothing else:
    {{
    "total_rows": {total_rows},
    "total_columns": {total_columns},
    "total_issues": {len(pandas_issues)},
    "issues": [
        {{
        "column": "<from input>",
        "issue_type": "<from input>",
        "severity": "<high|medium|low>",
        "description": "<max 8 words>",
        "affected_rows": [<from input>],
        "affected_count": <from input>
        }}
    ],
    "overall_quality_score": <float 0-1>,
    "summary": "<max 15 words>"
    }}"""

    response = ollama.chat(
        model="llama3.2",
        options={
            "temperature": 0,
            "num_ctx": 8192,
            "num_predict": 4096
        },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw = response["message"]["content"].strip()

    # clean markdown
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

    # repair truncated JSON by closing any open brackets
    def repair_json(s):
        open_braces = s.count('{') - s.count('}')
        open_brackets = s.count('[') - s.count(']')
        
        # remove trailing comma before closing
        s = s.rstrip()
        if s.endswith(','):
            s = s[:-1]
        
        # close any open strings
        if s.count('"') % 2 != 0:
            s += '"'
        
        # close open brackets and braces
        s += ']' * open_brackets
        s += '}' * open_braces
        
        return s

    raw = repair_json(raw)
    print(f"Repaired raw length: {len(raw)}")

    try:
        report_dict = json.loads(raw)
        report = DataQualityReport(**report_dict)
        return report
    except json.JSONDecodeError as e:
        print(f"JSON Error after repair: {e}")
        print(f"Last 100 chars: {raw[-100:]}")
        raise



def print_report(report: DataQualityReport):
    print("\n" + "="*50)
    print("DATA QUALITY REPORT")
    print("="*50)
    print(f"Total rows:    {report.total_rows}")
    print(f"Total columns: {report.total_columns}")
    print(f"Total issues:  {report.total_issues}")
    print(f"Quality score: {report.overall_quality_score:.0%}")
    print(f"\nSummary: {report.summary}")
    print("\nISSUES FOUND:")
    print("-"*50)

    for i, issue in enumerate(report.issues, 1):
        severity_label = {
            "high": "[HIGH]",
            "medium": "[MEDIUM]",
            "low": "[LOW]"
        }.get(issue.severity, "[UNKNOWN]")

        print(f"\n{i}. {severity_label} Column: {issue.column}")
        print(f"   Type:    {issue.issue_type}")
        print(f"   Rows:    {issue.affected_rows}")
        print(f"   Details: {issue.description}")


if __name__ == "__main__":
    print("Running data quality check on sample_data.csv...")
    report = check_quality("sample_data.csv")
    print_report(report)

    with open("quality_report.json", "w") as f:
        f.write(report.model_dump_json(indent=2))
    print("\nReport saved to quality_report.json")