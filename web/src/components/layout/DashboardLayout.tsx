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
    <div className="h-screen flex flex-col bg-background">
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

      {/* Command Palette */}
      <CommandPalette 
        open={commandPaletteOpen} 
        onOpenChange={setCommandPaletteOpen} 
      />
    </div>
  );
}
