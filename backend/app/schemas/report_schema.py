from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    COMPREHENSIVE = "COMPREHENSIVE"
    TECHNICAL = "TECHNICAL"
    FUNDAMENTAL = "FUNDAMENTAL"
    DAILY_DIGEST = "DAILY_DIGEST"


class ReportFormat(str, Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"
    JSON = "JSON"
    HTML = "HTML"


class ReportGenerateRequest(BaseModel):
    userId: int
    reportType: ReportType
    symbols: List[str] = Field(..., min_items=1)
    includeFundamental: bool = True
    includeTechnical: bool = True
    includeSentiment: bool = True
    format: ReportFormat = ReportFormat.PDF
    deliveryChannels: List[str] = Field(default_factory=list)


class ReportGenerateResponse(BaseModel):
    reportId: str
    status: str
    estimatedTime: int
    downloadUrl: Optional[str] = None
    notificationSent: bool = False
