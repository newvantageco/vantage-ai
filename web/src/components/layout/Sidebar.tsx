"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DashboardIcon,
  MessageIcon,
  CalendarIcon,
  ContentIcon,
  TargetIcon,
  AnalyticsIcon,
  SettingsIcon,
  UsersIcon,
  BotIcon,
  ShieldIcon,
  CreditCardIcon,
  PaletteIcon,
  BellIcon,
  ChevronLeftIcon,
  SparklesIcon,
  RefreshIcon,
  AlertCircleIcon,
  ActivityIcon,
  ClockIcon,
  FileEditIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  PlusIcon,
  SearchIcon,
  BuildingIcon
} from "@/components/ui/custom-icons";

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
          icon: DashboardIcon,
          badge: null,
        },
        {
          title: "Calendar",
          href: "/calendar",
          icon: CalendarIcon,
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
          icon: MessageIcon,
          badge: "3",
        },
        {
          title: "Templates",
          href: "/templates",
          icon: FileEditIcon,
          badge: null,
        },
        {
          title: "Campaigns",
          href: "/campaigns",
          icon: TargetIcon,
          badge: null,
        },
        {
          title: "Planning",
          href: "/planning",
          icon: CalendarIcon,
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
          icon: AnalyticsIcon,
          badge: null,
        },
        {
          title: "Automations",
          href: "/automations",
          icon: BotIcon,
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
          icon: PaletteIcon,
          badge: null,
        },
        {
          title: "Team",
          href: "/team",
          icon: UsersIcon,
          badge: null,
        },
        {
          title: "Billing",
          href: "/billing",
          icon: CreditCardIcon,
          badge: null,
        },
        {
          title: "Privacy",
          href: "/privacy",
          icon: ShieldIcon,
          badge: null,
        },
        {
          title: "AI Usage",
          href: "/dev/ai-usage",
          icon: SparklesIcon,
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
        "flex flex-col h-full border-r border-slate-200/50 bg-white/80 backdrop-blur-sm transition-all duration-300",
        isCollapsed ? "w-16" : "w-64",
        className
      )}
    >
      {/* Collapse Toggle */}
      <div className="flex items-center justify-end p-2 border-b border-slate-200/50">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="h-8 w-8 p-0 hover:bg-slate-100"
        >
          <ChevronLeftIcon className={cn("h-4 w-4 transition-transform text-slate-600", isCollapsed && "rotate-180")} />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-6 overflow-y-auto">
        {navigation.map((section, sectionIndex) => (
          <div key={sectionIndex} className="space-y-1">
            {!isCollapsed && (
              <h4 className="px-3 py-2 text-xs font-semibold text-slate-600 uppercase tracking-wide">
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
                        "w-full justify-start h-10 px-3 transition-all duration-200",
                        isCollapsed && "justify-center px-2",
                        active && "bg-gradient-to-r from-blue-100 to-indigo-100 text-slate-900 font-medium shadow-sm",
                        !active && "hover:bg-slate-100 text-slate-700"
                      )}
                      title={isCollapsed ? item.title : undefined}
                    >
                      <Icon className={cn("h-4 w-4", !isCollapsed && "mr-3", active ? "text-blue-600" : "text-slate-600")} />
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
            <SettingsIcon className={cn("h-4 w-4", !isCollapsed && "mr-3")} />
            {!isCollapsed && "Settings"}
          </Button>
        </Link>
      </div>
    </div>
  );
}
