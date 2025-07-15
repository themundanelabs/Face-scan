import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import CameraCapture from "./pages/CameraCapture";
import { Toaster } from "@/components/ui/toaster";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/capture" element={<CameraCapture />} />
        </Routes>
        <Toaster />
      </BrowserRouter>
    </div>
  );
}

export default App;