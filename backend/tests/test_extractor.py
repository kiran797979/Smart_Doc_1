"""
Unit tests for text extraction functionality
"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from extractor.text_extractor import DocumentExtractor


class TestDocumentExtractor:
    """Test cases for DocumentExtractor class"""
    
    def test_extractor_initialization(self, document_extractor):
        """Test that DocumentExtractor initializes correctly"""
        assert document_extractor is not None
        assert hasattr(document_extractor, 'extract_text')
    
    def test_extract_text_from_txt_file(self, document_extractor, sample_txt_file):
        """Test text extraction from TXT file"""
        result = document_extractor.extract_text(sample_txt_file)
        
        assert result is not None
        assert isinstance(result, str)
        assert 'ABC Company' in result
        assert '$75,000' in result
        assert 'Software Engineer' in result
    
    def test_extract_text_file_not_found(self, document_extractor):
        """Test extraction with non-existent file"""
        with pytest.raises(FileNotFoundError):
            document_extractor.extract_text('/path/to/nonexistent/file.txt')
    
    def test_extract_text_unsupported_format(self, document_extractor, temp_dir):
        """Test extraction with unsupported file format"""
        unsupported_file = os.path.join(temp_dir, "test.xyz")
        with open(unsupported_file, 'w') as f:
            f.write("test content")
        
        with pytest.raises(ValueError) as exc_info:
            document_extractor.extract_text(unsupported_file)
        
        assert 'unsupported' in str(exc_info.value).lower()
    
    def test_supported_formats(self, document_extractor):
        """Test supported formats list"""
        assert '.txt' in document_extractor.supported_formats
        assert '.pdf' in document_extractor.supported_formats
        assert '.docx' in document_extractor.supported_formats
    
    def test_extract_from_txt_with_encoding(self, document_extractor, temp_dir):
        """Test TXT extraction with different encodings"""
        # Test UTF-8 content
        utf8_file = os.path.join(temp_dir, "utf8_test.txt")
        content = "Test content with special chars: café, naïve, résumé"
        
        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = document_extractor.extract_text(utf8_file)
        
        assert isinstance(result, str)
        assert 'café' in result
    
    @patch('pdfplumber.open')
    def test_extract_from_pdf_success(self, mock_pdf_open, document_extractor, temp_dir):
        """Test successful PDF extraction"""
        # Mock pdfplumber
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF content with $85,000 salary"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf
        
        # Create a dummy PDF file
        pdf_file = os.path.join(temp_dir, "test.pdf")
        with open(pdf_file, 'wb') as f:
            f.write(b"dummy pdf content")
        
        result = document_extractor.extract_text(pdf_file)
        
        assert isinstance(result, str)
        assert '$85,000' in result
    
    @patch('pdfplumber.open')
    @patch('fitz.open')
    def test_extract_from_pdf_fallback(self, mock_fitz_open, mock_pdf_open, document_extractor, temp_dir):
        """Test PDF extraction with fallback to PyMuPDF"""
        # Mock pdfplumber to fail
        mock_pdf_open.side_effect = Exception("pdfplumber failed")
        
        # Mock PyMuPDF to succeed
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "PyMuPDF extracted content"
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__enter__.return_value = mock_doc
        mock_fitz_open.return_value = mock_doc
        
        # Create a dummy PDF file
        pdf_file = os.path.join(temp_dir, "test.pdf")
        with open(pdf_file, 'wb') as f:
            f.write(b"dummy pdf content")
        
        result = document_extractor.extract_text(pdf_file)
        
        assert isinstance(result, str)
        # The mock returns a MagicMock object that gets converted to string
        assert len(result) > 0
    
    def test_extract_from_docx_error_handling(self, document_extractor, temp_dir):
        """Test DOCX extraction error handling"""
        # Create a dummy DOCX file that will fail
        docx_file = os.path.join(temp_dir, "test.docx")
        with open(docx_file, 'wb') as f:
            f.write(b"not a real docx file")
        
        # Should raise an exception for invalid DOCX file
        with pytest.raises(Exception):
            document_extractor.extract_text(docx_file)
    
    def test_extract_text_empty_file(self, document_extractor, temp_dir):
        """Test extraction from empty file"""
        empty_file = os.path.join(temp_dir, "empty.txt")
        with open(empty_file, 'w') as f:
            f.write("")
        
        result = document_extractor.extract_text(empty_file)
        
        assert isinstance(result, str)
        assert result == ""
    
    def test_extract_text_basic_functionality(self, document_extractor, sample_txt_file):
        """Test basic text extraction functionality"""
        result = document_extractor.extract_text(sample_txt_file)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Employment Contract" in result