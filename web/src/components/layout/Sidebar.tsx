"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  ChevronLeft,
  LayoutDashboard,
  MessageSquare,
  Calendar,
  FileText,
  Image,
  BarChart3,
  Settings,
  Users,
  Zap,
  Shield,
  CreditCard,
  Palette,
  Bell,
} from "lucide-react";

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navigation = [
    {
      title: "Dashboard",
      items: [
        {
          title: "Overview",
          href: "/dashboard",
          icon: LayoutDashboard,
          badge: null,
        },
        {
          title: "Calendar",
          href: "/calendar",
          icon: Calendar,
          badge: null,
        },
      ],
    },
    {
      title: "Content & Messaging",
      items: [
        {
          title: "Inbox",
          href: "/inbox",
          icon: MessageSquare,
          badge: "3",
        },
        {
          title: "Templates",
          href: "/templates",
          icon: FileText,
          badge: null,
        },
        {
          title: "Campaigns",
          href: "/campaigns",
          icon: Image,
          badge: null,
        },
        {
          title: "Planning",
          href: "/planning",
          icon: Calendar,
          badge: null,
        },
      ],
    },
    {
      title: "Analytics & Automation",
      items: [
        {
          title: "Reports",
          href: "/reports",
          icon: BarChart3,
          badge: null,
        },
        {
          title: "Automations",
          href: "/automations",
          icon: Zap,
          badge: null,
        },
      ],
    },
    {
      title: "Settings",
      items: [
        {
          title: "Brand Guide",
          href: "/brand-guide",
          icon: Palette,
          badge: null,
        },
        {
          title: "Team",
          href: "/team",
          icon: Users,
          badge: null,
        },
        {
          title: "Billing",
          href: "/billing",
          icon: CreditCard,
          badge: null,
        },
        {
          title: "Privacy",
          href: "/privacy",
          icon: Shield,
          badge: null,
        },
        {
          title: "AI Usage",
          href: "/dev/ai-usage",
          icon: BarChart3,
          badge: null,
        },
      ],
    },
  ];

  const isActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === "/" || pathname === "/dashboard";
    }
    return pathname.startsWith(href);
  };

  return (
    <div
      className={cn(
        "flex flex-col h-full border-r bg-background transition-all duration-300",
        isCollapsed ? "w-16" : "w-64",
        className
      )}
    >
      {/* Collapse Toggle */}
      <div className="flex items-center justify-end p-2 border-b">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="h-8 w-8 p-0"
        >
          <ChevronLeft className={cn("h-4 w-4 transition-transform", isCollapsed && "rotate-180")} />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-6 overflow-y-auto">
        {navigation.map((section, sectionIndex) => (
          <div key={sectionIndex} className="space-y-1">
            {!isCollapsed && (
              <h4 className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                {section.title}
              </h4>
            )}
            <div className="space-y-1">
              {section.items.map((item, itemIndex) => {
                const active = isActive(item.href);
                const Icon = item.icon;
                
                return (
                  <Link key={itemIndex} href={item.href}>
                    <Button
                      variant={active ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start h-10 px-3",
                        isCollapsed && "justify-center px-2",
                        active && "bg-secondary text-secondary-foreground font-medium"
                      )}
                      title={isCollapsed ? item.title : undefined}
                    >
                      <Icon className={cn("h-4 w-4", !isCollapsed && "mr-3")} />
                      {!isCollapsed && (
                        <>
                          <span className="flex-1 text-left">{item.title}</span>
                          {item.badge && (
                            <span className="ml-auto bg-primary text-primary-foreground text-xs px-1.5 py-0.5 rounded-full">
                              {item.badge}
                            </span>
                          )}
                        </>
                      )}
                    </Button>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Bottom section */}
      <div className="p-2 border-t">
        <Link href="/settings">
          <Button
            variant={isActive("/settings") ? "secondary" : "ghost"}
            className={cn(
              "w-full justify-start h-10 px-3",
              isCollapsed && "justify-center px-2"
            )}
            title={isCollapsed ? "Settings" : undefined}
          >
            <Settings className={cn("h-4 w-4", !isCollapsed && "mr-3")} />
            {!isCollapsed && "Settings"}
          </Button>
        </Link>
      </div>
    </div>
  );
}
