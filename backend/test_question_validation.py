#!/usr/bin/env python
"""
Test script to validate challenge question data
Run this to see what's failing without using Django admin
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.challenges.models import ChallengeQuestion, Challenge

print("=" * 80)
print("CHALLENGE QUESTION VALIDATION TEST")
print("=" * 80)

# Test data - modify this to match what you're entering
test_data = {
    'question_text': '''What are the values of x, y, and z after executing the following code?

x = [1, 2, 3]
y = x
x += [4]
z = x + [5]

def modify(lst):
    lst = lst + [6]
    lst[0] = 99

modify(y)''',
    'question_type': 'multiple_choice',
    'options': [
        {"label": "A", "text": "x: [1, 2, 3, 4], y: [1, 2, 3, 4], z: [1, 2, 3, 4, 5]"},
        {"label": "B", "text": "x: [99, 2, 3, 4], y: [99, 2, 3, 4], z: [1, 2, 3, 4, 5]"},
        {"label": "C", "text": "x: [99, 2, 3, 4, 6], y: [99, 2, 3, 4, 6], z: [1, 2, 3, 4, 5, 6]"},
        {"label": "D", "text": "x: [1, 2, 3, 4, 6], y: [1, 2, 3, 4, 6], z: [1, 2, 3, 4, 5]"}
    ],
    'correct_options': ["A"],
    'correct_answer': '',
    'explanation': 'Test explanation',
    'order': 1,
}

print("\nTest Data:")
print(f"Question Type: {test_data['question_type']}")
print(f"Options: {test_data['options']}")
print(f"Correct Options: {test_data['correct_options']}")
print(f"Correct Answer: '{test_data['correct_answer']}'")

# Get first challenge for testing
try:
    challenge = Challenge.objects.first()
    if not challenge:
        print("\n❌ ERROR: No challenges found in database!")
        print("Please create a challenge first in Django admin.")
        sys.exit(1)
    
    print(f"\nUsing Challenge: {challenge.title} (ID: {challenge.id})")
    
    # Create question instance
    question = ChallengeQuestion(
        challenge=challenge,
        **test_data
    )
    
    print("\n" + "=" * 80)
    print("RUNNING VALIDATION...")
    print("=" * 80)
    
    # This will call clean() and show any validation errors
    question.clean()
    
    print("\n✅ VALIDATION PASSED!")
    print("The data is valid. You should be able to save this in Django admin.")
    
    # Try to save
    question.save()
    print(f"\n✅ SUCCESSFULLY SAVED! Question ID: {question.id}")
    
    # Clean up test data
    question.delete()
    print("✅ Test question deleted (cleanup)")
    
except Exception as e:
    print("\n❌ VALIDATION FAILED!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    
    if hasattr(e, 'message_dict'):
        print("\nDetailed Errors:")
        for field, messages in e.message_dict.items():
            print(f"  - {field}: {messages}")
    
    import traceback
    print("\nFull Traceback:")
    print(traceback.format_exc())

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
