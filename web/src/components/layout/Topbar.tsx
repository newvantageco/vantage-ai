"use client";

import { useState } from "react";
import { Search, ChevronDown, Bell, Settings, LogOut, User, Building2, Plus } from "lucide-react";
import { UserButton, useUser } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ThemeToggle } from "@/components/theme-toggle";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";

interface TopbarProps {
  onSearchFocus?: () => void;
}

export function Topbar({ onSearchFocus }: TopbarProps) {
  const { user } = useUser();
  const [selectedOrg, setSelectedOrg] = useState("Acme Corp");
  
  // Mock organizations - in real app, this would come from API
  const organizations = [
    { id: "1", name: "Acme Corp", role: "Owner" },
    { id: "2", name: "Digital Agency", role: "Admin" },
    { id: "3", name: "Startup Inc", role: "Member" },
  ];

  const notifications = [
    { id: "1", title: "New message from customer", time: "2 min ago", unread: true },
    { id: "2", title: "Campaign published successfully", time: "1 hour ago", unread: true },
    { id: "3", title: "Weekly report ready", time: "3 hours ago", unread: false },
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <div className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-4 gap-4">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">V</span>
          </div>
          <span className="font-semibold text-lg hidden sm:block">Vantage AI</span>
        </div>

        {/* Organization Switcher */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2 px-3 h-9">
              <Building2 className="h-4 w-4" />
              <span className="hidden sm:block">{selectedOrg}</span>
              <ChevronDown className="h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-64">
            <DropdownMenuLabel>Switch Organisation</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {organizations.map((org) => (
              <DropdownMenuItem
                key={org.id}
                onClick={() => setSelectedOrg(org.name)}
                className="flex items-center justify-between"
              >
                <div>
                  <div className="font-medium">{org.name}</div>
                  <div className="text-xs text-muted-foreground">{org.role}</div>
                </div>
                {org.name === selectedOrg && (
                  <div className="w-2 h-2 bg-primary rounded-full" />
                )}
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-primary">
              <Plus className="h-4 w-4 mr-2" />
              Create Organisation
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Global Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search everything... (⌘K)"
              className="pl-10 pr-4 h-9 bg-muted/30 border-0 focus-visible:bg-background"
              onClick={onSearchFocus}
              readOnly
            />
            <kbd className="absolute right-3 top-1/2 transform -translate-y-1/2 px-1.5 py-0.5 text-xs font-semibold text-muted-foreground bg-muted border border-border rounded">
              ⌘K
            </kbd>
          </div>
        </div>

        {/* Right side icons */}
        <div className="flex items-center gap-1">
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="relative h-9 w-9">
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                  <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs">
                    {unreadCount}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel className="flex items-center justify-between">
                Notifications
                <Button variant="ghost" size="sm" className="h-6 text-xs">
                  Mark all read
                </Button>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <div className="max-h-64 overflow-y-auto">
                {notifications.map((notification) => (
                  <DropdownMenuItem key={notification.id} className="flex items-start p-3">
                    <div className="flex-1">
                      <div className={`text-sm ${notification.unread ? 'font-medium' : ''}`}>
                        {notification.title}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {notification.time}
                      </div>
                    </div>
                    {notification.unread && (
                      <div className="w-2 h-2 bg-primary rounded-full mt-2" />
                    )}
                  </DropdownMenuItem>
                ))}
              </div>
              {notifications.length === 0 && (
                <div className="p-4 text-center text-muted-foreground text-sm">
                  No notifications
                </div>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Settings */}
          <Button variant="ghost" size="sm" className="h-9 w-9">
            <Settings className="h-4 w-4" />
          </Button>

          {/* Profile */}
          <div className="ml-2">
            <UserButton 
              afterSignOutUrl="/"
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8"
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
