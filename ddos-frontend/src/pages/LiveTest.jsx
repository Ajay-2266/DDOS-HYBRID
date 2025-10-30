import React, { useState } from "react";
import axios from "../api";

export default function LiveTest(){
  const [form, setForm] = useState({
    packet_count: "", avg_pkt_size: "", flow_duration: "", src_port: "", dst_port: ""
  });
  const [res, setRes] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const payload = { ...form };
      const r = await axios.post("/analysis/test", payload);
      setRes(r.data);
    } catch(err){
      console.error(err);
      alert("Test failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <div className="card p-4">
        <h2 className="text-lg font-bold">Live Test - Single Sample</h2>
        <form className="mt-3 grid grid-cols-2 gap-2" onSubmit={submit}>
          <input className="p-2 card" placeholder="packet_count" value={form.packet_count} onChange={(e)=>setForm({...form, packet_count:e.target.value})}/>
          <input className="p-2 card" placeholder="avg_pkt_size" value={form.avg_pkt_size} onChange={(e)=>setForm({...form, avg_pkt_size:e.target.value})}/>
          <input className="p-2 card" placeholder="flow_duration" value={form.flow_duration} onChange={(e)=>setForm({...form, flow_duration:e.target.value})}/>
          <input className="p-2 card" placeholder="src_port" value={form.src_port} onChange={(e)=>setForm({...form, src_port:e.target.value})}/>
          <input className="col-span-2 p-2 card" placeholder="dst_port" value={form.dst_port} onChange={(e)=>setForm({...form, dst_port:e.target.value})}/>
          <div className="col-span-2">
            <button className="px-4 py-2 rounded bg-neon text-black" type="submit">{loading ? "Testing..." : "Test Sample"}</button>
          </div>
        </form>
      </div>

      {res && (
        <div className="card p-4">
          <h3 className="font-bold">Prediction</h3>
          <pre className="mt-2 text-sm">{JSON.stringify(res, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
