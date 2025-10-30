import React from "react";

export default function StatCard({title, value, sub}) {
  return (
    <div className="p-4 rounded-lg card w-full">
      <div className="text-sm text-neon/80">{title}</div>
      <div className="text-2xl font-bold mt-2">{value}</div>
      {sub && <div className="text-xs text-neon/60 mt-1">{sub}</div>}
    </div>
  );
}
