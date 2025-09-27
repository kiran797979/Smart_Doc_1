"""
Database Manager for Smart Doc Checker
Handles SQLite operations for storing documents, clauses, and contradictions
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database operations for the Smart Doc Checker"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file. If None, uses default path.
        """
        if db_path is None:
            # Create database in the backend directory
            db_dir = Path(__file__).parent.parent
            db_path = db_dir / "smart_doc_checker.db"
        
        self.db_path = str(db_path)
        self.connection = None
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
        return self.connection
    
    def initialize_database(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                clauses TEXT NOT NULL,  -- JSON string of extracted clauses
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Contradictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contradictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clause_type TEXT NOT NULL,
                documents TEXT NOT NULL,  -- JSON string of conflicting documents
                severity TEXT NOT NULL,
                summary TEXT NOT NULL,
                details TEXT,  -- JSON string with additional details
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis sessions table (for tracking bulk analyses)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_ids TEXT NOT NULL,  -- JSON array of document IDs
                total_contradictions INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Database initialized successfully")
    
    def store_document(self, filename: str, file_path: str, raw_text: str, clauses: Dict[str, Any]) -> int:
        """
        Store a document and its extracted clauses
        
        Args:
            filename: Name of the document file
            file_path: Full path to the document
            raw_text: Extracted plain text
            clauses: Dictionary of extracted clauses
            
        Returns:
            Document ID of the stored document
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO documents (filename, file_path, raw_text, clauses, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (filename, file_path, raw_text, json.dumps(clauses)))
        
        doc_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Stored document: {filename} (ID: {doc_id})")
        return doc_id
    
    def store_contradiction(self, contradiction: Dict[str, Any]) -> int:
        """
        Store a detected contradiction
        
        Args:
            contradiction: Dictionary containing contradiction details
            
        Returns:
            Contradiction ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO contradictions (clause_type, documents, severity, summary, details)
            VALUES (?, ?, ?, ?, ?)
        """, (
            contradiction["clause_type"],
            json.dumps(contradiction["documents"]),
            contradiction.get("severity", "medium"),
            contradiction.get("summary", ""),
            json.dumps(contradiction.get("details", {}))
        ))
        
        contradiction_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Stored contradiction: {contradiction['clause_type']} (ID: {contradiction_id})")
        return contradiction_id
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all stored documents"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, filename, file_path, clauses, created_at, updated_at
            FROM documents
            ORDER BY created_at DESC
        """)
        
        documents = []
        for row in cursor.fetchall():
            doc = {
                "id": row["id"],
                "filename": row["filename"],
                "file_path": row["file_path"],
                "clauses": json.loads(row["clauses"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
            documents.append(doc)
        
        return documents
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, filename, file_path, raw_text, clauses, created_at, updated_at
            FROM documents
            WHERE id = ?
        """, (doc_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "filename": row["filename"],
                "file_path": row["file_path"],
                "raw_text": row["raw_text"],
                "clauses": json.loads(row["clauses"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        return None
    
    def get_all_contradictions(self) -> List[Dict[str, Any]]:
        """Get all stored contradictions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, clause_type, documents, severity, summary, details, created_at
            FROM contradictions
            ORDER BY created_at DESC
        """)
        
        contradictions = []
        for row in cursor.fetchall():
            contradiction = {
                "id": row["id"],
                "clause_type": row["clause_type"],
                "documents": json.loads(row["documents"]),
                "severity": row["severity"],
                "summary": row["summary"],
                "details": json.loads(row["details"]) if row["details"] else {},
                "created_at": row["created_at"]
            }
            contradictions.append(contradiction)
        
        return contradictions
    
    def delete_document(self, doc_id: int) -> bool:
        """Delete a document and related contradictions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete the document
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        
        # Note: We keep contradictions for historical reference
        # In a production system, you might want to mark them as outdated
        
        conn.commit()
        return cursor.rowcount > 0
    
    def clear_all_data(self):
        """Clear all data from the database (useful for testing)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM contradictions")
        cursor.execute("DELETE FROM analysis_sessions")
        cursor.execute("DELETE FROM documents")
        
        conn.commit()
        print("✅ All data cleared from database")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Count documents
        cursor.execute("SELECT COUNT(*) as count FROM documents")
        doc_count = cursor.fetchone()["count"]
        
        # Count contradictions
        cursor.execute("SELECT COUNT(*) as count FROM contradictions")
        contradiction_count = cursor.fetchone()["count"]
        
        # Get most common clause types with contradictions
        cursor.execute("""SELECT clause_type, COUNT(*) as count 
                         FROM contradictions 
                         GROUP BY clause_type 
                         ORDER BY count DESC 
                         LIMIT 5""")
        common_contradictions = [{"clause_type": row["clause_type"], "count": row["count"]} 
                               for row in cursor.fetchall()]
        
        return {
            "total_documents": doc_count,
            "total_contradictions": contradiction_count,
            "common_contradiction_types": common_contradictions
        }
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


# Test the database functionality
if __name__ == "__main__":
    print("🗄️  Testing Database Manager")
    print("=" * 30)
    
    # Initialize database
    db = DatabaseManager()
    db.initialize_database()
    
    # Test storing a sample document
    sample_clauses = {
        "notice_period": "30 days",
        "working_hours": "9 AM to 5 PM",
        "termination_clause": "Either party may terminate"
    }
    
    doc_id = db.store_document(
        "test_contract.pdf",
        "/path/to/test_contract.pdf",
        "This is sample contract text...",
        sample_clauses
    )
    
    # Test storing a contradiction
    sample_contradiction = {
        "clause_type": "notice_period",
        "documents": [
            {"filename": "contract1.pdf", "value": "30 days"},
            {"filename": "contract2.pdf", "value": "2 weeks"}
        ],
        "severity": "high",
        "summary": "Notice period mismatch between contracts"
    }
    
    contradiction_id = db.store_contradiction(sample_contradiction)
    
    # Test retrieval
    all_docs = db.get_all_documents()
    all_contradictions = db.get_all_contradictions()
    stats = db.get_statistics()
    
    print(f"\n📊 Database Statistics:")
    print(f"Documents: {stats['total_documents']}")
    print(f"Contradictions: {stats['total_contradictions']}")
    
    print("\n✅ Database test completed successfully!")
    
    # Clean up test data
    db.clear_all_data()
    db.close()