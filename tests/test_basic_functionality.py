#!/usr/bin/env python3
"""
Basic PropertyPilot functionality test without Unicode characters
Tests core functionality that should work in any environment
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_environment_setup():
    """Test basic environment setup"""
    print("Testing Environment Setup")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✓ Python version: {python_version.major}.{python_version.minor}")
        return True
    else:
        print(f"✗ Python version too old: {python_version.major}.{python_version.minor}")
        return False

def test_basic_imports():
    """Test basic Python imports"""
    print("\nTesting Basic Imports")
    print("=" * 50)
    
    try:
        import json
        import os
        import sys
        from datetime import datetime
        print("✓ Standard library imports working")
        
        # Test dotenv
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ dotenv import working")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\nTesting Environment Variables")
    print("=" * 50)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key and gemini_key != 'your_gemini_api_key_here':
        print("✓ GEMINI_API_KEY is set")
        gemini_ok = True
    else:
        print("✗ GEMINI_API_KEY not set or using placeholder")
        gemini_ok = False
    
    aws_region = os.getenv('AWS_REGION')
    if aws_region:
        print(f"✓ AWS_REGION is set: {aws_region}")
        aws_ok = True
    else:
        print("✗ AWS_REGION not set")
        aws_ok = False
    
    return gemini_ok and aws_ok

def test_file_structure():
    """Test that required files exist"""
    print("\nTesting File Structure")
    print("=" * 50)
    
    required_files = [
        'property_pilot_agents.py',
        'main.py',
        'automated_web_research.py',
        'requirements.txt',
        '.env',
        'Dockerfile.main'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            all_exist = False
    
    return all_exist

def test_basic_calculations():
    """Test basic calculation functions"""
    print("\nTesting Basic Calculations")
    print("=" * 50)
    
    try:
        # Test ROI calculation
        purchase_price = 400000
        annual_rental_income = 48000
        annual_expenses = 12000
        
        net_income = annual_rental_income - annual_expenses
        roi = (net_income / purchase_price) * 100
        
        print(f"✓ ROI Calculation: {roi:.2f}%")
        
        # Test cash flow calculation
        monthly_rent = 4000
        monthly_expenses = 1000
        monthly_cash_flow = monthly_rent - monthly_expenses
        
        print(f"✓ Monthly Cash Flow: ${monthly_cash_flow:,}")
        
        return True
    except Exception as e:
        print(f"✗ Calculation failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("PropertyPilot Basic Functionality Test")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Basic Imports", test_basic_imports),
        ("Environment Variables", test_environment_variables),
        ("File Structure", test_file_structure),
        ("Basic Calculations", test_basic_calculations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n[PASS] {test_name}")
            else:
                print(f"\n[FAIL] {test_name}")
        except Exception as e:
            print(f"\n[ERROR] {test_name}: {e}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed == total:
        print("\nAll basic tests passed! System is ready for advanced testing.")
        return True
    else:
        print(f"\n{total-passed} test(s) failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)