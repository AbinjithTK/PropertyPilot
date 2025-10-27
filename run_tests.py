#!/usr/bin/env python3
"""
PropertyPilot Test Suite Runner
Comprehensive testing for PropertyPilot with Google Gemini integration
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PropertyPilotTestRunner:
    """Comprehensive test runner for PropertyPilot"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    def run_test_file(self, test_file, description):
        """Run a specific test file and capture results"""
        print(f"\n🧪 Running {description}")
        print("=" * 60)
        
        try:
            start_time = time.time()
            # Set environment variables for proper encoding and Python path
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONPATH'] = os.getcwd()
            
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True, timeout=300, env=env)
            end_time = time.time()
            
            duration = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ {description} - PASSED ({duration:.1f}s)")
                self.test_results[test_file] = {
                    'status': 'PASSED',
                    'duration': duration,
                    'output': result.stdout
                }
                return True
            else:
                print(f"❌ {description} - FAILED ({duration:.1f}s)")
                print(f"Error: {result.stderr}")
                self.test_results[test_file] = {
                    'status': 'FAILED',
                    'duration': duration,
                    'error': result.stderr,
                    'output': result.stdout
                }
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT (>300s)")
            self.test_results[test_file] = {
                'status': 'TIMEOUT',
                'duration': 300,
                'error': 'Test timed out after 300 seconds'
            }
            return False
        except Exception as e:
            print(f"💥 {description} - ERROR: {e}")
            self.test_results[test_file] = {
                'status': 'ERROR',
                'duration': 0,
                'error': str(e)
            }
            return False
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking Prerequisites")
        print("=" * 60)
        
        # Check environment variables
        required_vars = ['GEMINI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        else:
            print("✅ Environment variables configured")
        
        # Check Python dependencies
        try:
            import strands
            import google.genai
            print("✅ Required Python packages available")
        except ImportError as e:
            print(f"❌ Missing Python packages: {e}")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all PropertyPilot tests"""
        print("🏠 PropertyPilot Comprehensive Test Suite")
        print("=" * 60)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix the issues above.")
            return False
        
        # Define test suite
        tests = [
            ("tests/test_gemini_integration.py", "Gemini API Integration"),
            ("tests/test_strands_gemini.py", "Strands Gemini Integration"),
            ("tests/test_tools_only.py", "PropertyPilot Tools"),
            ("tests/test_agents_functionality.py", "PropertyPilot Agents"),
            ("tests/test_zillow_integration.py", "Zillow API Integration"),
            ("tests/test_core_functionality.py", "Core Functionality"),
            ("tests/test_automated_research.py", "Automated Research"),
            ("tests/test_local_service.py", "Local Service"),
            ("tests/test_aws_setup.py", "AWS Setup"),
            ("tests/test_agentcore_benefits.py", "AgentCore Benefits")
        ]
        
        # Run tests
        passed_tests = 0
        total_tests = 0
        
        for test_file, description in tests:
            if os.path.exists(test_file):
                total_tests += 1
                if self.run_test_file(test_file, description):
                    passed_tests += 1
            else:
                print(f"⚠️ Test file not found: {test_file}")
        
        # Generate summary
        self.generate_summary(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def generate_summary(self, passed_tests, total_tests):
        """Generate test summary report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY REPORT")
        print("=" * 60)
        
        print(f"📊 Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}%)")
        print(f"⏱️ Total Duration: {total_duration:.1f} seconds")
        print(f"🕐 Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📋 Detailed Results:")
        for test_file, result in self.test_results.items():
            status_icon = {
                'PASSED': '✅',
                'FAILED': '❌', 
                'TIMEOUT': '⏰',
                'ERROR': '💥'
            }.get(result['status'], '❓')
            
            print(f"   {status_icon} {test_file}: {result['status']} ({result['duration']:.1f}s)")
            
            if result['status'] != 'PASSED' and 'error' in result:
                print(f"      Error: {result['error'][:100]}...")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            import json
            json.dump({
                'summary': {
                    'passed': passed_tests,
                    'total': total_tests,
                    'success_rate': passed_tests/total_tests*100,
                    'duration': total_duration,
                    'start_time': self.start_time.isoformat(),
                    'end_time': end_time.isoformat()
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! PropertyPilot is ready for deployment.")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Please review the issues above.")

def main():
    """Main test runner function"""
    runner = PropertyPilotTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🚀 PropertyPilot is ready for AgentCore deployment!")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please fix the issues before deployment.")
        exit(1)

if __name__ == "__main__":
    main()