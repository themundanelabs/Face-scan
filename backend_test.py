#!/usr/bin/env python3
"""
Backend API Testing Suite for Face Color Analyzer
Tests all backend endpoints with comprehensive test cases
"""

import requests
import json
import base64
import time
from datetime import datetime
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.results = {
            'health_check': {'passed': False, 'details': ''},
            'analyze_face': {'passed': False, 'details': ''},
            'stats': {'passed': False, 'details': ''},
            'history': {'passed': False, 'details': ''},
            'error_handling': {'passed': False, 'details': ''}
        }
        self.session_id = f"test_session_{int(time.time())}"
        
    def create_test_image_base64(self, color=(255, 255, 255), size=(200, 200)):
        """Create a simple test image and return as base64"""
        try:
            # Create a simple colored image
            img = Image.new('RGB', size, color)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            return f"data:image/jpeg;base64,{img_base64}"
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None

    def test_health_endpoint(self):
        """Test GET /api/health endpoint"""
        print("\n=== Testing Health Endpoint ===")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ['status', 'timestamp', 'service']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields and data.get('status') == 'healthy':
                    self.results['health_check']['passed'] = True
                    self.results['health_check']['details'] = f"✅ Health check passed. Response: {data}"
                    print("✅ Health endpoint working correctly")
                else:
                    self.results['health_check']['details'] = f"❌ Missing fields: {missing_fields} or status not healthy"
                    print(f"❌ Health endpoint issues: {self.results['health_check']['details']}")
            else:
                self.results['health_check']['details'] = f"❌ HTTP {response.status_code}: {response.text}"
                print(f"❌ Health endpoint failed: {self.results['health_check']['details']}")
                
        except Exception as e:
            self.results['health_check']['details'] = f"❌ Exception: {str(e)}"
            print(f"❌ Health endpoint error: {e}")

    def test_analyze_face_valid_single_image(self):
        """Test POST /api/analysis/analyze-face with valid single image"""
        print("\n=== Testing Face Analysis - Single Valid Image ===")
        try:
            # Create test image (Note: Simple colored rectangles won't have faces)
            test_image = self.create_test_image_base64((200, 150, 100))  # Skin-like color
            
            if not test_image:
                self.results['analyze_face']['details'] += "❌ Failed to create test image. "
                return False
            
            payload = {
                "images": [
                    {
                        "step": 0,
                        "data": test_image.split(',')[1],  # Remove data URL prefix
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ],
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{API_BASE_URL}/analysis/analyze-face",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'analysis_id', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # For images without faces, success should be false but structure should be correct
                    if not data.get('success'):
                        # Check error handling structure
                        if 'error' in data and 'metadata' in data:
                            metadata = data['metadata']
                            if ('total_images' in metadata and 
                                'images_analyzed' in metadata and 
                                'processing_time_ms' in metadata):
                                self.results['analyze_face']['details'] += "✅ Single image analysis structure correct (no face detected as expected). "
                                print("✅ Single image analysis API structure working correctly")
                                return True
                            else:
                                self.results['analyze_face']['details'] += "❌ Missing metadata fields in error response. "
                        else:
                            self.results['analyze_face']['details'] += "❌ Missing error or metadata in failed response. "
                    else:
                        # If success is true, check full structure
                        if 'colors' in data and data['colors']:
                            color_fields = ['skin_tone', 'eye_color', 'lip_color', 'hair_color']
                            missing_color_fields = [field for field in color_fields if field not in data['colors']]
                            
                            if not missing_color_fields and 'metadata' in data:
                                self.results['analyze_face']['details'] += "✅ Single image analysis passed with face detection. "
                                print("✅ Single image analysis working correctly with face detection")
                                return True
                            else:
                                self.results['analyze_face']['details'] += f"❌ Missing color fields: {missing_color_fields}. "
                        else:
                            self.results['analyze_face']['details'] += "❌ Success=true but missing colors. "
                else:
                    self.results['analyze_face']['details'] += f"❌ Missing required fields: {missing_fields}. "
            else:
                self.results['analyze_face']['details'] += f"❌ HTTP {response.status_code}: {response.text}. "
                print(f"❌ Single image analysis failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.results['analyze_face']['details'] += f"❌ Exception in single image test: {str(e)}. "
            print(f"❌ Single image analysis error: {e}")
        
        return False

    def test_analyze_face_multiple_images(self):
        """Test POST /api/analysis/analyze-face with multiple images"""
        print("\n=== Testing Face Analysis - Multiple Images ===")
        try:
            # Create multiple test images
            images = []
            colors = [(200, 150, 100), (180, 140, 90), (220, 160, 110)]  # Different skin tones
            
            for i, color in enumerate(colors):
                test_image = self.create_test_image_base64(color)
                if test_image:
                    images.append({
                        "step": i,
                        "data": test_image.split(',')[1],
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            if len(images) != 3:
                self.results['analyze_face']['details'] += "❌ Failed to create multiple test images. "
                return False
            
            payload = {
                "images": images,
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{API_BASE_URL}/analysis/analyze-face",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic structure regardless of success
                required_fields = ['success', 'analysis_id', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields and 'metadata' in data:
                    metadata = data['metadata']
                    if metadata.get('total_images') == 3:
                        # API structure is correct
                        if data.get('success'):
                            self.results['analyze_face']['details'] += "✅ Multiple images analysis passed with face detection. "
                            print("✅ Multiple images analysis working correctly with face detection")
                        else:
                            self.results['analyze_face']['details'] += "✅ Multiple images analysis structure correct (no faces detected as expected). "
                            print("✅ Multiple images analysis API structure working correctly")
                        return True
                    else:
                        self.results['analyze_face']['details'] += f"❌ Expected 3 images, got {metadata.get('total_images')}. "
                else:
                    self.results['analyze_face']['details'] += f"❌ Missing required fields: {missing_fields} or metadata. "
            else:
                self.results['analyze_face']['details'] += f"❌ Multiple images HTTP {response.status_code}. "
                
        except Exception as e:
            self.results['analyze_face']['details'] += f"❌ Exception in multiple images test: {str(e)}. "
            print(f"❌ Multiple images analysis error: {e}")
        
        return False

    def test_analyze_face_invalid_data(self):
        """Test POST /api/analysis/analyze-face with invalid data"""
        print("\n=== Testing Face Analysis - Invalid Data ===")
        
        test_cases = [
            # Invalid base64 data
            {
                "name": "Invalid base64",
                "payload": {
                    "images": [
                        {
                            "step": 0,
                            "data": "invalid_base64_data",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    ],
                    "session_id": self.session_id
                }
            },
            # Empty images array
            {
                "name": "Empty images",
                "payload": {
                    "images": [],
                    "session_id": self.session_id
                }
            },
            # Missing required fields
            {
                "name": "Missing images field",
                "payload": {
                    "session_id": self.session_id
                }
            }
        ]
        
        passed_tests = 0
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/analysis/analyze-face",
                    json=test_case["payload"],
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                # Should either return 400/422 or success=false
                if response.status_code in [400, 422]:
                    passed_tests += 1
                    print(f"✅ {test_case['name']}: Correctly rejected with HTTP {response.status_code}")
                elif response.status_code == 200:
                    data = response.json()
                    if not data.get('success'):
                        passed_tests += 1
                        print(f"✅ {test_case['name']}: Correctly returned success=false")
                    else:
                        print(f"❌ {test_case['name']}: Should have failed but returned success=true")
                else:
                    print(f"❌ {test_case['name']}: Unexpected status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {test_case['name']}: Exception {e}")
        
        if passed_tests == len(test_cases):
            self.results['error_handling']['details'] += "✅ Invalid data handling passed. "
            return True
        else:
            self.results['error_handling']['details'] += f"❌ Invalid data handling: {passed_tests}/{len(test_cases)} passed. "
            return False

    def test_stats_endpoint(self):
        """Test GET /api/analysis/stats endpoint"""
        print("\n=== Testing Stats Endpoint ===")
        try:
            response = requests.get(f"{API_BASE_URL}/analysis/stats", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ['total_analyses', 'successful_analyses', 'failed_analyses', 'success_rate']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check data types
                    if (isinstance(data['total_analyses'], int) and 
                        isinstance(data['successful_analyses'], int) and
                        isinstance(data['failed_analyses'], int) and
                        isinstance(data['success_rate'], (int, float))):
                        
                        self.results['stats']['passed'] = True
                        self.results['stats']['details'] = f"✅ Stats endpoint passed. Total analyses: {data['total_analyses']}"
                        print("✅ Stats endpoint working correctly")
                    else:
                        self.results['stats']['details'] = "❌ Stats endpoint: Invalid data types"
                        print("❌ Stats endpoint: Invalid data types")
                else:
                    self.results['stats']['details'] = f"❌ Stats endpoint missing fields: {missing_fields}"
                    print(f"❌ Stats endpoint missing fields: {missing_fields}")
            else:
                self.results['stats']['details'] = f"❌ Stats endpoint HTTP {response.status_code}: {response.text}"
                print(f"❌ Stats endpoint failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.results['stats']['details'] = f"❌ Stats endpoint exception: {str(e)}"
            print(f"❌ Stats endpoint error: {e}")

    def test_history_endpoint(self):
        """Test GET /api/analysis/history/{session_id} endpoint"""
        print("\n=== Testing History Endpoint ===")
        try:
            response = requests.get(f"{API_BASE_URL}/analysis/history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ['session_id', 'analyses', 'count']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    if (data['session_id'] == self.session_id and 
                        isinstance(data['analyses'], list) and
                        isinstance(data['count'], int)):
                        
                        self.results['history']['passed'] = True
                        self.results['history']['details'] = f"✅ History endpoint passed. Found {data['count']} analyses"
                        print("✅ History endpoint working correctly")
                    else:
                        self.results['history']['details'] = "❌ History endpoint: Invalid response structure"
                        print("❌ History endpoint: Invalid response structure")
                else:
                    self.results['history']['details'] = f"❌ History endpoint missing fields: {missing_fields}"
                    print(f"❌ History endpoint missing fields: {missing_fields}")
            else:
                self.results['history']['details'] = f"❌ History endpoint HTTP {response.status_code}: {response.text}"
                print(f"❌ History endpoint failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.results['history']['details'] = f"❌ History endpoint exception: {str(e)}"
            print(f"❌ History endpoint error: {e}")

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base URL: {API_BASE_URL}")
        print(f"Session ID: {self.session_id}")
        
        # Test health endpoint first
        self.test_health_endpoint()
        
        # Test face analysis endpoints
        single_image_passed = self.test_analyze_face_valid_single_image()
        multiple_images_passed = self.test_analyze_face_multiple_images()
        
        # Set overall analyze_face result
        if single_image_passed or multiple_images_passed:
            self.results['analyze_face']['passed'] = True
        
        # Test error handling
        error_handling_passed = self.test_analyze_face_invalid_data()
        if error_handling_passed:
            self.results['error_handling']['passed'] = True
        
        self.test_stats_endpoint()
        
        # Test history endpoint
        self.test_history_endpoint()
        
        # Print summary
        self.print_summary()
        
        return self.results

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("🧪 BACKEND API TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result['passed'])
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"{test_name.upper():<20} {status}")
            if result['details']:
                print(f"{'':>22} {result['details']}")
        
        print("-" * 60)
        print(f"OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL BACKEND TESTS PASSED!")
        else:
            print("⚠️  SOME BACKEND TESTS FAILED")
        
        print("="*60)

def main():
    """Main test execution"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    all_passed = all(result['passed'] for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())