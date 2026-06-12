from pydantic import BaseModel
from typing import List, Optional

class DataQualityIssue(BaseModel):
    column: str
    issue_type: str       # null, type_mismatch, outlier, duplicate, invalid_format
    severity: str         # high, medium, low
    description: str
    affected_rows: List[int]
    affected_count: int

class DataQualityReport(BaseModel):
    total_rows: int
    total_columns: int
    total_issues: int
    issues: List[DataQualityIssue]
    overall_quality_score: float   # 0.0 to 1.0
    summary: str