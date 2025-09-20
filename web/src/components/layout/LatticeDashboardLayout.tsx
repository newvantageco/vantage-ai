"use client";

import { useState } from "react";
import { LatticeSidebar } from "./LatticeSidebar";
import { CommandPalette } from "./CommandPalette";
import { Toaster } from "react-hot-toast";
import { Button } from "@/components/ui/button";
import { 
  Search, 
  Menu, 
  Bell, 
  Settings,
  Zap
} from "lucide-react";
import { WorkingTutorialButton } from "@/components/tutorials";
import { ThemeToggle } from "@/components/theme-toggle";

interface LatticeDashboardLayoutProps {
  children: React.ReactNode;
}

export function LatticeDashboardLayout({ children }: LatticeDashboardLayoutProps) {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSearchFocus = () => {
    setCommandPaletteOpen(true);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="h-screen flex flex-col">
        {/* Top Navigation Bar */}
        <header className="h-16 border-b border-border bg-card flex items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </Button>
            
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-green-600 to-green-700 rounded-lg flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-foreground">VANTAGE AI</h1>
                <p className="text-xs text-muted-foreground -mt-1">Operator Console</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Search */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleSearchFocus}
              className="hidden sm:flex items-center gap-2 text-muted-foreground"
            >
              <Search className="h-4 w-4" />
              <span className="text-sm">Search...</span>
              <kbd className="pointer-events-none hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
                <span className="text-xs">⌘</span>K
              </kbd>
            </Button>

            {/* Notifications */}
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full flex items-center justify-center">
                <span className="text-xs text-white font-bold">3</span>
              </span>
            </Button>

            {/* Tutorial Button */}
            <WorkingTutorialButton variant="inline" />

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Settings */}
            <Button variant="ghost" size="sm">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Desktop Sidebar */}
          <LatticeSidebar className="hidden lg:flex" />
          
          {/* Mobile Sidebar Overlay */}
          {sidebarOpen && (
            <div className="lg:hidden fixed inset-0 z-50">
              <div 
                className="fixed inset-0 bg-black/50 backdrop-blur-sm"
                onClick={() => setSidebarOpen(false)}
              />
              <div className="fixed left-0 top-0 h-full w-64">
                <LatticeSidebar onClose={() => setSidebarOpen(false)} />
              </div>
            </div>
          )}

          {/* Page Content */}
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
      
      {/* Floating Tutorial Button */}
      <WorkingTutorialButton variant="floating" />

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'hsl(var(--card))',
            color: 'hsl(var(--card-foreground))',
            borderRadius: '8px',
            border: '1px solid hsl(var(--border))',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.4)',
          },
          success: {
            iconTheme: {
              primary: '#22c55e',
              secondary: 'white',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: 'white',
            },
          },
        }}
      />
    </div>
  );
}
