import React from "react";
import { Link, useLocation } from "react-router-dom";

const NavItem = ({to, label}) => {
  const loc = useLocation();
  const active = loc.pathname === to;
  return (
    <Link to={to} className={`px-4 py-2 rounded ${active ? "bg-accent text-black" : "hover:bg-accent/50"}`}>
      {label}
    </Link>
  );
};

export default function Navbar(){
  return (
    <nav className="flex items-center justify-between px-6 py-4 border-b border-accent card">
      <div className="text-xl font-bold">DDoS Detection</div>
      <div className="flex gap-2">
        <NavItem to="/" label="Dashboard" />
        <NavItem to="/upload" label="Upload" />
        <NavItem to="/live" label="Live Test" />
        <NavItem to="/history" label="History" />
      </div>
    </nav>
  );
}
