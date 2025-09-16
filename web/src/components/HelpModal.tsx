"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  HelpCircle, 
  ExternalLink, 
  Keyboard, 
  BookOpen, 
  MessageSquare,
  Zap,
  FileText,
  Users
} from "lucide-react";

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HelpModal({ isOpen, onClose }: HelpModalProps) {
  const [activeTab, setActiveTab] = useState<"shortcuts" | "docs" | "support">("shortcuts");

  // Close modal on Escape key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const shortcuts = [
    { keys: ["⌘", "K"], description: "Search templates" },
    { keys: ["⌘", "N"], description: "Create new template" },
    { keys: ["⌘", "/"], description: "Show this help" },
    { keys: ["Esc"], description: "Close modals" },
    { keys: ["Tab"], description: "Navigate between elements" },
    { keys: ["Enter"], description: "Confirm actions" },
  ];

  const docLinks = [
    {
      title: "Getting Started",
      description: "Learn the basics of using Vantage AI",
      icon: <Zap className="h-5 w-5" />,
      href: "/docs/getting-started",
    },
    {
      title: "Templates Guide",
      description: "How to create and manage content templates",
      icon: <FileText className="h-5 w-5" />,
      href: "/docs/templates",
    },
    {
      title: "API Reference",
      description: "Complete API documentation for developers",
      icon: <BookOpen className="h-5 w-5" />,
      href: "/docs/api",
    },
    {
      title: "Best Practices",
      description: "Tips for optimising your content workflow",
      icon: <Users className="h-5 w-5" />,
      href: "/docs/best-practices",
    },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5" />
            Help & Documentation
          </DialogTitle>
          <DialogDescription>
            Get help, learn keyboard shortcuts, and access documentation
          </DialogDescription>
        </DialogHeader>

        {/* Tab Navigation */}
        <div className="flex border-b">
          {[
            { id: "shortcuts", label: "Shortcuts", icon: <Keyboard className="h-4 w-4" /> },
            { id: "docs", label: "Documentation", icon: <BookOpen className="h-4 w-4" /> },
            { id: "support", label: "Support", icon: <MessageSquare className="h-4 w-4" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="py-4">
          {activeTab === "shortcuts" && (
            <div className="space-y-4">
              <h3 className="font-semibold">Keyboard Shortcuts</h3>
              <div className="grid gap-3">
                {shortcuts.map((shortcut, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                    <span className="text-sm text-muted-foreground">{shortcut.description}</span>
                    <div className="flex items-center gap-1">
                      {shortcut.keys.map((key, keyIndex) => (
                        <kbd
                          key={keyIndex}
                          className="px-2 py-1 text-xs font-semibold text-foreground bg-background border border-border rounded"
                        >
                          {key}
                        </kbd>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "docs" && (
            <div className="space-y-4">
              <h3 className="font-semibold">Documentation</h3>
              <div className="grid gap-3">
                {docLinks.map((doc, index) => (
                  <Card key={index} className="cursor-pointer hover:bg-muted/30 transition-colors">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-primary/10 rounded-lg">
                            {doc.icon}
                          </div>
                          <div>
                            <CardTitle className="text-base">{doc.title}</CardTitle>
                            <CardDescription className="text-sm">{doc.description}</CardDescription>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm" asChild>
                          <a href={doc.href} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      </div>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === "support" && (
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold mb-3">Get Support</h3>
                <div className="space-y-3">
                  <Card className="cursor-pointer hover:bg-muted/30 transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Contact Support</h4>
                          <p className="text-sm text-muted-foreground">Get help from our support team</p>
                        </div>
                        <Button variant="outline" size="sm" asChild>
                          <a href="mailto:support@vantage-ai.com">
                            <MessageSquare className="h-4 w-4 mr-2" />
                            Email Us
                          </a>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="cursor-pointer hover:bg-muted/30 transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Community</h4>
                          <p className="text-sm text-muted-foreground">Join our community discussions</p>
                        </div>
                        <Button variant="outline" size="sm" asChild>
                          <a href="https://community.vantage-ai.com" target="_blank" rel="noopener noreferrer">
                            <Users className="h-4 w-4 mr-2" />
                            Visit Community
                          </a>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Version Information</h4>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">v1.0.0</Badge>
                  <span className="text-sm text-muted-foreground">Last updated: Sept 2025</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Help Button Component
export function HelpButton() {
  const [isOpen, setIsOpen] = useState(false);

  // Keyboard shortcut to open help
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === '/') {
        event.preventDefault();
        setIsOpen(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 rounded-full w-12 h-12 shadow-lg bg-background border"
        title="Help & Documentation (⌘/)"
      >
        <HelpCircle className="h-5 w-5" />
      </Button>
      <HelpModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
}
