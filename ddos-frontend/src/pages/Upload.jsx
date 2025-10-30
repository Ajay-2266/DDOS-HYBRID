import React, { useState } from "react";
import axios from "../api";

export default function Upload(){
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if(!file) return alert("Select a CSV file");
    try {
      setLoading(true);
      const form = new FormData();
      form.append("file", file);
      // POST to Spring Boot which forwards to Flask
      const res = await axios.post("/analysis/upload", form, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResult(res.data);
    } catch(err){
      console.error(err);
      alert("Upload failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="card p-4">
        <h2 className="text-lg font-bold">Upload Network Traffic CSV</h2>
        <form onSubmit={submit} className="mt-4 space-y-2">
          <input type="file" accept=".csv" onChange={(e)=>setFile(e.target.files[0])} className="w-full" />
          <button type="submit" className="mt-2 px-4 py-2 rounded bg-neon text-black font-semibold">
            {loading ? "Processing..." : "Upload & Analyze"}
          </button>
        </form>
      </div>

      {result && (
        <div className="card p-4">
          <h3 className="font-bold">Analysis Result</h3>
          <pre className="text-sm mt-2 text-neon/80">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
