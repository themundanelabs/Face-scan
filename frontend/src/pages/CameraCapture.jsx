import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Camera, ArrowLeft, RotateCcw, Check, Palette } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import FaceOverlay from "@/components/FaceOverlay";
import ColorResults from "@/components/ColorResults";
import { mockColorAnalysis } from "@/utils/mockData";

const CameraCapture = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [capturedImages, setCapturedImages] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [colorResults, setColorResults] = useState(null);
  const [faceDetected, setFaceDetected] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  const steps = [
    {
      title: "Front View",
      instruction: "Look directly at the camera and align your face in the center",
      icon: "👤"
    },
    {
      title: "Left Profile",
      instruction: "Turn your head to the left and align your profile",
      icon: "👈"
    },
    {
      title: "Right Profile", 
      instruction: "Turn your head to the right and align your profile",
      icon: "👉"
    }
  ];

  useEffect(() => {
    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      });
      
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setCameraError(null);
      
      // Simulate face detection for mock
      setTimeout(() => setFaceDetected(true), 1000);
    } catch (error) {
      console.error("Camera access error:", error);
      setCameraError("Unable to access camera. Please ensure you have granted camera permissions.");
      toast({
        title: "Camera Error",
        description: "Unable to access camera. Please check your permissions.",
        variant: "destructive"
      });
    }
  };

  const captureImage = () => {
    if (!faceDetected) {
      toast({
        title: "Face Not Detected",
        description: "Please position your face within the guide before capturing.",
        variant: "destructive"
      });
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    const newImages = [...capturedImages, {
      step: currentStep,
      data: imageData,
      timestamp: new Date().toISOString()
    }];

    setCapturedImages(newImages);
    
    toast({
      title: `${steps[currentStep].title} Captured!`,
      description: `Step ${currentStep + 1} of 3 complete.`,
    });

    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
      // Simulate new face detection delay
      setFaceDetected(false);
      setTimeout(() => setFaceDetected(true), 1500);
    } else {
      analyzeImages(newImages);
    }
  };

  const analyzeImages = async (images) => {
    setIsAnalyzing(true);
    
    // Simulate analysis with mock data
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const results = mockColorAnalysis();
    setColorResults(results);
    setIsAnalyzing(false);
    setAnalysisComplete(true);
    
    toast({
      title: "Analysis Complete!",
      description: "Your facial feature colors have been extracted.",
    });
  };

  const resetCapture = () => {
    setCurrentStep(0);
    setCapturedImages([]);
    setIsAnalyzing(false);
    setAnalysisComplete(false);
    setColorResults(null);
    setFaceDetected(false);
    setTimeout(() => setFaceDetected(true), 1000);
  };

  const progress = ((currentStep) / steps.length) * 100;

  if (cameraError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle className="text-center text-red-600">Camera Access Required</CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-gray-600">{cameraError}</p>
            <div className="space-y-2">
              <Button onClick={startCamera} className="w-full">
                Try Again
              </Button>
              <Button onClick={() => navigate("/")} variant="outline" className="w-full">
                Go Back
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (analysisComplete && colorResults) {
    return <ColorResults results={colorResults} onReset={resetCapture} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button
            onClick={() => navigate("/")}
            variant="outline"
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Button>
          <div className="flex items-center gap-4">
            <Progress value={progress} className="w-32" />
            <span className="text-sm text-gray-600">
              Step {currentStep + 1} of {steps.length}
            </span>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Camera Section */}
          <div className="lg:col-span-2">
            <Card className="overflow-hidden shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Camera className="h-5 w-5" />
                  {steps[currentStep].title}
                </CardTitle>
                <p className="text-gray-600">{steps[currentStep].instruction}</p>
              </CardHeader>
              <CardContent className="p-0">
                <div className="relative bg-black aspect-video">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />
                  <FaceOverlay 
                    faceDetected={faceDetected}
                    step={currentStep}
                  />
                  <canvas
                    ref={canvasRef}
                    style={{ display: 'none' }}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Controls */}
            <div className="mt-6 flex justify-center gap-4">
              <Button
                onClick={captureImage}
                disabled={!faceDetected || isAnalyzing}
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-8 rounded-xl"
              >
                {isAnalyzing ? "Analyzing..." : "Capture Photo"}
              </Button>
              <Button
                onClick={resetCapture}
                variant="outline"
                className="py-3 px-8 rounded-xl"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset
              </Button>
            </div>
          </div>

          {/* Progress Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Progress</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {steps.map((step, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      index < currentStep ? 'bg-green-100 text-green-600' :
                      index === currentStep ? 'bg-blue-100 text-blue-600' :
                      'bg-gray-100 text-gray-400'
                    }`}>
                      {index < currentStep ? <Check className="h-4 w-4" /> : index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">{step.title}</div>
                      <div className="text-xs text-gray-500">{step.instruction}</div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Face Detection Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Detection Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    faceDetected ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className="text-sm">
                    {faceDetected ? 'Face Detected' : 'Position Your Face'}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Captured Images */}
            {capturedImages.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Captured Images</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {capturedImages.map((image, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {steps[image.step].title}
                        </Badge>
                        <Check className="h-4 w-4 text-green-500" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CameraCapture;