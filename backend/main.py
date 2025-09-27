"""
Smart Doc Checker - Main Controller Script
Orchestrates the entire document analysis pipeline
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor.text_extractor import DocumentExtractor
from nlp.clause_parser import ClauseParser
from checker.contradiction_detector import ContradictionDetector
from database.db_manager import DatabaseManager


class SmartDocChecker:
    """Main controller class for the Smart Doc Checker application"""
    
    def __init__(self):
        """Initialize all components"""
        self.extractor = DocumentExtractor()
        self.parser = ClauseParser()
        self.detector = ContradictionDetector()
        self.db = DatabaseManager()
        
        # Initialize database
        self.db.initialize_database()
        
    def process_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Main pipeline to process multiple documents and detect contradictions
        
        Args:
            file_paths: List of paths to documents to analyze
            
        Returns:
            Dictionary containing analysis results and contradictions
        """
        try:
            results = {
                "documents": [],
                "contradictions": [],
                "summary": {
                    "total_documents": len(file_paths),
                    "total_contradictions": 0,
                    "processing_status": "success"
                }
            }
            
            # Step 1: Extract text from all documents
            print("🔍 Extracting text from documents...")
            extracted_texts = []
            for file_path in file_paths:
                try:
                    text = self.extractor.extract_text(file_path)
                    extracted_texts.append({
                        "file_path": file_path,
                        "filename": os.path.basename(file_path),
                        "text": text,
                        "status": "success"
                    })
                    print(f"✅ Extracted text from {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"❌ Failed to extract text from {os.path.basename(file_path)}: {str(e)}")
                    extracted_texts.append({
                        "file_path": file_path,
                        "filename": os.path.basename(file_path),
                        "text": "",
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Step 2: Parse clauses from extracted text
            print("\n🧠 Parsing clauses using NLP...")
            parsed_documents = []
            for doc_data in extracted_texts:
                if doc_data["status"] == "success" and doc_data["text"].strip():
                    try:
                        clauses = self.parser.parse_clauses(doc_data["text"])
                        doc_result = {
                            "filename": doc_data["filename"],
                            "file_path": doc_data["file_path"],
                            "clauses": clauses,
                            "status": "success"
                        }
                        parsed_documents.append(doc_result)
                        results["documents"].append(doc_result)
                        
                        # Store in database
                        doc_id = self.db.store_document(
                            doc_data["filename"], 
                            doc_data["file_path"], 
                            doc_data["text"], 
                            clauses
                        )
                        doc_result["doc_id"] = doc_id
                        
                        print(f"✅ Parsed clauses from {doc_data['filename']}")
                        print(f"   Found clauses: {list(clauses.keys())}")
                        
                    except Exception as e:
                        print(f"❌ Failed to parse clauses from {doc_data['filename']}: {str(e)}")
                        doc_result = {
                            "filename": doc_data["filename"],
                            "file_path": doc_data["file_path"],
                            "clauses": {},
                            "status": "failed",
                            "error": str(e)
                        }
                        results["documents"].append(doc_result)
            
            # Step 3: Detect contradictions across documents
            print("\n🔍 Detecting contradictions...")
            if len(parsed_documents) >= 2:
                contradictions = self.detector.detect_contradictions(parsed_documents)
                results["contradictions"] = contradictions
                results["summary"]["total_contradictions"] = len(contradictions)
                
                # Store contradictions in database
                for contradiction in contradictions:
                    self.db.store_contradiction(contradiction)
                
                if contradictions:
                    print(f"⚠️  Found {len(contradictions)} contradiction(s):")
                    for i, contradiction in enumerate(contradictions, 1):
                        print(f"   {i}. {contradiction['clause_type']}: {contradiction['summary']}")
                else:
                    print("✅ No contradictions found!")
            else:
                print("⚠️  Need at least 2 documents to detect contradictions")
                results["summary"]["processing_status"] = "insufficient_documents"
            
            print(f"\n📊 Processing complete!")
            print(f"   Documents processed: {len(results['documents'])}")
            print(f"   Contradictions found: {results['summary']['total_contradictions']}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error in main processing pipeline: {str(e)}")
            return {
                "documents": [],
                "contradictions": [],
                "summary": {
                    "total_documents": len(file_paths),
                    "total_contradictions": 0,
                    "processing_status": "error",
                    "error": str(e)
                }
            }
    
    def get_all_results(self) -> Dict[str, Any]:
        """Get all stored results from database"""
        return {
            "documents": self.db.get_all_documents(),
            "contradictions": self.db.get_all_contradictions()
        }
    
    def get_document_results(self, doc_id: int) -> Dict[str, Any]:
        """Get results for a specific document"""
        return self.db.get_document_by_id(doc_id)


def main():
    """Main function for testing the pipeline"""
    print("🚀 Smart Doc Checker - Testing Pipeline")
    print("=" * 50)
    
    # Initialize the checker
    checker = SmartDocChecker()
    
    # Test with sample documents (if they exist)
    uploads_dir = Path(__file__).parent.parent / "uploads"
    sample_files = list(uploads_dir.glob("*.pdf")) + list(uploads_dir.glob("*.docx")) + list(uploads_dir.glob("*.txt"))
    
    if sample_files:
        print(f"Found {len(sample_files)} sample documents:")
        for file in sample_files:
            print(f"  - {file.name}")
        
        # Process the documents
        results = checker.process_documents([str(f) for f in sample_files])
        
        # Print results
        print("\n" + "=" * 50)
        print("📋 ANALYSIS RESULTS")
        print("=" * 50)
        print(json.dumps(results, indent=2, default=str))
        
    else:
        print("No sample documents found in uploads/ directory")
        print("Add some PDF or DOCX files to test the pipeline")


if __name__ == "__main__":
    main()