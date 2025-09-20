"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  Dialog,
  DialogContent,
} from "@/components/ui/dialog";
import {
  Search,
  FileText,
  Calendar,
  MessageSquare,
  Settings,
  Plus,
  Clock,
  BarChart3,
  Users,
  Image,
  Zap,
  CreditCard,
  Shield,
  Palette,
  LayoutDashboard,
  Upload,
  Download,
} from "lucide-react";
import toast from "react-hot-toast";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();
  const [search, setSearch] = useState("");

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        onOpenChange(!open);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [open, onOpenChange]);

  const runCommand = (command: () => void) => {
    command();
    onOpenChange(false);
    setSearch("");
  };

  const actions = [
    {
      id: "create-draft",
      title: "Create draft",
      description: "Start writing a new content draft",
      icon: <FileText className="h-4 w-4" />,
      action: () => {
        toast.success("Creating new draft...");
        router.push("/composer");
      },
      keywords: ["new", "draft", "content", "create", "write"],
    },
    {
      id: "schedule-now",
      title: "Schedule now",
      description: "Schedule content for immediate publishing",
      icon: <Clock className="h-4 w-4" />,
      action: () => {
        toast.success("Opening scheduler...");
        router.push("/calendar?action=schedule");
      },
      keywords: ["schedule", "publish", "now", "post", "immediate"],
    },
    {
      id: "search-content",
      title: "Search content",
      description: "Search the web for inspiration and trending content",
      icon: <Search className="h-4 w-4" />,
      action: () => {
        toast.success("Opening content search...");
        router.push("/search");
      },
      keywords: ["search", "find", "research", "content", "web"],
    },
    {
      id: "create-campaign",
      title: "Create campaign",
      description: "Start a new marketing campaign",
      icon: <Image className="h-4 w-4" />,
      action: () => {
        toast.success("Creating new campaign...");
        router.push("/campaigns?action=create");
      },
      keywords: ["campaign", "marketing", "ads", "promotion", "create"],
    },
    {
      id: "view-analytics",
      title: "View analytics",
      description: "Check performance metrics and insights",
      icon: <BarChart3 className="h-4 w-4" />,
      action: () => {
        toast.success("Loading analytics...");
        router.push("/analytics");
      },
      keywords: ["analytics", "metrics", "performance", "stats", "insights"],
    },
    {
      id: "upload-media",
      title: "Upload media",
      description: "Upload images, videos, or other media files",
      icon: <Upload className="h-4 w-4" />,
      action: () => {
        toast.success("Opening media upload...");
        router.push("/media?action=upload");
      },
      keywords: ["upload", "media", "images", "videos", "files"],
    },
    {
      id: "manage-team",
      title: "Manage team",
      description: "Add, remove, or manage team members",
      icon: <Users className="h-4 w-4" />,
      action: () => {
        toast.success("Opening team management...");
        router.push("/team");
      },
      keywords: ["team", "members", "users", "manage", "collaboration"],
    },
    {
      id: "view-automation",
      title: "View automation",
      description: "Manage automated workflows and rules",
      icon: <Zap className="h-4 w-4" />,
      action: () => {
        toast.success("Opening automation dashboard...");
        router.push("/automation");
      },
      keywords: ["automation", "workflows", "rules", "auto", "zap"],
    },
    {
      id: "export-data",
      title: "Export data",
      description: "Export your content and analytics data",
      icon: <Download className="h-4 w-4" />,
      action: () => {
        toast.success("Preparing data export...");
        // Simulate export process
        setTimeout(() => {
          toast.success("Data export completed!");
        }, 2000);
      },
      keywords: ["export", "download", "data", "backup", "save"],
    },
    {
      id: "go-to-inbox",
      title: "Go to Inbox",
      description: "View messages and conversations",
      icon: <MessageSquare className="h-4 w-4" />,
      action: () => {
        toast.success("Opening inbox...");
        router.push("/collaboration");
      },
      keywords: ["inbox", "messages", "conversations", "chat", "mail"],
    },
    {
      id: "open-settings",
      title: "Open Settings",
      description: "Configure your account and preferences",
      icon: <Settings className="h-4 w-4" />,
      action: () => {
        toast.success("Opening settings...");
        router.push("/settings");
      },
      keywords: ["settings", "preferences", "config", "account"],
    },
  ];

  const navigation = [
    {
      id: "nav-dashboard",
      title: "Dashboard",
      description: "Go to main dashboard",
      icon: <LayoutDashboard className="h-4 w-4" />,
      action: () => router.push("/dashboard"),
      keywords: ["dashboard", "home", "overview"],
    },
    {
      id: "nav-calendar",
      title: "Calendar",
      description: "View scheduled content",
      icon: <Calendar className="h-4 w-4" />,
      action: () => router.push("/calendar"),
      keywords: ["calendar", "schedule", "timeline"],
    },
    {
      id: "nav-templates",
      title: "Templates",
      description: "Manage content templates",
      icon: <FileText className="h-4 w-4" />,
      action: () => router.push("/templates"),
      keywords: ["templates", "content", "designs"],
    },
    {
      id: "nav-campaigns",
      title: "Campaigns",
      description: "View marketing campaigns",
      icon: <Image className="h-4 w-4" />,
      action: () => router.push("/campaigns"),
      keywords: ["campaigns", "marketing", "ads"],
    },
    {
      id: "nav-reports",
      title: "Reports",
      description: "Analytics and insights",
      icon: <BarChart3 className="h-4 w-4" />,
      action: () => router.push("/reports"),
      keywords: ["reports", "analytics", "insights", "stats"],
    },
    {
      id: "nav-automations",
      title: "Automations",
      description: "Automated workflows and rules",
      icon: <Zap className="h-4 w-4" />,
      action: () => router.push("/automations"),
      keywords: ["automations", "rules", "workflows", "auto"],
    },
    {
      id: "nav-team",
      title: "Team",
      description: "Manage team members",
      icon: <Users className="h-4 w-4" />,
      action: () => router.push("/team"),
      keywords: ["team", "members", "users", "collaboration"],
    },
    {
      id: "nav-collaboration",
      title: "Collaboration",
      description: "Content approvals, comments, and version control",
      icon: <MessageSquare className="h-4 w-4" />,
      action: () => router.push("/collaboration"),
      keywords: ["collaboration", "approvals", "comments", "feedback", "versions", "teamwork"],
    },
    {
      id: "nav-billing",
      title: "Billing",
      description: "Subscription and payments",
      icon: <CreditCard className="h-4 w-4" />,
      action: () => router.push("/billing"),
      keywords: ["billing", "subscription", "payments", "plan"],
    },
  ];

  const allCommands = [...actions, ...navigation];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="p-0 max-w-lg">
        <Command className="rounded-lg border-none shadow-md">
          <div className="flex items-center border-b px-3" cmdk-input-wrapper="">
            <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
            <Command.Input
              placeholder="Type a command or search..."
              value={search}
              onValueChange={setSearch}
              className="flex h-12 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            />
            <kbd className="pointer-events-none ml-auto hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100 sm:flex">
              <span className="text-xs">ESC</span>
            </kbd>
          </div>
          <Command.List className="max-h-[300px] overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>
            
            <Command.Group heading="Actions">
              {actions.map((action) => (
                <Command.Item
                  key={action.id}
                  value={`${action.title} ${action.keywords.join(" ")}`}
                  onSelect={() => runCommand(action.action)}
                  className="flex items-center gap-3 rounded-sm px-3 py-2 text-sm cursor-pointer hover:bg-accent aria-selected:bg-accent"
                >
                  {action.icon}
                  <div className="flex-1">
                    <div className="font-medium">{action.title}</div>
                    <div className="text-xs text-muted-foreground">{action.description}</div>
                  </div>
                </Command.Item>
              ))}
            </Command.Group>

            <Command.Separator className="my-2 h-px bg-border" />

            <Command.Group heading="Navigation">
              {navigation.map((nav) => (
                <Command.Item
                  key={nav.id}
                  value={`${nav.title} ${nav.keywords.join(" ")}`}
                  onSelect={() => runCommand(nav.action)}
                  className="flex items-center gap-3 rounded-sm px-3 py-2 text-sm cursor-pointer hover:bg-accent aria-selected:bg-accent"
                >
                  {nav.icon}
                  <div className="flex-1">
                    <div className="font-medium">{nav.title}</div>
                    <div className="text-xs text-muted-foreground">{nav.description}</div>
                  </div>
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>
          
          <div className="border-t px-3 py-2 text-xs text-muted-foreground">
            Use ↑↓ to navigate, Enter to select, ESC to close
          </div>
        </Command>
      </DialogContent>
    </Dialog>
  );
}
