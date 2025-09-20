"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Library, 
  Calendar, 
  BarChart3, 
  Settings, 
  Zap,
  ChevronRight,
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Play,
  Users,
  MessageSquare,
  GitBranch,
  Search
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    badge: null
  },
  {
    name: 'Content',
    href: '/content',
    icon: Library,
    badge: null
  },
  {
    name: 'Search',
    href: '/search',
    icon: Search,
    badge: 'New'
  },
  {
    name: 'Composer',
    href: '/composer',
    icon: Zap,
    badge: null
  },
  {
    name: 'Calendar',
    href: '/calendar',
    icon: Calendar,
    badge: null
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    badge: null
  },
  {
    name: 'Team',
    href: '/team',
    icon: Users,
    badge: null
  },
  {
    name: 'Collaboration',
    href: '/collaboration',
    icon: MessageSquare,
    badge: '5' // Pending approvals count
  },
  {
    name: 'Ops',
    href: '/ops',
    icon: Zap,
    badge: '3' // Active tasks count
  },
  {
    name: 'Engines',
    href: '/engines',
    icon: Activity,
    badge: 'Live' // Live system indicator
  },
  {
    name: 'Automation',
    href: '/automation',
    icon: Zap,
    badge: null
  },
  {
    name: 'Demo',
    href: '/demo',
    icon: Play,
    badge: 'Try' // Demo indicator
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    badge: null
  }
];

interface LatticeSidebarProps {
  className?: string;
  onClose?: () => void;
}

export function LatticeSidebar({ className = "", onClose }: LatticeSidebarProps) {
  const pathname = usePathname();

  return (
    <div className={`flex h-full w-64 flex-col sidebar-lattice ${className}`}>
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-green-600 to-green-700 rounded-lg flex items-center justify-center">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-foreground">VANTAGE</h1>
            <p className="text-xs text-muted-foreground -mt-1">AI Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col px-4 py-6 space-y-1">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`nav-item ${
                  isActive ? 'nav-item-active' : 'nav-item-inactive'
                }`}
                onClick={onClose}
              >
                <item.icon 
                  className="h-5 w-5" 
                />
                <span className="flex-1">{item.name}</span>
                {item.badge && (
                  <Badge variant="secondary" className="ml-auto text-xs">
                    {item.badge}
                  </Badge>
                )}
                {isActive && (
                  <ChevronRight className="h-4 w-4" />
                )}
              </Link>
            );
          })}
        </div>

        {/* Real-time Status Section */}
        <div className="mt-8 space-y-3">
          <div className="px-3 py-2">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              System Status
            </h3>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-3 px-3 py-2 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full pulse-realtime" />
              <span className="text-foreground">API Online</span>
            </div>
            <div className="flex items-center gap-3 px-3 py-2 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full pulse-realtime" />
              <span className="text-foreground">Database Connected</span>
            </div>
            <div className="flex items-center gap-3 px-3 py-2 text-sm">
              <div className="w-2 h-2 bg-yellow-500 rounded-full pulse-realtime" />
              <span className="text-foreground">AI Processing</span>
            </div>
          </div>
        </div>
      </nav>

      {/* User Profile */}
      <div className="border-t border-border p-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-white">U</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">Operator</p>
            <p className="text-xs text-muted-foreground truncate">admin@vantage.ai</p>
          </div>
          <div className="w-2 h-2 bg-green-500 rounded-full pulse-realtime" />
        </div>
      </div>
    </div>
  );
}
