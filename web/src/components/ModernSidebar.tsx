'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Calendar, 
  BarChart3, 
  Settings, 
  Users, 
  FileText, 
  Zap,
  MessageSquare,
  Image,
  Video,
  TrendingUp,
  Bell,
  HelpCircle
} from 'lucide-react'

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: BarChart3,
    current: false
  },
  {
    name: 'Calendar',
    href: '/public-calendar',
    icon: Calendar,
    current: false
  },
  {
    name: 'Content',
    href: '/content',
    icon: FileText,
    current: false
  },
  {
    name: 'Channels',
    href: '/channels',
    icon: Users,
    current: false
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: TrendingUp,
    current: false
  },
  {
    name: 'AI Assistant',
    href: '/ai-assistant',
    icon: Zap,
    current: false
  },
  {
    name: 'Messages',
    href: '/messages',
    icon: MessageSquare,
    current: false
  },
  {
    name: 'Media',
    href: '/media',
    icon: Image,
    current: false
  },
  {
    name: 'Videos',
    href: '/videos',
    icon: Video,
    current: false
  }
]

const secondaryItems = [
  {
    name: 'Notifications',
    href: '/notifications',
    icon: Bell,
    current: false
  },
  {
    name: 'Help & Support',
    href: '/help',
    icon: HelpCircle,
    current: false
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    current: false
  }
]

export function ModernSidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">VANTAGE</h1>
            <p className="text-xs text-gray-500 -mt-1">AI Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col px-4 py-6 space-y-1">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <item.icon 
                  className={`h-5 w-5 ${
                    isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-700'
                  }`} 
                />
                {item.name}
              </Link>
            )
          })}
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200 my-4"></div>

        {/* Secondary Navigation */}
        <div className="space-y-1">
          {secondaryItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <item.icon 
                  className={`h-5 w-5 ${
                    isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-700'
                  }`} 
                />
                {item.name}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* User Profile */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-gray-700">U</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">User Name</p>
            <p className="text-xs text-gray-500 truncate">user@example.com</p>
          </div>
        </div>
      </div>
    </div>
  )
}
