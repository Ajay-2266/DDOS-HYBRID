import React from "react";

export default function ChartCard({title, children}) {
  return (
    <div className="p-4 rounded-lg card">
      <div className="text-sm text-neon/80">{title}</div>
      <div className="mt-2">{children}</div>
    </div>
  );
}
