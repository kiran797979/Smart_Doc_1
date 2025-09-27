"""
Unit tests for contradiction detection functionality
"""
import pytest
from checker.contradiction_detector import ContradictionDetector


class TestContradictionDetector:
    """Test cases for ContradictionDetector class"""
    
    def test_detector_initialization(self, contradiction_detector):
        """Test that ContradictionDetector initializes correctly"""
        assert contradiction_detector is not None
        assert hasattr(contradiction_detector, 'detect_contradictions')
    
    def test_detect_salary_contradictions(self, contradiction_detector, sample_documents):
        """Test detection of salary contradictions"""
        contradictions = contradiction_detector.detect_contradictions(sample_documents)
        
        # Should find salary contradiction between $75,000 and $80,000
        salary_contradictions = [c for c in contradictions if c['clause_type'] == 'salary']
        assert len(salary_contradictions) > 0
        
        contradiction = salary_contradictions[0]
        assert contradiction['severity'] in ['critical', 'high', 'medium']
        assert len(contradiction['documents']) >= 2
        assert 'salary' in contradiction['summary'].lower()
    
    def test_detect_working_hours_contradictions(self, contradiction_detector):
        """Test detection of working hours contradictions"""
        documents = [
            {
                "id": 1,
                "filename": "contract.txt",
                "clauses": {"working_hours": ["9:00 AM to 5:00 PM"]},
                "status": "success"
            },
            {
                "id": 2,
                "filename": "policy.txt", 
                "clauses": {"working_hours": ["8:00 AM to 6:00 PM"]},
                "status": "success"
            }
        ]
        
        contradictions = contradiction_detector.detect_contradictions(documents)
        
        hours_contradictions = [c for c in contradictions if c['clause_type'] == 'working_hours']
        assert len(hours_contradictions) > 0
    
    def test_detect_notice_period_contradictions(self, contradiction_detector):
        """Test detection of notice period contradictions"""
        documents = [
            {
                "id": 1,
                "filename": "contract.txt",
                "clauses": {"notice_period": ["30 days"]},
                "status": "success"
            },
            {
                "id": 2,
                "filename": "handbook.txt",
                "clauses": {"notice_period": ["2 weeks"]},
                "status": "success"
            }
        ]
        
        contradictions = contradiction_detector.detect_contradictions(documents)
        
        notice_contradictions = [c for c in contradictions if c['clause_type'] == 'notice_period']
        assert len(notice_contradictions) > 0
        
        contradiction = notice_contradictions[0]
        assert 'notice' in contradiction['summary'].lower()
    
    def test_detect_deadline_contradictions(self, contradiction_detector, sample_documents):
        """Test detection of deadline contradictions"""
        contradictions = contradiction_detector.detect_contradictions(sample_documents)
        
        deadline_contradictions = [c for c in contradictions if c['clause_type'] == 'deadline']
        assert len(deadline_contradictions) > 0
        
        contradiction = deadline_contradictions[0]
        assert contradiction['severity'] in ['critical', 'high', 'medium']
    
    def test_no_contradictions_identical_documents(self, contradiction_detector):
        """Test that identical documents produce no contradictions"""
        documents = [
            {
                "id": 1,
                "filename": "doc1.txt",
                "clauses": {
                    "salary": ["$75,000"],
                    "working_hours": ["9:00 AM to 5:00 PM"]
                },
                "status": "success"
            },
            {
                "id": 2,
                "filename": "doc2.txt",
                "clauses": {
                    "salary": ["$75,000"],
                    "working_hours": ["9:00 AM to 5:00 PM"]
                },
                "status": "success"
            }
        ]
        
        contradictions = contradiction_detector.detect_contradictions(documents)
        
        # Should find no contradictions since values are identical
        assert len(contradictions) == 0
    
    def test_single_document_no_contradictions(self, contradiction_detector):
        """Test that single document produces no contradictions"""
        documents = [
            {
                "id": 1,
                "filename": "single.txt",
                "clauses": {
                    "salary": ["$75,000"],
                    "working_hours": ["9:00 AM to 5:00 PM"],
                    "notice_period": ["30 days"]
                },
                "status": "success"
            }
        ]
        
        contradictions = contradiction_detector.detect_contradictions(documents)
        
        # Single document cannot have contradictions with itself
        assert len(contradictions) == 0
    
    def test_empty_documents_list(self, contradiction_detector):
        """Test handling of empty documents list"""
        contradictions = contradiction_detector.detect_contradictions([])
        
        assert isinstance(contradictions, list)
        assert len(contradictions) == 0
    
    def test_documents_without_clauses(self, contradiction_detector):
        """Test handling of documents without relevant clauses"""
        documents = [
            {
                "id": 1,
                "filename": "empty1.txt",
                "clauses": {},
                "status": "success"
            },
            {
                "id": 2,
                "filename": "empty2.txt", 
                "clauses": {},
                "status": "success"
            }
        ]
        
        contradictions = contradiction_detector.detect_contradictions(documents)
        
        assert len(contradictions) == 0
    
    def test_severity_classification(self, contradiction_detector):
        """Test that contradictions are properly classified by severity"""
        documents = [
            {
                "id": 1,
                "filename": "contract.txt",
                "clauses": {
                    "salary": ["$50,000"],  # Large difference
                    "working_hours": ["9:00 AM to 5:00 PM"],
                    "notice_period": ["30 days"]
                },
                "status": "success"
            },
            {
                "id": 2,
                "filename": "policy.txt",
                "clauses": {
                    "salary": ["$100,000"],  # Large difference -> critical
                    "working_hours": ["9:30 AM to 5:30 PM"],  # Small difference -> medium
                    "notice_period": ["4 weeks"]  # Similar value -> low/medium
                },
                "status": "success"
            }
        ]
        
        contradictions = contradiction_detector.detect_contradictions(documents)
        
        # Should have different severity levels
        severities = [c['severity'] for c in contradictions]
        assert len(set(severities)) > 1  # Multiple severity levels
        
        # Salary contradiction should be critical due to large difference
        salary_contradictions = [c for c in contradictions if c['clause_type'] == 'salary']
        if salary_contradictions:
            assert salary_contradictions[0]['severity'] in ['critical', 'high']
    
    def test_contradiction_details_structure(self, contradiction_detector, sample_documents):
        """Test that contradiction objects have proper structure"""
        contradictions = contradiction_detector.detect_contradictions(sample_documents)
        
        assert len(contradictions) > 0
        
        for contradiction in contradictions:
            # Required fields
            assert 'clause_type' in contradiction
            assert 'severity' in contradiction
            assert 'summary' in contradiction
            assert 'documents' in contradiction
            
            # Verify documents structure
            assert len(contradiction['documents']) >= 2
            for doc in contradiction['documents']:
                assert 'filename' in doc
                assert 'value' in doc
            
            # Verify severity is valid
            assert contradiction['severity'] in ['critical', 'high', 'medium', 'low']
            
            # Verify clause type is valid
            assert contradiction['clause_type'] in [
                'salary', 'working_hours', 'notice_period', 'deadline', 'dates'
            ]
    
    def test_multiple_values_same_clause_type(self, contradiction_detector):
        """Test handling of documents with multiple values for same clause type"""
        documents = [
            {
                "id": 1,
                "filename": "doc1.txt",
                "clauses": {
                    "salary": ["$75,000", "$80,000"],  # Multiple salary values
                    "deadline": ["5:00 PM", "6:00 PM"]  # Multiple deadlines
                },
                "status": "success"
            },
            {
                "id": 2,
                "filename": "doc2.txt",
                "clauses": {
                    "salary": ["$85,000"],
                    "deadline": ["midnight"]
                },
                "status": "success"
            }
        ]
        
        contradictions = contradiction_detector.detect_contradictions(documents)
        
        # Should handle multiple values and still detect contradictions
        assert len(contradictions) > 0
        
        # Should find contradictions for both salary and deadline
        clause_types = [c['clause_type'] for c in contradictions]
        assert 'salary' in clause_types
        assert 'deadline' in clause_types
    
    def test_numerical_comparison_accuracy(self, contradiction_detector):
        """Test accuracy of numerical comparisons"""
        documents = [
            {
                "id": 1,
                "filename": "doc1.txt",
                "clauses": {"salary": ["$75,000"]},
                "status": "success"
            },
            {
                "id": 2,
                "filename": "doc2.txt",
                "clauses": {"salary": ["$75000"]},  # Same value, different format
                "status": "success"
            },
            {
                "id": 3,
                "filename": "doc3.txt",
                "clauses": {"salary": ["75K"]},  # Same value, K format
                "status": "success"
            }
        ]
        
        contradictions = contradiction_detector.detect_contradictions(documents)
        
        # Should recognize these as the same value and not report contradictions
        salary_contradictions = [c for c in contradictions if c['clause_type'] == 'salary']
        assert len(salary_contradictions) == 0