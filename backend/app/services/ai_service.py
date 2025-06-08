import os
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
import json
import logging
from datetime import datetime
from docx import Document
import pandas as pd
import openpyxl
from transformers import pipeline

from app.config.ai_settings import get_ai_settings
from app.models.reports import Report, ReportInsight
from app.schemas.insight import ReportInsightCreate

settings = get_ai_settings()
logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered report analysis and insight generation."""

    def __init__(self):
        self.model_path = settings.MODEL_PATH
        self.cache_dir = settings.CACHE_DIR
        self.max_workers = settings.MAX_WORKERS
        self.batch_size = settings.BATCH_SIZE
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
        self.keywords_pipeline = pipeline("feature-extraction", model="distilbert-base-uncased")  # Placeholder

    async def process_report(self, report: Report) -> List[ReportInsight]:
        """Process a report and generate insights."""
        try:
            # Read report content based on file type
            content = await self._read_report_content(report)
            
            # Generate insights
            insights = await self._generate_insights(content, report)
            
            return insights
        except Exception as e:
            logger.error(f"Error processing report {report.id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing report: {str(e)}"
            )

    async def _read_report_content(self, report: Report) -> str:
        """Read report content based on file type."""
        if not os.path.exists(report.file_path):
            raise HTTPException(status_code=404, detail="Report file not found")

        try:
            if report.file_type == "pdf":
                return await self._read_pdf(report.file_path)
            elif report.file_type == "docx":
                return await self._read_docx(report.file_path)
            elif report.file_type in ["xlsx", "xls"]:
                return await self._read_excel(report.file_path)
            elif report.file_type == "csv":
                return await self._read_csv(report.file_path)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {report.file_type}"
                )
        except Exception as e:
            logger.error(f"Error reading report content: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error reading report content: {str(e)}"
            )

    async def _generate_insights(
        self,
        content: str,
        report: Report
    ) -> List[ReportInsight]:
        """Generate insights from report content."""
        insights = []
        
        # Generate summary
        summary = await self._generate_summary(content)
        insights.append(
            ReportInsight(
                report_id=report.id,
                insight_type="summary",
                content=summary,
                confidence_score=0.9,
                metadata={
                    "model": "gpt-4",
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
        )

        # Generate key points
        key_points = await self._generate_key_points(content)
        insights.append(
            ReportInsight(
                report_id=report.id,
                insight_type="key_points",
                content=json.dumps(key_points),
                confidence_score=0.85,
                metadata={
                    "model": "gpt-4",
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
        )

        # Generate recommendations
        recommendations = await self._generate_recommendations(content)
        insights.append(
            ReportInsight(
                report_id=report.id,
                insight_type="recommendations",
                content=json.dumps(recommendations),
                confidence_score=0.8,
                metadata={
                    "model": "gpt-4",
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
        )

        return insights

    async def _read_pdf(self, file_path: str) -> str:
        """Read PDF file content."""
        # TODO: Implement PDF reading
        raise NotImplementedError("PDF reading not implemented")

    async def _read_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    async def _read_excel(self, file_path: str) -> str:
        wb = openpyxl.load_workbook(file_path)
        text = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                text.append("\t".join([str(cell) for cell in row if cell is not None]))
        return "\n".join(text)

    async def _read_csv(self, file_path: str) -> str:
        df = pd.read_csv(file_path)
        return df.to_csv(index=False)

    async def _generate_summary(self, content: str) -> str:
        summary = self.summarizer(content[:1024], max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']

    async def _generate_key_points(self, content: str) -> List[str]:
        # For demo, split summary into sentences as key points
        summary = await self._generate_summary(content)
        return [s.strip() for s in summary.split('.') if s.strip()]

    async def _generate_recommendations(self, content: str) -> List[str]:
        # Placeholder: Use summary as recommendations
        summary = await self._generate_summary(content)
        return [f"Recommendation: {s.strip()}" for s in summary.split('.') if s.strip()]

    async def answer_question(self, context: str, question: str) -> str:
        result = self.qa_pipeline(question=question, context=context[:512])
        return result['answer'] 