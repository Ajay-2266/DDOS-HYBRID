import React, { useEffect, useState } from "react";
import axios from "../api";
import StatCard from "../components/StatCard";
import ChartCard from "../components/ChartCard";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from "recharts";

const COLORS = ["#00ff9f", "#ff5252", "#ffd166", "#7dd3fc"];

export default function Dashboard(){
  const [stats, setStats] = useState({
    totalRecords: 0,
    normal: 0,
    attack: 0,
    avgConfidence: 0,
    accuracy: 0,
    attackTypes: {}
  });
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    async function fetchStats(){
      try {
        setLoading(true);
        const res = await axios.get("/analysis/stats");
        setStats(res.data || {});
      } catch(err){
        console.error(err);
      } finally { setLoading(false); }
    }
    fetchStats();
  }, []);

  const pieData = [
    { name: "Normal", value: stats.normal || 0 },
    { name: "Attack", value: stats.attack || 0 }
  ];

  const barData = Object.entries(stats.attackTypes || {}).map(([k,v]) => ({ name: k, value: v }));

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2 grid grid-cols-2 gap-4">
        <StatCard title="Total Records" value={stats.totalRecords} />
        <StatCard title="Accuracy (%)" value={(stats.accuracy || 0).toFixed(2)} sub="Model performance" />
        <StatCard title="Avg Confidence (%)" value={(stats.avgConfidence || 0).toFixed(2)} />
        <StatCard title="Detected Attacks" value={stats.attack || 0} />
        <ChartCard title="Normal vs Attack">
          <div style={{ width: "100%", height: 240 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={80} label>
                  {pieData.map((entry, index) => <Cell key={`c-${index}`} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      <div className="col-span-1 space-y-4">
        <ChartCard title="Attack Types">
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <BarChart data={barData}>
                <XAxis dataKey="name" tick={{fontSize:12}}/>
                <YAxis />
                <Tooltip />
                <Bar dataKey="value">
                  {barData.map((entry, idx) => <Cell key={`b-${idx}`} fill={COLORS[idx % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>
    </div>
  );
}
