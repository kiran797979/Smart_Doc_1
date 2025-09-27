# Test configuration and fixtures
import pytest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from extractor.text_extractor import DocumentExtractor
from nlp.clause_parser import ClauseParser
from checker.contradiction_detector import ContradictionDetector
from database.db_manager import DatabaseManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_txt_file(temp_dir):
    """Create a sample text file for testing"""
    content = """
    Employment Contract - ABC Company
    
    Position: Software Engineer
    Annual Salary: $75,000
    Working Hours: 9:00 AM to 5:00 PM, Monday to Friday
    Notice Period: 30 days written notice required
    Start Date: January 15, 2024
    
    Employee must submit reports by 5:00 PM daily.
    """
    file_path = os.path.join(temp_dir, "test_contract.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return """
    HR Policy Manual
    
    Compensation Guidelines:
    - Base salary range: $80,000 - $90,000
    - Working schedule: 40 hours per week
    - Standard hours: 8:00 AM to 6:00 PM
    - Notice requirement: 2 weeks advance notice
    - Policy effective: March 1, 2024
    
    All deadlines are midnight unless specified otherwise.
    """


@pytest.fixture
def document_extractor():
    """Create DocumentExtractor instance"""
    return DocumentExtractor()


@pytest.fixture
def clause_parser():
    """Create ClauseParser instance"""
    return ClauseParser()


@pytest.fixture
def contradiction_detector():
    """Create ContradictionDetector instance"""
    return ContradictionDetector()


@pytest.fixture
def test_database(temp_dir):
    """Create test database"""
    db_path = os.path.join(temp_dir, "test.db")
    db_manager = DatabaseManager(db_path)
    yield db_manager
    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def sample_documents():
    """Sample document data for testing"""
    return [
        {
            "id": 1,
            "filename": "contract.txt",
            "file_path": "/path/to/contract.txt",
            "clauses": {
                "salary": ["$75,000"],
                "working_hours": ["9:00 AM to 5:00 PM"],
                "notice_period": ["30 days"],
                "deadline": ["5:00 PM"]
            },
            "status": "success"
        },
        {
            "id": 2,
            "filename": "hr_policy.txt",
            "file_path": "/path/to/hr_policy.txt",
            "clauses": {
                "salary": ["$80,000"],
                "working_hours": ["8:00 AM to 6:00 PM"],
                "notice_period": ["2 weeks"],
                "deadline": ["midnight"]
            },
            "status": "success"
        }
    ]


@pytest.fixture
def sample_contradictions():
    """Sample contradiction data for testing"""
    return [
        {
            "clause_type": "salary",
            "severity": "critical",
            "summary": "Salary discrepancy between documents",
            "documents": [
                {"filename": "contract.txt", "value": "$75,000"},
                {"filename": "hr_policy.txt", "value": "$80,000"}
            ],
            "details": {"difference": 5000, "percentage": 6.67}
        }
    ]