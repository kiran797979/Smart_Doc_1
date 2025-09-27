"""
Clause Parser for Smart Doc Checker
Uses NLP to identify and extract key clauses from document text
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

try:
    import spacy
    from spacy.matcher import Matcher
except ImportError:
    spacy = None
    Matcher = None

try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None


class ClauseParser:
    """Extracts structured clauses from document text using NLP"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the clause parser
        
        Args:
            model_name: spaCy model to use for NLP processing
        """
        self.model_name = model_name
        self.nlp = None
        self.matcher = None
        
        # Initialize spaCy if available
        if spacy is not None:
            try:
                self.nlp = spacy.load(model_name)
                self.matcher = Matcher(self.nlp.vocab)
                self._setup_patterns()
                print(f"✅ Loaded spaCy model: {model_name}")
            except OSError:
                print(f"⚠️  spaCy model '{model_name}' not found. Install with: python -m spacy download {model_name}")
                self.nlp = None
        else:
            print("⚠️  spaCy not available. Install with: pip install spacy")
        
        # Regex patterns for basic clause detection (fallback)
        self._setup_regex_patterns()
    
    def _setup_patterns(self):
        """Setup spaCy matcher patterns for different clause types"""
        if not self.matcher:
            return
        
        # Notice period patterns
        notice_patterns = [
            [{"LOWER": {"IN": ["notice", "notification"]}}, 
             {"LOWER": "period", "OP": "?"}, 
             {"LOWER": "of", "OP": "?"}, 
             {"IS_DIGIT": True}, 
             {"LOWER": {"IN": ["days", "weeks", "months", "day", "week", "month"]}}],
            
            [{"IS_DIGIT": True}, 
             {"LOWER": {"IN": ["days", "weeks", "months", "day", "week", "month"]}}, 
             {"LOWER": {"IN": ["notice", "notification"]}}],
             
            [{"LOWER": {"IN": ["thirty", "sixty", "ninety", "fourteen"]}}, 
             {"LOWER": {"IN": ["days", "day"]}}, 
             {"LOWER": {"IN": ["notice", "notification"]}}]
        ]
        self.matcher.add("NOTICE_PERIOD", notice_patterns)
        
        # Working hours patterns
        working_hours_patterns = [
            [{"LOWER": {"IN": ["working", "work", "office"]}}, 
             {"LOWER": "hours"}, 
             {"IS_PUNCT": True, "OP": "?"}, 
             {"LIKE_NUM": True}, 
             {"LOWER": {"IN": ["am", "pm", "to", "-"]}, "OP": "*"}, 
             {"LIKE_NUM": True}, 
             {"LOWER": {"IN": ["am", "pm"]}}],
             
            [{"LIKE_NUM": True}, 
             {"LOWER": {"IN": ["am", "pm"]}}, 
             {"LOWER": {"IN": ["to", "-"]}}, 
             {"LIKE_NUM": True}, 
             {"LOWER": {"IN": ["am", "pm"]}}]
        ]
        self.matcher.add("WORKING_HOURS", working_hours_patterns)
        
        # Termination clause patterns
        termination_patterns = [
            [{"LOWER": {"IN": ["terminate", "termination", "end", "dismiss"]}}, 
             {"LOWER": {"IN": ["employment", "contract", "agreement"]}, "OP": "?"}, 
             {"IS_ALPHA": True, "OP": "*"}],
             
            [{"LOWER": {"IN": ["either", "any"]}}, 
             {"LOWER": "party"}, 
             {"LOWER": "may"}, 
             {"LOWER": {"IN": ["terminate", "end"]}}]
        ]
        self.matcher.add("TERMINATION", termination_patterns)
        
        # Deadline patterns
        deadline_patterns = [
            [{"LOWER": {"IN": ["deadline", "due", "expires", "expire"]}}, 
             {"IS_ALPHA": True, "OP": "*"}, 
             {"LOWER": {"IN": ["by", "on", "before"]}, "OP": "?"}, 
             {"LOWER": {"IN": ["midnight", "noon", "morning", "evening"]}}],
             
            [{"LOWER": "must"}, 
             {"LOWER": "be"}, 
             {"LOWER": {"IN": ["completed", "submitted", "done"]}}, 
             {"LOWER": "by"}, 
             {"IS_ALPHA": True, "OP": "*"}]
        ]
        self.matcher.add("DEADLINE", deadline_patterns)
    
    def _setup_regex_patterns(self):
        """Setup regex patterns as fallback for clause detection"""
        self.regex_patterns = {
            "notice_period": [
                r"(\d+)\s+(days?|weeks?|months?)\s+notice",
                r"notice\s+period\s+of\s+(\d+)\s+(days?|weeks?|months?)",
                r"(thirty|sixty|ninety|fourteen)\s+days?\s+notice",
                r"(\d+)\s+(day|week|month)\s+notice\s+period"
            ],
            
            "working_hours": [
                r"(\d{1,2})\s*(am|pm)\s*(?:to|-)\s*(\d{1,2})\s*(am|pm)",
                r"working\s+hours?\s*:?\s*(\d{1,2})\s*(am|pm)\s*(?:to|-)\s*(\d{1,2})\s*(am|pm)",
                r"office\s+hours?\s*:?\s*(\d{1,2})\s*(am|pm)\s*(?:to|-)\s*(\d{1,2})\s*(am|pm)",
                r"(\d{1,2}):\d{2}\s*(?:to|-)\s*(\d{1,2}):\d{2}"
            ],
            
            "termination_clause": [
                r"(?:either|any)\s+party\s+may\s+terminate",
                r"termination\s+of\s+(?:employment|contract|agreement)",
                r"(?:terminate|end)\s+(?:this\s+)?(?:employment|contract|agreement)",
                r"dismissal\s+(?:with|without)\s+cause"
            ],
            
            "deadline": [
                r"deadline\s*:?\s*(.*?)(?:\.|$)",
                r"due\s+(?:by|on|before)\s+(.*?)(?:\.|$)",
                r"must\s+be\s+(?:completed|submitted|done)\s+by\s+(.*?)(?:\.|$)",
                r"expires?\s+(?:on|at)\s+(.*?)(?:\.|$)"
            ],
            
            "salary": [
                r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"salary\s+of\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"(\d{1,3}(?:,\d{3})*)\s+(?:dollars?|usd)",
                r"annual\s+compensation\s+of\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
            ],
            
            "dates": [
                r"(\d{1,2}\/\d{1,2}\/\d{2,4})",
                r"(\d{1,2}-\d{1,2}-\d{2,4})",
                r"((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4})",
                r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})"
            ]
        }
    
    def parse_clauses(self, text: str) -> Dict[str, Any]:
        """
        Parse clauses from document text
        
        Args:
            text: Document text to parse
            
        Returns:
            Dictionary of extracted clauses
        """
        clauses = {}
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Use spaCy if available, otherwise fall back to regex
        if self.nlp is not None:
            clauses.update(self._parse_with_spacy(cleaned_text))
        
        # Always run regex patterns (can catch things spaCy might miss)
        clauses.update(self._parse_with_regex(cleaned_text))
        
        # Post-process and validate clauses
        clauses = self._post_process_clauses(clauses)
        
        return clauses
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for processing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page separators
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Normalize common variations
        text = re.sub(r'\b(thirty|30)\b', '30', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(sixty|60)\b', '60', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(ninety|90)\b', '90', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(fourteen|14)\b', '14', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _parse_with_spacy(self, text: str) -> Dict[str, Any]:
        """Parse clauses using spaCy NLP"""
        clauses = {}
        doc = self.nlp(text)
        
        # Find matches using the matcher
        matches = self.matcher(doc)
        
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            
            if label == "NOTICE_PERIOD":
                clauses["notice_period"] = self._extract_notice_period(span.text)
            elif label == "WORKING_HOURS":
                clauses["working_hours"] = self._extract_working_hours(span.text)
            elif label == "TERMINATION":
                clauses["termination_clause"] = span.text.strip()
            elif label == "DEADLINE":
                clauses["deadline"] = self._extract_deadline(span.text)
        
        return clauses
    
    def _parse_with_regex(self, text: str) -> Dict[str, Any]:
        """Parse clauses using regex patterns"""
        clauses = {}
        
        for clause_type, patterns in self.regex_patterns.items():
            matches = []
            
            for pattern in patterns:
                found = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in found:
                    matches.append(match.group().strip())
            
            if matches:
                # Take the first match for now (could be improved)
                raw_match = matches[0]
                
                # Process the match based on clause type
                if clause_type == "notice_period":
                    clauses[clause_type] = self._extract_notice_period(raw_match)
                elif clause_type == "working_hours":
                    clauses[clause_type] = self._extract_working_hours(raw_match)
                elif clause_type == "deadline":
                    clauses[clause_type] = self._extract_deadline(raw_match)
                elif clause_type == "dates":
                    if "important_dates" not in clauses:
                        clauses["important_dates"] = []
                    clauses["important_dates"].extend(matches[:3])  # Limit to 3 dates
                else:
                    clauses[clause_type] = raw_match
        
        return clauses
    
    def _extract_notice_period(self, text: str) -> str:
        """Extract and normalize notice period"""
        # Try to find number + time unit
        match = re.search(r'(\d+)\s+(days?|weeks?|months?)', text, re.IGNORECASE)
        if match:
            number, unit = match.groups()
            unit = unit.lower().rstrip('s') + ('s' if int(number) > 1 else '')
            return f"{number} {unit}"
        
        # Handle written numbers
        written_numbers = {
            'fourteen': '14', 'thirty': '30', 'sixty': '60', 'ninety': '90'
        }
        for word, num in written_numbers.items():
            if word in text.lower():
                if 'day' in text.lower():
                    return f"{num} days"
                elif 'week' in text.lower():
                    return f"{num} weeks"
                elif 'month' in text.lower():
                    return f"{num} months"
        
        return text.strip()
    
    def _extract_working_hours(self, text: str) -> str:
        """Extract and normalize working hours"""
        # Look for time patterns like "9 AM to 5 PM"
        match = re.search(r'(\d{1,2})\s*(am|pm)\s*(?:to|-)\s*(\d{1,2})\s*(am|pm)', text, re.IGNORECASE)
        if match:
            start_hour, start_period, end_hour, end_period = match.groups()
            return f"{start_hour} {start_period.upper()} to {end_hour} {end_period.upper()}"
        
        # Look for 24-hour format
        match = re.search(r'(\d{1,2}):\d{2}\s*(?:to|-)\s*(\d{1,2}):\d{2}', text)
        if match:
            return match.group()
        
        return text.strip()
    
    def _extract_deadline(self, text: str) -> str:
        """Extract and normalize deadline"""
        # Try to extract the deadline part
        deadline_match = re.search(r'(?:deadline|due|expires?|must\s+be\s+(?:completed|submitted|done))\s*:?\s*(?:by|on|before)?\s*(.*?)(?:\.|$)', text, re.IGNORECASE)
        if deadline_match:
            deadline = deadline_match.group(1).strip()
            
            # Try to parse as date if possible
            if date_parser:
                try:
                    parsed_date = date_parser.parse(deadline)
                    return parsed_date.strftime("%B %d, %Y")
                except:
                    pass
            
            return deadline
        
        return text.strip()
    
    def _post_process_clauses(self, clauses: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process and validate extracted clauses"""
        processed = {}
        
        for key, value in clauses.items():
            if isinstance(value, str):
                # Clean up the value
                value = value.strip()
                value = re.sub(r'\s+', ' ', value)
                
                # Skip very short or very long values
                if len(value) < 2 or len(value) > 200:
                    continue
                
                processed[key] = value
            elif isinstance(value, list):
                # Clean up list values
                cleaned_list = [v.strip() for v in value if v.strip() and len(v.strip()) > 2]
                if cleaned_list:
                    processed[key] = cleaned_list
        
        return processed
    
    def analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze the structure of the text for debugging"""
        analysis = {
            "total_length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.findall(r'[.!?]+', text)),
            "paragraph_count": len([p for p in text.split('\n\n') if p.strip()])
        }
        
        if self.nlp:
            doc = self.nlp(text[:1000])  # Analyze first 1000 chars
            analysis["entities"] = [(ent.text, ent.label_) for ent in doc.ents]
            analysis["pos_tags"] = [(token.text, token.pos_) for token in doc if token.pos_ in ['NOUN', 'VERB', 'ADJ']][:10]
        
        return analysis


# Test the clause parser
if __name__ == "__main__":
    print("🧠 Testing Clause Parser")
    print("=" * 30)
    
    parser = ClauseParser()
    
    # Test with sample contract text
    sample_text = """
    EMPLOYMENT CONTRACT
    
    This agreement is between Company ABC and John Doe.
    
    1. The employee must provide 30 days notice before termination.
    2. Working hours are from 9 AM to 5 PM, Monday through Friday.
    3. Either party may terminate this agreement with proper notice.
    4. All reports must be submitted by midnight on the deadline.
    5. Annual salary is $75,000.
    6. This contract expires on December 31, 2024.
    """
    
    print("Sample text:")
    print(sample_text[:200] + "...")
    
    print("\nExtracting clauses...")
    clauses = parser.parse_clauses(sample_text)
    
    print("\n📋 Extracted Clauses:")
    for clause_type, value in clauses.items():
        print(f"  {clause_type}: {value}")
    
    # Test structure analysis
    print("\n📊 Text Analysis:")
    analysis = parser.analyze_text_structure(sample_text)
    for key, value in analysis.items():
        if key != "pos_tags":  # Skip verbose POS tags
            print(f"  {key}: {value}")
    
    print("\n✅ Clause parser test completed!")