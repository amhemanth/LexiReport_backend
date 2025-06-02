from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin

class ReportType(enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    POWERBI = "powerbi"
    TABLEAU = "tableau"
    GOOGLE_DATA_STUDIO = "google_data_studio"

class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    description = Column(String)
    file_path = Column(String)  # Path to stored file
    report_type = Column(Enum(ReportType), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="reports")
    insights = relationship("ReportInsight", back_populates="report", cascade="all, delete-orphan")

class ReportInsight(Base, TimestampMixin):
    __tablename__ = "report_insights"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    content = Column(String, nullable=False)  # The extracted text insight
    insight_metadata = Column(JSON)  # Additional metadata about the insight (e.g., position in document, confidence score)
    
    # Relationships
    report = relationship("Report", back_populates="insights") 