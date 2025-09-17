"use client";

import { useState } from "react";
import { Topbar } from "./Topbar";
import { Sidebar } from "./Sidebar";
import { CommandPalette } from "./CommandPalette";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  const handleSearchFocus = () => {
    setCommandPaletteOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-blue-100/60 to-indigo-100/40 rounded-full blur-2xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-24 h-24 bg-gradient-to-br from-purple-100/60 to-pink-100/40 rounded-full blur-2xl animate-pulse [animation-delay:1s]"></div>
        <div className="absolute bottom-32 left-1/3 w-40 h-40 bg-gradient-to-br from-cyan-100/60 to-blue-100/40 rounded-full blur-2xl animate-pulse [animation-delay:2s]"></div>
      </div>

      <div className="relative z-10 h-screen flex flex-col">
        {/* Topbar */}
        <Topbar onSearchFocus={handleSearchFocus} />

        {/* Main content area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <Sidebar className="hidden md:flex" />

          {/* Page content */}
          <main className="flex-1 overflow-auto">
            <div className="h-full">
              {children}
            </div>
          </main>
        </div>
      </div>

      {/* Command Palette */}
      <CommandPalette 
        open={commandPaletteOpen} 
        onOpenChange={setCommandPaletteOpen} 
      />
    </div>
  );
}
