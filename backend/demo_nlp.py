#!/usr/bin/env python3
"""
Demo script to showcase NLP parsing capabilities
"""

from nlp.clause_parser import ClauseParser

def main():
    parser = ClauseParser()

    # Test document with various clause types
    test_document = '''
Employment Agreement

Position: Senior Software Developer
Annual Salary: $95,000 per year
Working Hours: Monday to Friday, 9:00 AM to 6:00 PM
Notice Period: 4 weeks written notice required
Start Date: January 15, 2024
Probation: 6 months probationary period
Reports due by 5:30 PM every Friday
Deadline for project submission: March 30, 2024
Vacation: 3 weeks per year
Benefits: Health insurance effective immediately
'''

    print('=' * 60)
    print('    NLP CLAUSE PARSING DEMONSTRATION')
    print('=' * 60)
    print('📄 DOCUMENT TEXT:')
    print(test_document)
    print()

    # Parse the clauses
    clauses = parser.parse_clauses(test_document)

    print('🔍 EXTRACTED CLAUSES:')
    print('-' * 30)
    for clause_type, value in clauses.items():
        icon = {
            'salary': '💰',
            'working_hours': '🕐', 
            'notice_period': '📋',
            'deadline': '⏰',
            'important_dates': '📅'
        }.get(clause_type, '📝')
        
        print(f'{icon} {clause_type.replace("_", " ").title()}: {value}')

    print()
    print('✅ NLP parsing completed successfully!')
    print(f'📊 Total clauses extracted: {len(clauses)}')

if __name__ == "__main__":
    main()