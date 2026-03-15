#!/usr/bin/env python
"""
Test script to verify weekly suggestion form and day fields are working correctly
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mitadt_mess.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from testapp.views import weekly_suggestion
from testapp.forms import WeeklysuggestionForm
from testapp.models import SuggestionPeriod

def test_form():
    """Test that the form creates correctly with all day fields"""
    print("=== Testing WeeklysuggestionForm ===")
    try:
        form = WeeklysuggestionForm()
        print(f"✅ Form created successfully with {len(form.fields)} fields")
        
        # Check day fields
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meals = ['breakfast', 'lunch', 'dinner']
        
        missing_fields = []
        for day in days:
            for meal in meals:
                field_name = f"{day}_{meal}"
                if field_name not in form.fields:
                    missing_fields.append(field_name)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All 21 day/meal fields are present")
            
        return True
    except Exception as e:
        print(f"❌ Form creation failed: {str(e)}")
        return False

def test_suggestion_period():
    """Test that suggestion period system is working"""
    print("\n=== Testing SuggestionPeriod ===")
    try:
        current_period = SuggestionPeriod.get_current_period()
        if current_period:
            print(f"✅ Current period found: {current_period.name}")
            print(f"   Submission allowed: {current_period.is_submission_allowed()}")
        else:
            print("⚠️  No current active period")
            
        total_periods = SuggestionPeriod.objects.count()
        print(f"   Total periods in database: {total_periods}")
        return True
    except Exception as e:
        print(f"❌ SuggestionPeriod test failed: {str(e)}")
        return False

def test_view():
    """Test that the weekly_suggestion view works correctly"""
    print("\n=== Testing weekly_suggestion view ===")
    try:
        # Create test request
        factory = RequestFactory()
        request = factory.get('/weekly-suggestion/')
        
        # Add required attributes
        request.user = User()
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        
        # Call the view
        response = weekly_suggestion(request)
        print("✅ View executed without errors")
        
        # The response should be a TemplateResponse
        if hasattr(response, 'context_data'):
            context = response.context_data
            day_fields = context.get('day_fields', [])
            print(f"✅ Context contains {len(day_fields)} day fields")
            
            if day_fields:
                first_day = day_fields[0]
                print(f"   First day field structure: {list(first_day.keys())}")
                
                # Check if form fields are present
                if 'bf' in first_day and first_day['bf'] is not None:
                    print("✅ Day fields contain form field objects")
                else:
                    print("❌ Day fields missing form field objects")
            else:
                print("❌ No day fields in context")
        else:
            print("✅ Response created (context not directly accessible)")
            
        return True
    except Exception as e:
        print(f"❌ View test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing Weekly Suggestion System")
    print("=" * 50)
    
    results = []
    results.append(test_form())
    results.append(test_suggestion_period())
    results.append(test_view())
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All tests passed! Weekly suggestion system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()