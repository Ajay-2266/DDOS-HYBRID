import React, { useEffect, useState } from "react";
import axios from "../api";

export default function History(){
  const [rows, setRows] = useState([]);

  useEffect(()=>{
    async function load(){
      try {
        const r = await axios.get("/analysis/all");
        setRows(r.data || []);
      } catch(err){
        console.error(err);
      }
    }
    load();
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Analysis History</h2>
      <table className="w-full text-left card">
        <thead>
          <tr className="border-b">
            <th className="p-2">ID</th>
            <th>Timestamp</th>
            <th>Total</th>
            <th>Normal</th>
            <th>Attack</th>
            <th>Accuracy</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id} className="border-b">
              <td className="p-2">{r.id}</td>
              <td>{new Date(r.timestamp).toLocaleString()}</td>
              <td>{r.totalRecords}</td>
              <td>{r.normalCount}</td>
              <td>{r.attackCount}</td>
              <td>{r.accuracy}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
