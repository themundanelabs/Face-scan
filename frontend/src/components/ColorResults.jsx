import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, Copy, Download, RotateCcw, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const ColorResults = ({ results, onReset }) => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [copiedColors, setCopiedColors] = useState(new Set());

  const copyToClipboard = async (color, label) => {
    try {
      await navigator.clipboard.writeText(color);
      setCopiedColors(prev => new Set([...prev, color]));
      toast({
        title: "Copied!",
        description: `${label} color ${color} copied to clipboard.`,
      });
      
      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopiedColors(prev => {
          const newSet = new Set(prev);
          newSet.delete(color);
          return newSet;
        });
      }, 2000);
    } catch (error) {
      toast({
        title: "Copy Failed",
        description: "Unable to copy to clipboard.",
        variant: "destructive"
      });
    }
  };

  const downloadPalette = () => {
    const paletteData = {
      skinTone: results.skinTone,
      eyeColor: results.eyeColor,
      lipColor: results.lipColor,
      hairColor: results.hairColor,
      generatedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(paletteData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'color-palette.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Downloaded!",
      description: "Your color palette has been downloaded.",
    });
  };

  const ColorCard = ({ label, color, icon, description }) => (
    <Card className="transition-all duration-300 hover:shadow-lg transform hover:-translate-y-1">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-3">
          <div className="text-2xl">{icon}</div>
          <div>
            <CardTitle className="text-lg">{label}</CardTitle>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div 
              className="w-16 h-16 rounded-lg border-2 border-gray-200 shadow-inner"
              style={{ backgroundColor: color }}
            />
            <div className="flex-1">
              <div className="font-mono text-lg font-semibold">{color}</div>
              <Button
                onClick={() => copyToClipboard(color, label)}
                variant="outline"
                size="sm"
                className="mt-2"
              >
                {copiedColors.has(color) ? (
                  <Check className="h-4 w-4 mr-1" />
                ) : (
                  <Copy className="h-4 w-4 mr-1" />
                )}
                {copiedColors.has(color) ? 'Copied' : 'Copy'}
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

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
            <Button
              onClick={onReset}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RotateCcw className="h-4 w-4" />
              Capture Again
            </Button>
            <Button
              onClick={downloadPalette}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Download Palette
            </Button>
          </div>
        </div>

        {/* Results Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full mb-4">
            <Check className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Your Color Palette
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Here are your personalized HEX color codes extracted from your facial features. 
            Click any color to copy it to your clipboard.
          </p>
        </div>

        {/* Color Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <ColorCard
            label="Skin Tone"
            color={results.skinTone}
            icon="🏽"
            description="Dominant skin color from cheek area"
          />
          <ColorCard
            label="Eye Color"
            color={results.eyeColor}
            icon="👁️"
            description="Dominant iris color"
          />
          <ColorCard
            label="Lip Color"
            color={results.lipColor}
            icon="💋"
            description="Natural lip color"
          />
          <ColorCard
            label="Hair Color"
            color={results.hairColor}
            icon="💇"
            description="Dominant hair color"
          />
        </div>

        {/* Palette Summary */}
        <Card className="max-w-4xl mx-auto">
          <CardHeader>
            <CardTitle className="text-xl text-center">Complete Color Palette</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap justify-center gap-4 mb-6">
              {[
                { color: results.skinTone, label: "Skin" },
                { color: results.eyeColor, label: "Eyes" },
                { color: results.lipColor, label: "Lips" },
                { color: results.hairColor, label: "Hair" }
              ].map((item, index) => (
                <div key={index} className="text-center">
                  <div 
                    className="w-20 h-20 rounded-full border-4 border-white shadow-lg mx-auto mb-2"
                    style={{ backgroundColor: item.color }}
                  />
                  <Badge variant="outline" className="text-xs">
                    {item.label}
                  </Badge>
                </div>
              ))}
            </div>
            
            <Separator className="my-6" />
            
            <div className="text-center space-y-4">
              <p className="text-gray-600">
                Your unique color palette has been generated using advanced facial recognition 
                and color analysis algorithms. These colors represent your natural features 
                and can be used for makeup matching, fashion coordination, or design inspiration.
              </p>
              
              <div className="flex justify-center gap-4 flex-wrap">
                <Badge variant="secondary">Privacy Protected</Badge>
                <Badge variant="secondary">AI-Powered Analysis</Badge>
                <Badge variant="secondary">Precise HEX Colors</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ColorResults;