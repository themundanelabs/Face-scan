import cv2
import numpy as np
import mediapipe as mp
from sklearn.cluster import KMeans
from PIL import Image
import base64
import io
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class FaceAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Key landmark indices for different facial features
        self.SKIN_LANDMARKS = [
            # Forehead and cheek area landmarks
            10, 151, 9, 10, 151, 234, 127, 162, 21, 54, 103, 67, 109, 10, 151,
            # Additional cheek landmarks
            116, 117, 118, 119, 120, 121, 126, 142, 36, 205, 206, 207, 213, 192, 147, 90, 180
        ]
        
        self.EYE_LANDMARKS = {
            'left_eye': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
            'right_eye': [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        }
        
        self.LIP_LANDMARKS = [
            # Outer lip landmarks
            61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318,
            # Inner lip landmarks
            78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415
        ]
        
        self.HAIR_LANDMARKS = [
            # Top of head and forehead area
            10, 151, 9, 10, 151, 234, 127, 162, 21, 54, 103, 67, 109,
            # Forehead and hairline
            9, 10, 151, 234, 127, 162, 21, 54, 103, 67, 109, 10, 151
        ]

    def base64_to_image(self, base64_string: str) -> np.ndarray:
        """Convert base64 string to OpenCV image"""
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            return image_bgr
            
        except Exception as e:
            logger.error(f"Error converting base64 to image: {e}")
            raise ValueError(f"Invalid image data: {e}")

    def extract_face_landmarks(self, image: np.ndarray) -> Optional[List]:
        """Extract facial landmarks from image"""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.face_mesh.process(rgb_image)
            
            if results.multi_face_landmarks:
                return results.multi_face_landmarks[0].landmark
            return None
            
        except Exception as e:
            logger.error(f"Error extracting face landmarks: {e}")
            return None

    def get_region_pixels(self, image: np.ndarray, landmarks: List, 
                         landmark_indices: List[int]) -> np.ndarray:
        """Extract pixels from specific facial region"""
        try:
            height, width = image.shape[:2]
            
            # Convert normalized landmarks to pixel coordinates
            region_points = []
            for idx in landmark_indices:
                if idx < len(landmarks):
                    landmark = landmarks[idx]
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    region_points.append([x, y])
            
            if not region_points:
                return np.array([])
            
            # Create mask for the region
            mask = np.zeros((height, width), dtype=np.uint8)
            pts = np.array(region_points, dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)
            
            # Extract pixels from the region
            region_pixels = image[mask > 0]
            
            return region_pixels
            
        except Exception as e:
            logger.error(f"Error extracting region pixels: {e}")
            return np.array([])

    def extract_dominant_color(self, pixels: np.ndarray, n_colors: int = 3) -> str:
        """Extract dominant color using K-means clustering"""
        try:
            if len(pixels) == 0:
                return "#000000"
            
            # Reshape pixels for K-means
            pixels_reshaped = pixels.reshape(-1, 3)
            
            # Remove very dark and very light pixels (shadows/highlights)
            brightness = np.sum(pixels_reshaped, axis=1)
            valid_pixels = pixels_reshaped[
                (brightness > 50) & (brightness < 650)
            ]
            
            if len(valid_pixels) < 10:
                valid_pixels = pixels_reshaped
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=min(n_colors, len(valid_pixels)), 
                          random_state=42, n_init=10)
            kmeans.fit(valid_pixels)
            
            # Get the most dominant color (largest cluster)
            labels = kmeans.labels_
            (values, counts) = np.unique(labels, return_counts=True)
            dominant_color_idx = values[np.argmax(counts)]
            dominant_color = kmeans.cluster_centers_[dominant_color_idx]
            
            # Convert BGR to RGB and then to HEX
            r, g, b = int(dominant_color[2]), int(dominant_color[1]), int(dominant_color[0])
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            return hex_color
            
        except Exception as e:
            logger.error(f"Error extracting dominant color: {e}")
            return "#000000"

    def analyze_single_image(self, image: np.ndarray) -> Dict:
        """Analyze a single image for facial features"""
        try:
            # Extract landmarks
            landmarks = self.extract_face_landmarks(image)
            
            if not landmarks:
                return {
                    'face_detected': False,
                    'error': 'No face detected in image'
                }
            
            results = {'face_detected': True}
            
            # Extract skin color
            skin_pixels = self.get_region_pixels(image, landmarks, self.SKIN_LANDMARKS)
            results['skin_color'] = self.extract_dominant_color(skin_pixels)
            
            # Extract eye colors
            left_eye_pixels = self.get_region_pixels(image, landmarks, self.EYE_LANDMARKS['left_eye'])
            right_eye_pixels = self.get_region_pixels(image, landmarks, self.EYE_LANDMARKS['right_eye'])
            
            # Combine eye pixels
            eye_pixels = np.vstack([left_eye_pixels, right_eye_pixels]) if len(left_eye_pixels) > 0 and len(right_eye_pixels) > 0 else np.array([])
            results['eye_color'] = self.extract_dominant_color(eye_pixels)
            
            # Extract lip color
            lip_pixels = self.get_region_pixels(image, landmarks, self.LIP_LANDMARKS)
            results['lip_color'] = self.extract_dominant_color(lip_pixels)
            
            # Extract hair color (from forehead/hairline area)
            hair_pixels = self.get_region_pixels(image, landmarks, self.HAIR_LANDMARKS)
            results['hair_color'] = self.extract_dominant_color(hair_pixels)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing single image: {e}")
            return {
                'face_detected': False,
                'error': f'Analysis failed: {str(e)}'
            }

    def analyze_multiple_images(self, images: List[str]) -> Dict:
        """Analyze multiple images and combine results"""
        try:
            all_results = []
            
            for i, base64_image in enumerate(images):
                logger.info(f"Analyzing image {i+1}/{len(images)}")
                
                # Convert base64 to image
                image = self.base64_to_image(base64_image)
                
                # Analyze image
                result = self.analyze_single_image(image)
                
                if result['face_detected']:
                    all_results.append(result)
                else:
                    logger.warning(f"No face detected in image {i+1}")
            
            if not all_results:
                return {
                    'success': False,
                    'error': 'No faces detected in any of the provided images'
                }
            
            # Combine results from all images
            combined_results = self.combine_analysis_results(all_results)
            
            return {
                'success': True,
                'results': combined_results,
                'images_analyzed': len(all_results),
                'total_images': len(images)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing multiple images: {e}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }

    def combine_analysis_results(self, results: List[Dict]) -> Dict:
        """Combine analysis results from multiple images"""
        try:
            # Collect all colors for each feature
            skin_colors = []
            eye_colors = []
            lip_colors = []
            hair_colors = []
            
            for result in results:
                if result.get('skin_color'):
                    skin_colors.append(result['skin_color'])
                if result.get('eye_color'):
                    eye_colors.append(result['eye_color'])
                if result.get('lip_color'):
                    lip_colors.append(result['lip_color'])
                if result.get('hair_color'):
                    hair_colors.append(result['hair_color'])
            
            # Get most common color for each feature
            combined = {
                'skin_tone': self.get_most_common_color(skin_colors) if skin_colors else "#F5DEB3",
                'eye_color': self.get_most_common_color(eye_colors) if eye_colors else "#8B4513",
                'lip_color': self.get_most_common_color(lip_colors) if lip_colors else "#FFB6C1",
                'hair_color': self.get_most_common_color(hair_colors) if hair_colors else "#4E2A04"
            }
            
            return combined
            
        except Exception as e:
            logger.error(f"Error combining analysis results: {e}")
            return {
                'skin_tone': "#F5DEB3",
                'eye_color': "#8B4513", 
                'lip_color': "#FFB6C1",
                'hair_color': "#4E2A04"
            }

    def get_most_common_color(self, colors: List[str]) -> str:
        """Get the most common color from a list"""
        if not colors:
            return "#000000"
        
        # Simple approach: return the first color
        # In a more sophisticated implementation, you could:
        # 1. Convert to RGB and average
        # 2. Use color distance metrics
        # 3. Apply more advanced color theory
        
        return colors[0] if colors else "#000000"

    def validate_hex_color(self, hex_color: str) -> bool:
        """Validate if string is a valid hex color"""
        try:
            if not hex_color.startswith('#') or len(hex_color) != 7:
                return False
            int(hex_color[1:], 16)
            return True
        except ValueError:
            return False