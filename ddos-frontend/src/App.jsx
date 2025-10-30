import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import LiveTest from "./pages/LiveTest";
import History from "./pages/History";

export default function App(){
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="p-6">
        <Routes>
          <Route path="/" element={<Dashboard/>} />
          <Route path="/upload" element={<Upload/>} />
          <Route path="/live" element={<LiveTest/>} />
          <Route path="/history" element={<History/>} />
        </Routes>
      </main>
    </div>
  );
}
