#!/usr/bin/env python3
"""
Demo script to showcase contradiction detection capabilities
"""

from main import SmartDocChecker
import json

def main():
    # Create checker instance
    checker = SmartDocChecker()

    # Create sample documents with intentional contradictions
    sample_docs = [
        {
            'filename': 'contract_a.txt',
            'doc_id': 1,
            'content': 'Employee salary is $75,000 per year. Working hours: 9 AM to 5 PM. Notice period: 30 days.',
            'clauses': {
                'salary': '$75,000',
                'working_hours': '9 AM to 5 PM',
                'notice_period': '30 days'
            }
        },
        {
            'filename': 'contract_b.txt',
            'doc_id': 2,
            'content': 'Annual compensation: $85,000. Work schedule: 8 AM to 6 PM. Required notice: 2 weeks.',
            'clauses': {
                'salary': '$85,000',
                'working_hours': '8 AM to 6 PM', 
                'notice_period': '2 weeks'
            }
        },
        {
            'filename': 'policy_manual.txt',
            'doc_id': 3,
            'content': 'Base salary: $80,000. Office hours: 9:00 AM - 5:30 PM. Termination notice: 1 month.',
            'clauses': {
                'salary': '$80,000',
                'working_hours': '9:00 AM - 5:30 PM',
                'notice_period': '1 month'
            }
        }
    ]

    # Detect contradictions
    contradictions = checker.detector.detect_contradictions(sample_docs)

    print('=' * 60)
    print('    SMART DOC CHECKER - CONTRADICTION DETECTION DEMO')
    print('=' * 60)
    print(f'📄 Documents analyzed: {len(sample_docs)}')
    print(f'⚠️  Contradictions found: {len(contradictions)}')
    print()

    if contradictions:
        print('🔍 DETECTED CONTRADICTIONS:')
        print('-' * 40)
        
        for i, contradiction in enumerate(contradictions, 1):
            severity_emoji = {
                'critical': '🔴',
                'high': '🟡', 
                'medium': '🟠'
            }.get(contradiction['severity'], '⚪')
            
            print(f'{i}. {contradiction["clause_type"].replace("_", " ").title()} Contradiction {severity_emoji}')
            print(f'   📊 Severity: {contradiction["severity"].upper()}')
            print(f'   📝 Description: {contradiction["description"]}')
            print(f'   💥 Conflicting values:')
            
            for doc in contradiction['documents']:
                print(f'      📄 {doc["filename"]}: "{doc["value"]}"')
            print()
        
        print('=' * 60)
        print('✅ System is working correctly - contradictions detected!')
    else:
        print('No contradictions found.')

if __name__ == "__main__":
    main()