"use client";

import { useState, useEffect } from "react";
import Image from 'next/image';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  MessageSquare, 
  Search, 
  Filter, 
  Send, 
  Bot, 
  Phone, 
  Mail, 
  Clock,
  ChevronRight,
  MoreVertical,
  Star,
  Archive,
  Trash2
} from "lucide-react";

interface Conversation {
  id: string;
  org_id: string;
  channel: string;
  peer_id: string;
  last_message_at: string | null;
  created_at: string;
  message_count: number;
}

interface Message {
  id: string;
  conversation_id: string;
  direction: "inbound" | "outbound";
  text: string | null;
  media_url: string | null;
  metadata: any;
  created_at: string;
}

interface InboxStats {
  total_conversations: number;
  recent_conversations: number;
  channel_breakdown: Record<string, number>;
  generated_at: string;
}

export default function InboxPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [stats, setStats] = useState<InboxStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [channelFilter, setChannelFilter] = useState<string>("all");
  const [newMessage, setNewMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [showAIDraft, setShowAIDraft] = useState(false);
  const [aiDraft, setAiDraft] = useState("");
  const [generatingDraft, setGeneratingDraft] = useState(false);

  // Load conversations and stats
  useEffect(() => {
    loadConversations();
    loadStats();
  }, []);

  // Load messages when conversation is selected
  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation.id);
    }
  }, [selectedConversation]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/inbox/threads");
      const data = await response.json();
      setConversations(data.threads || []);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch("/api/v1/inbox/stats/summary");
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  const loadMessages = async (conversationId: string) => {
    try {
      const response = await fetch(`/api/v1/inbox/${conversationId}/messages`);
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error("Failed to load messages:", error);
    }
  };

  const handleSendMessage = async () => {
    if (!selectedConversation || !newMessage.trim()) return;

    try {
      setSending(true);
      const response = await fetch(`/api/v1/inbox/${selectedConversation.id}/reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message_text: newMessage })
      });

      if (response.ok) {
        setNewMessage("");
        await loadMessages(selectedConversation.id);
        await loadConversations(); // Refresh to update last_message_at
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setSending(false);
    }
  };

  const handleGenerateAIDraft = async () => {
    if (!selectedConversation) return;

    try {
      setGeneratingDraft(true);
      const response = await fetch(`/api/v1/inbox/${selectedConversation.id}/ai-draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tone: "professional" })
      });

      const data = await response.json();
      if (data.draft) {
        setAiDraft(data.draft);
        setShowAIDraft(true);
      }
    } catch (error) {
      console.error("Failed to generate AI draft:", error);
    } finally {
      setGeneratingDraft(false);
    }
  };

  const handleUseAIDraft = () => {
    setNewMessage(aiDraft);
    setShowAIDraft(false);
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case "whatsapp":
        return <MessageSquare className="h-4 w-4" />;
      case "sms":
        return <Phone className="h-4 w-4" />;
      case "email":
        return <Mail className="h-4 w-4" />;
      default:
        return <MessageSquare className="h-4 w-4" />;
    }
  };

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case "whatsapp":
        return "bg-green-100 text-green-800";
      case "sms":
        return "bg-blue-100 text-blue-800";
      case "email":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatPhoneNumber = (phone: string) => {
    // Simple phone number formatting
    if (phone.length > 10) {
      return `+${phone.slice(0, -10)} ${phone.slice(-10, -7)}-${phone.slice(-7, -4)}-${phone.slice(-4)}`;
    }
    return phone;
  };

  const formatTime = (timestamp: string | null) => {
    if (!timestamp) return "No messages";
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.peer_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesChannel = channelFilter === "all" || conv.channel === channelFilter;
    return matchesSearch && matchesChannel;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Conversations Sidebar */}
      <div className="w-1/3 border-r bg-gray-50/50">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold">Inbox</h1>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-2 gap-2 mb-4">
              <div className="text-center p-2 bg-white rounded">
                <div className="text-lg font-semibold">{stats.total_conversations}</div>
                <div className="text-xs text-muted-foreground">Total</div>
              </div>
              <div className="text-center p-2 bg-white rounded">
                <div className="text-lg font-semibold text-orange-600">{stats.recent_conversations}</div>
                <div className="text-xs text-muted-foreground">Recent</div>
              </div>
            </div>
          )}
          
          {/* Search and Filters */}
          <div className="space-y-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={channelFilter} onValueChange={setChannelFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All channels" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Channels</SelectItem>
                <SelectItem value="whatsapp">WhatsApp</SelectItem>
                <SelectItem value="sms">SMS</SelectItem>
                <SelectItem value="email">Email</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        {/* Conversations List */}
        <div className="overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className="p-4">
              <EmptyState
                illustration="inbox"
                title="No conversations yet"
                description="When customers contact you through your connected channels, their messages will appear here."
                action={{
                  label: "Connect Channel",
                  onClick: () => alert("Navigate to channel setup"),
                  variant: "default"
                }}
                secondaryAction={{
                  label: "View Guide",
                  onClick: () => alert("Navigate to help"),
                  variant: "outline"
                }}
                className="py-8"
              />
            </div>
          ) : (
            filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`p-4 border-b cursor-pointer hover:bg-gray-100 ${
                  selectedConversation?.id === conversation.id ? "bg-blue-50 border-l-4 border-l-blue-500" : ""
                }`}
                onClick={() => setSelectedConversation(conversation)}
              >
                <div className="flex items-start space-x-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback>
                      {conversation.peer_id.slice(-2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium truncate">
                          {conversation.channel === "whatsapp" 
                            ? formatPhoneNumber(conversation.peer_id)
                            : conversation.peer_id
                          }
                        </span>
                        <Badge className={getChannelColor(conversation.channel)}>
                          {getChannelIcon(conversation.channel)}
                          <span className="ml-1 capitalize">{conversation.channel}</span>
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-xs text-muted-foreground">
                          {formatTime(conversation.last_message_at)}
                        </span>
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {conversation.message_count} messages
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Conversation Header */}
            <div className="p-4 border-b bg-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback>
                      {selectedConversation.peer_id.slice(-2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="font-medium">
                      {selectedConversation.channel === "whatsapp" 
                        ? formatPhoneNumber(selectedConversation.peer_id)
                        : selectedConversation.peer_id
                      }
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {selectedConversation.message_count} messages
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm" onClick={handleGenerateAIDraft} disabled={generatingDraft}>
                    <Bot className="h-4 w-4 mr-2" />
                    {generatingDraft ? "Generating..." : "AI Draft"}
                  </Button>
                  <Button variant="outline" size="sm">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.direction === "outbound" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.direction === "outbound"
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    {message.text && <div className="text-sm">{message.text}</div>}
                    {message.media_url && (
                      <div className="mt-2">
                        {message.media_url.match(/\.(jpg|jpeg|png|gif)$/i) ? (
                          <Image 
                            src={message.media_url} 
                            alt="Media attachment" 
                            width={400}
                            height={300}
                            className="rounded object-contain"
                            style={{ maxWidth: '100%', height: 'auto' }}
                          />
                        ) : (
                          <a href={message.media_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                            View Media
                          </a>
                        )}
                      </div>
                    )}
                    <div className={`text-xs mt-1 ${
                      message.direction === "outbound" ? "text-blue-100" : "text-gray-500"
                    }`}>
                      {formatTime(message.created_at)}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t bg-white">
              <div className="flex space-x-2">
                <div className="flex-1">
                  <Textarea
                    placeholder="Type your reply..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    rows={1}
                    className="resize-none"
                  />
                </div>
                <Button onClick={handleSendMessage} disabled={!newMessage.trim() || sending}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            <div className="text-center py-16">
              <div className="max-w-sm mx-auto">
                <div className="rounded-full bg-muted/20 w-16 h-16 flex items-center justify-center mx-auto mb-6">
                  <MessageSquare className="h-8 w-8 text-muted-foreground/60" />
                </div>
                <h3 className="text-xl font-semibold mb-3 text-foreground">Select a conversation</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Choose a conversation from the sidebar to view messages and start replying to your customers.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Draft Dialog */}
      <Dialog open={showAIDraft} onOpenChange={setShowAIDraft}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>AI-Generated Draft</DialogTitle>
            <DialogDescription>
              Here's a suggested reply for this conversation based on your brand voice
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Textarea
              value={aiDraft}
              onChange={(e) => setAiDraft(e.target.value)}
              rows={6}
              className="font-mono text-sm"
            />
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowAIDraft(false)}>
                Cancel
              </Button>
              <Button onClick={handleUseAIDraft}>
                Use This Draft
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
