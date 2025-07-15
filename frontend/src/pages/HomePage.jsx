import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Camera, Palette, Eye, Smile } from "lucide-react";

const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Camera className="h-8 w-8 text-blue-500" />,
      title: "Smart Face Detection",
      description: "Advanced facial recognition guides you through perfect positioning"
    },
    {
      icon: <Palette className="h-8 w-8 text-purple-500" />,
      title: "Color Analysis",
      description: "Extract dominant colors from skin, eyes, lips, and hair using AI"
    },
    {
      icon: <Eye className="h-8 w-8 text-green-500" />,
      title: "Multi-Angle Capture",
      description: "Front, left, and right profile captures for comprehensive analysis"
    },
    {
      icon: <Smile className="h-8 w-8 text-pink-500" />,
      title: "Privacy First",
      description: "All processing happens in your browser - no data stored"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center max-w-4xl mx-auto mb-16">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mb-6">
              <Camera className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-6">
              Face Color Analyzer
            </h1>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Discover your unique color palette with our AI-powered facial feature analysis. 
              Capture three angles of your face and get precise HEX color codes for your skin tone, 
              eye color, lip color, and hair color.
            </p>
          </div>
          
          <Button 
            onClick={() => navigate("/capture")}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-4 px-8 rounded-xl text-lg transform transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl"
          >
            Start Color Analysis
          </Button>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 bg-white/80 backdrop-blur-sm">
              <CardHeader className="text-center pb-4">
                <div className="flex justify-center mb-4">
                  {feature.icon}
                </div>
                <CardTitle className="text-lg font-semibold text-gray-800">
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <CardDescription className="text-center text-gray-600">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* How It Works Section */}
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-800 mb-12">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Position Your Face</h3>
              <p className="text-gray-600">Align your face within the dotted guide for optimal capture</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Capture Three Angles</h3>
              <p className="text-gray-600">Take front, left profile, and right profile photos</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Get Your Colors</h3>
              <p className="text-gray-600">Receive precise HEX codes for all your facial features</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;