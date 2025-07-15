// Mock data for color analysis results
export const mockColorAnalysis = () => {
  // Simulate realistic color analysis results
  const skinTones = [
    "#F5DEB3", "#E8C5A0", "#D4A574", "#C99A6B", "#B8956A",
    "#A0825C", "#8B6F47", "#7A5F3D", "#654832", "#4D3319"
  ];
  
  const eyeColors = [
    "#87CEEB", "#4682B4", "#5F9EA0", "#2E8B57", "#228B22",
    "#8B4513", "#A0522D", "#CD853F", "#D2691E", "#8B4513"
  ];
  
  const lipColors = [
    "#FFB6C1", "#FF69B4", "#DC143C", "#B22222", "#8B0000",
    "#FFA0B4", "#FF91A4", "#FF1493", "#C71585", "#800080"
  ];
  
  const hairColors = [
    "#000000", "#2F1B14", "#3D2314", "#4E2A04", "#6A4C2A",
    "#8B4513", "#A0522D", "#CD853F", "#D2B48C", "#F5DEB3"
  ];
  
  return {
    skinTone: skinTones[Math.floor(Math.random() * skinTones.length)],
    eyeColor: eyeColors[Math.floor(Math.random() * eyeColors.length)],
    lipColor: lipColors[Math.floor(Math.random() * lipColors.length)],
    hairColor: hairColors[Math.floor(Math.random() * hairColors.length)],
    confidence: {
      skinTone: 0.85 + Math.random() * 0.15,
      eyeColor: 0.75 + Math.random() * 0.25,
      lipColor: 0.80 + Math.random() * 0.20,
      hairColor: 0.90 + Math.random() * 0.10
    },
    analysisMetadata: {
      totalImages: 3,
      processingTime: Math.floor(Math.random() * 3000) + 1000,
      algorithm: "K-means clustering with face detection",
      timestamp: new Date().toISOString()
    }
  };
};

// Mock face detection simulation
export const mockFaceDetection = () => {
  return {
    faceDetected: Math.random() > 0.3, // 70% chance of detection
    confidence: Math.random() * 0.4 + 0.6, // 60-100% confidence
    landmarks: {
      leftEye: { x: 120, y: 80 },
      rightEye: { x: 180, y: 80 },
      nose: { x: 150, y: 120 },
      mouth: { x: 150, y: 160 }
    }
  };
};

// Mock camera capabilities
export const mockCameraCapabilities = () => {
  return {
    video: true,
    audio: false,
    deviceId: "mock-camera-device",
    label: "Mock Camera",
    width: { ideal: 1280 },
    height: { ideal: 720 },
    facingMode: "user"
  };
};

// Helper function to validate hex colors
export const isValidHexColor = (hex) => {
  return /^#[0-9A-F]{6}$/i.test(hex);
};

// Convert hex to RGB
export const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
};

// Get color brightness (for contrast calculations)
export const getColorBrightness = (hex) => {
  const rgb = hexToRgb(hex);
  if (!rgb) return 0;
  return (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
};

// Get contrasting text color
export const getContrastColor = (hex) => {
  return getColorBrightness(hex) > 128 ? "#000000" : "#ffffff";
};