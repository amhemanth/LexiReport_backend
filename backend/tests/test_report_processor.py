import pytest
from pathlib import Path
from app.services.report_processor import ReportProcessor

@pytest.fixture
def report_processor():
    return ReportProcessor()

@pytest.fixture
def sample_pdf_path(tmp_path):
    # Create a sample PDF file for testing
    pdf_path = tmp_path / "test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n%Test PDF content")
    return str(pdf_path)

@pytest.fixture
def sample_excel_path(tmp_path):
    # Create a sample Excel file for testing
    excel_path = tmp_path / "test.xlsx"
    with open(excel_path, "wb") as f:
        f.write(b"PK\x03\x04\x14\x00\x00\x00\x08\x00")  # Minimal Excel file header
    return str(excel_path)

def test_process_pdf(report_processor, sample_pdf_path):
    insights = report_processor.process_pdf(sample_pdf_path)
    assert isinstance(insights, list)
    # Add more specific assertions based on expected PDF processing results

def test_process_excel(report_processor, sample_excel_path):
    insights = report_processor.process_excel(sample_excel_path)
    assert isinstance(insights, list)
    # Add more specific assertions based on expected Excel processing results

def test_process_report_invalid_type(report_processor, sample_pdf_path):
    with pytest.raises(ValueError):
        report_processor.process_report(sample_pdf_path, "invalid_type") 