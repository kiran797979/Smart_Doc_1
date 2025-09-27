"""
Contradiction Detector for Smart Doc Checker
Compares clauses across documents to identify contradictions and inconsistencies
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
import json


class ContradictionDetector:
    """Detects contradictions and inconsistencies across multiple documents"""
    
    def __init__(self):
        """Initialize the contradiction detector"""
        self.similarity_threshold = 0.8
        self.contradiction_rules = self._setup_contradiction_rules()
    
    def _setup_contradiction_rules(self) -> Dict[str, Any]:
        """Setup rules for detecting contradictions in different clause types"""
        return {
            "notice_period": {
                "comparison_type": "time_duration",
                "severity": "high",
                "description": "Notice period requirements differ between documents"
            },
            "working_hours": {
                "comparison_type": "time_range",
                "severity": "medium",
                "description": "Working hours specifications are inconsistent"
            },
            "termination_clause": {
                "comparison_type": "text_semantic",
                "severity": "high",
                "description": "Termination conditions conflict between documents"
            },
            "deadline": {
                "comparison_type": "datetime",
                "severity": "high",
                "description": "Deadline requirements are contradictory"
            },
            "salary": {
                "comparison_type": "numeric",
                "severity": "critical",
                "description": "Salary amounts differ between documents"
            },
            "important_dates": {
                "comparison_type": "date_list",
                "severity": "medium",
                "description": "Important dates are inconsistent across documents"
            }
        }
    
    def detect_contradictions(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect contradictions across multiple documents
        
        Args:
            documents: List of documents with parsed clauses
            
        Returns:
            List of contradiction objects
        """
        if len(documents) < 2:
            return []
        
        contradictions = []
        
        # Group clauses by type across all documents
        clause_groups = self._group_clauses_by_type(documents)
        
        # Check each clause type for contradictions
        for clause_type, clause_instances in clause_groups.items():
            if len(clause_instances) >= 2:  # Need at least 2 instances to compare
                clause_contradictions = self._detect_clause_contradictions(
                    clause_type, clause_instances
                )
                contradictions.extend(clause_contradictions)
        
        # Sort by severity and add IDs
        contradictions = self._prioritize_contradictions(contradictions)
        
        return contradictions
    
    def _group_clauses_by_type(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group clauses by type across all documents"""
        clause_groups = defaultdict(list)
        
        for doc in documents:
            filename = doc.get("filename", "unknown")
            clauses = doc.get("clauses", {})
            
            for clause_type, clause_value in clauses.items():
                clause_groups[clause_type].append({
                    "filename": filename,
                    "doc_id": doc.get("doc_id"),
                    "file_path": doc.get("file_path"),
                    "value": clause_value,
                    "clause_type": clause_type
                })
        
        return dict(clause_groups)
    
    def _detect_clause_contradictions(self, clause_type: str, clause_instances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect contradictions for a specific clause type"""
        contradictions = []
        
        # Get comparison rules for this clause type
        rules = self.contradiction_rules.get(clause_type, {
            "comparison_type": "text_exact",
            "severity": "medium",
            "description": f"{clause_type} values differ between documents"
        })
        
        comparison_type = rules["comparison_type"]
        
        # Compare all pairs of clauses
        for i in range(len(clause_instances)):
            for j in range(i + 1, len(clause_instances)):
                clause1 = clause_instances[i]
                clause2 = clause_instances[j]
                
                is_contradiction, details = self._compare_clause_values(
                    clause1["value"], clause2["value"], comparison_type
                )
                
                if is_contradiction:
                    contradiction = {
                        "clause_type": clause_type,
                        "severity": rules["severity"],
                        "description": rules["description"],
                        "documents": [
                            {
                                "filename": clause1["filename"],
                                "doc_id": clause1.get("doc_id"),
                                "value": clause1["value"]
                            },
                            {
                                "filename": clause2["filename"],
                                "doc_id": clause2.get("doc_id"),
                                "value": clause2["value"]
                            }
                        ],
                        "details": details,
                        "summary": self._generate_contradiction_summary(clause1, clause2, clause_type)
                    }
                    contradictions.append(contradiction)
        
        return contradictions
    
    def _compare_clause_values(self, value1: Any, value2: Any, comparison_type: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Compare two clause values based on the comparison type
        
        Returns:
            Tuple of (is_contradiction, details_dict)
        """
        details = {
            "comparison_type": comparison_type,
            "value1": str(value1),
            "value2": str(value2)
        }
        
        try:
            if comparison_type == "time_duration":
                return self._compare_time_durations(value1, value2, details)
            elif comparison_type == "time_range":
                return self._compare_time_ranges(value1, value2, details)
            elif comparison_type == "numeric":
                return self._compare_numeric_values(value1, value2, details)
            elif comparison_type == "datetime":
                return self._compare_datetime_values(value1, value2, details)
            elif comparison_type == "date_list":
                return self._compare_date_lists(value1, value2, details)
            elif comparison_type == "text_semantic":
                return self._compare_text_semantic(value1, value2, details)
            else:  # text_exact
                return self._compare_text_exact(value1, value2, details)
                
        except Exception as e:
            details["error"] = str(e)
            return False, details
    
    def _compare_time_durations(self, value1: str, value2: str, details: Dict) -> Tuple[bool, Dict]:
        """Compare time durations (e.g., '30 days' vs '2 weeks')"""
        def parse_duration(value: str) -> Optional[int]:
            # Convert to days for comparison
            match = re.search(r'(\d+)\s+(days?|weeks?|months?)', str(value), re.IGNORECASE)
            if match:
                number, unit = match.groups()
                number = int(number)
                unit = unit.lower()
                
                if 'day' in unit:
                    return number
                elif 'week' in unit:
                    return number * 7
                elif 'month' in unit:
                    return number * 30  # Approximate
            return None
        
        days1 = parse_duration(value1)
        days2 = parse_duration(value2)
        
        details["parsed_days1"] = days1
        details["parsed_days2"] = days2
        
        if days1 is not None and days2 is not None:
            is_different = days1 != days2
            details["difference_days"] = abs(days1 - days2) if is_different else 0
            return is_different, details
        
        # Fallback to text comparison if parsing fails
        return str(value1).strip().lower() != str(value2).strip().lower(), details
    
    def _compare_time_ranges(self, value1: str, value2: str, details: Dict) -> Tuple[bool, Dict]:
        """Compare time ranges (e.g., '9 AM to 5 PM' vs '8 AM to 6 PM')"""
        def parse_time_range(value: str) -> Optional[Tuple[int, int]]:
            # Extract start and end hours (convert to 24-hour format)
            match = re.search(r'(\d{1,2})\s*(am|pm)\s*(?:to|-)\s*(\d{1,2})\s*(am|pm)', str(value), re.IGNORECASE)
            if match:
                start_hour, start_period, end_hour, end_period = match.groups()
                
                start_hour = int(start_hour)
                end_hour = int(end_hour)
                
                # Convert to 24-hour format
                if start_period.lower() == 'pm' and start_hour != 12:
                    start_hour += 12
                elif start_period.lower() == 'am' and start_hour == 12:
                    start_hour = 0
                    
                if end_period.lower() == 'pm' and end_hour != 12:
                    end_hour += 12
                elif end_period.lower() == 'am' and end_hour == 12:
                    end_hour = 0
                
                return (start_hour, end_hour)
            return None
        
        range1 = parse_time_range(value1)
        range2 = parse_time_range(value2)
        
        details["parsed_range1"] = range1
        details["parsed_range2"] = range2
        
        if range1 and range2:
            is_different = range1 != range2
            if is_different:
                details["start_time_diff"] = abs(range1[0] - range2[0])
                details["end_time_diff"] = abs(range1[1] - range2[1])
            return is_different, details
        
        # Fallback to text comparison
        return str(value1).strip().lower() != str(value2).strip().lower(), details
    
    def _compare_numeric_values(self, value1: str, value2: str, details: Dict) -> Tuple[bool, Dict]:
        """Compare numeric values (e.g., salaries)"""
        def extract_number(value: str) -> Optional[float]:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[$,]', '', str(value))
            
            # Handle K notation (thousands)
            if 'K' in cleaned.upper():
                k_match = re.search(r'(\d+(?:\.\d+)?)\s*K', cleaned, re.IGNORECASE)
                if k_match:
                    return float(k_match.group(1)) * 1000
            
            # Handle regular numbers
            match = re.search(r'(\d+(?:\.\d{2})?)', cleaned)
            if match:
                return float(match.group(1))
            return None
        
        num1 = extract_number(value1)
        num2 = extract_number(value2)
        
        details["parsed_num1"] = num1
        details["parsed_num2"] = num2
        
        if num1 is not None and num2 is not None:
            is_different = num1 != num2
            if is_different:
                details["difference"] = abs(num1 - num2)
                details["percentage_diff"] = (abs(num1 - num2) / max(num1, num2)) * 100
            return is_different, details
        
        return str(value1).strip() != str(value2).strip(), details
    
    def _compare_datetime_values(self, value1: str, value2: str, details: Dict) -> Tuple[bool, Dict]:
        """Compare datetime values"""
        # For now, do text comparison (could be enhanced with date parsing)
        normalized1 = re.sub(r'\s+', ' ', str(value1).strip().lower())
        normalized2 = re.sub(r'\s+', ' ', str(value2).strip().lower())
        
        is_different = normalized1 != normalized2
        details["normalized1"] = normalized1
        details["normalized2"] = normalized2
        
        return is_different, details
    
    def _compare_date_lists(self, value1: Any, value2: Any, details: Dict) -> Tuple[bool, Dict]:
        """Compare lists of dates"""
        if isinstance(value1, list) and isinstance(value2, list):
            set1 = set(str(v).strip().lower() for v in value1)
            set2 = set(str(v).strip().lower() for v in value2)
            
            is_different = set1 != set2
            details["common_dates"] = list(set1.intersection(set2))
            details["unique_to_doc1"] = list(set1.difference(set2))
            details["unique_to_doc2"] = list(set2.difference(set1))
            
            return is_different, details
        
        return self._compare_text_exact(value1, value2, details)
    
    def _compare_text_semantic(self, value1: str, value2: str, details: Dict) -> Tuple[bool, Dict]:
        """Compare text semantically (basic implementation)"""
        # Normalize and compare key terms
        text1 = str(value1).lower().strip()
        text2 = str(value2).lower().strip()
        
        # Extract key terms
        key_terms1 = set(re.findall(r'\b(?:terminate|end|dismiss|cause|notice|party)\b', text1))
        key_terms2 = set(re.findall(r'\b(?:terminate|end|dismiss|cause|notice|party)\b', text2))
        
        # Check for conflicting terms
        conflicting_pairs = [
            ('with', 'without'),
            ('cause', 'no cause'),
            ('immediate', 'notice'),
            ('either', 'employer only')
        ]
        
        has_conflict = False
        for term1, term2 in conflicting_pairs:
            if (term1 in text1 and term2 in text2) or (term2 in text1 and term1 in text2):
                has_conflict = True
                details["conflicting_terms"] = (term1, term2)
                break
        
        details["key_terms1"] = list(key_terms1)
        details["key_terms2"] = list(key_terms2)
        details["semantic_conflict"] = has_conflict
        
        # If no semantic conflict detected, check if texts are significantly different
        if not has_conflict:
            similarity = self._calculate_text_similarity(text1, text2)
            details["similarity_score"] = similarity
            has_conflict = similarity < 0.5  # Consider very different texts as potential conflicts
        
        return has_conflict, details
    
    def _compare_text_exact(self, value1: str, value2: str, details: Dict) -> Tuple[bool, Dict]:
        """Compare text exactly (case-insensitive)"""
        normalized1 = str(value1).strip().lower()
        normalized2 = str(value2).strip().lower()
        
        is_different = normalized1 != normalized2
        similarity = self._calculate_text_similarity(normalized1, normalized2)
        
        details["normalized1"] = normalized1
        details["normalized2"] = normalized2
        details["similarity_score"] = similarity
        
        return is_different, details
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic text similarity (Jaccard similarity)"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_contradiction_summary(self, clause1: Dict, clause2: Dict, clause_type: str) -> str:
        """Generate a human-readable summary of the contradiction"""
        doc1_name = clause1["filename"]
        doc2_name = clause2["filename"]
        value1 = clause1["value"]
        value2 = clause2["value"]
        
        return f"{clause_type.replace('_', ' ').title()}: '{value1}' in {doc1_name} vs '{value2}' in {doc2_name}"
    
    def _prioritize_contradictions(self, contradictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort contradictions by severity and add IDs"""
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        # Sort by severity, then by clause type
        contradictions.sort(key=lambda x: (
            severity_order.get(x["severity"], 3),
            x["clause_type"]
        ))
        
        # Add IDs
        for i, contradiction in enumerate(contradictions, 1):
            contradiction["id"] = i
        
        return contradictions
    
    def generate_contradiction_report(self, contradictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive contradiction report"""
        if not contradictions:
            return {
                "summary": "No contradictions found",
                "total_contradictions": 0,
                "by_severity": {},
                "by_clause_type": {},
                "recommendations": []
            }
        
        # Count by severity
        by_severity = defaultdict(int)
        by_clause_type = defaultdict(int)
        
        for contradiction in contradictions:
            by_severity[contradiction["severity"]] += 1
            by_clause_type[contradiction["clause_type"]] += 1
        
        # Generate recommendations
        recommendations = []
        if by_severity["critical"] > 0:
            recommendations.append("Address critical contradictions immediately, especially salary or legal terms")
        if by_severity["high"] > 0:
            recommendations.append("Review high-priority contradictions that may affect contract validity")
        if by_clause_type["notice_period"] > 0:
            recommendations.append("Standardize notice period requirements across all documents")
        if by_clause_type["working_hours"] > 0:
            recommendations.append("Align working hours specifications in all relevant documents")
        
        return {
            "summary": f"Found {len(contradictions)} contradiction(s) across documents",
            "total_contradictions": len(contradictions),
            "by_severity": dict(by_severity),
            "by_clause_type": dict(by_clause_type),
            "recommendations": recommendations,
            "most_critical": contradictions[0] if contradictions else None
        }


# Test the contradiction detector
if __name__ == "__main__":
    print("🔍 Testing Contradiction Detector")
    print("=" * 40)
    
    detector = ContradictionDetector()
    
    # Sample documents with contradictions
    sample_documents = [
        {
            "filename": "contract1.pdf",
            "clauses": {
                "notice_period": "30 days",
                "working_hours": "9 AM to 5 PM",
                "termination_clause": "Either party may terminate with cause",
                "salary": "$75,000"
            }
        },
        {
            "filename": "contract2.pdf",
            "clauses": {
                "notice_period": "2 weeks",
                "working_hours": "8 AM to 6 PM",
                "termination_clause": "Employer may terminate without cause",
                "salary": "$80,000"
            }
        },
        {
            "filename": "hr_policy.pdf",
            "clauses": {
                "notice_period": "1 month",
                "working_hours": "9 AM to 5 PM",
                "deadline": "End of fiscal year"
            }
        }
    ]
    
    print("Sample documents:")
    for doc in sample_documents:
        print(f"  - {doc['filename']}: {len(doc['clauses'])} clauses")
    
    print("\nDetecting contradictions...")
    contradictions = detector.detect_contradictions(sample_documents)
    
    print(f"\n📊 Found {len(contradictions)} contradiction(s):")
    for contradiction in contradictions:
        print(f"\n  ID: {contradiction['id']}")
        print(f"  Type: {contradiction['clause_type']}")
        print(f"  Severity: {contradiction['severity']}")
        print(f"  Summary: {contradiction['summary']}")
        print(f"  Documents involved: {len(contradiction['documents'])}")
    
    # Generate report
    report = detector.generate_contradiction_report(contradictions)
    print(f"\n📋 Report Summary:")
    print(f"  Total: {report['total_contradictions']}")
    print(f"  By severity: {report['by_severity']}")
    print(f"  Recommendations: {len(report['recommendations'])}")
    
    print("\n✅ Contradiction detector test completed!")