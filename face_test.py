#!/usr/bin/env python3
"""
Additional test to verify face detection works with actual face-like images
"""

import requests
import json
import base64
import time
from datetime import datetime
from PIL import Image, ImageDraw
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

def create_face_like_image():
    """Create a simple face-like image that might be detected by MediaPipe"""
    try:
        # Create a larger image with face-like features
        img = Image.new('RGB', (400, 400), (240, 220, 200))  # Skin tone background
        draw = ImageDraw.Draw(img)
        
        # Draw face outline (oval)
        draw.ellipse([50, 50, 350, 350], fill=(220, 200, 180), outline=(200, 180, 160))
        
        # Draw eyes
        draw.ellipse([120, 150, 160, 180], fill=(100, 80, 60))  # Left eye
        draw.ellipse([240, 150, 280, 180], fill=(100, 80, 60))  # Right eye
        
        # Draw nose
        draw.ellipse([190, 200, 210, 240], fill=(210, 190, 170))
        
        # Draw mouth
        draw.ellipse([170, 270, 230, 300], fill=(200, 100, 100))
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return img_base64
        
    except Exception as e:
        print(f"Error creating face-like image: {e}")
        return None

def test_with_face_like_image():
    """Test the API with a face-like image"""
    print("🧪 Testing with face-like image...")
    
    face_image = create_face_like_image()
    if not face_image:
        print("❌ Failed to create face-like image")
        return
    
    payload = {
        "images": [
            {
                "step": 0,
                "data": face_image,
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        "session_id": f"face_test_{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analysis/analyze-face",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("✅ Face detection successful!")
                if 'colors' in data:
                    colors = data['colors']
                    print(f"   Skin tone: {colors.get('skin_tone')}")
                    print(f"   Eye color: {colors.get('eye_color')}")
                    print(f"   Lip color: {colors.get('lip_color')}")
                    print(f"   Hair color: {colors.get('hair_color')}")
            else:
                print(f"❌ Face detection failed: {data.get('error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_face_like_image()