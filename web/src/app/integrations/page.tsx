"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Search, 
  Plus, 
  Settings, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  ExternalLink, 
  Zap, 
  Shield, 
  Clock, 
  RefreshCw,
  Facebook,
  Instagram,
  Linkedin,
  Building2,
  MessageSquare,
  Target,
  Loader2,
  Filter
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRelativeTimeHours } from '@/lib/time-utils';
import { QuickHelp } from '@/components/tutorials';

// Component for rendering relative time that prevents hydration issues
function RelativeTime({ timestamp }: { timestamp: string }) {
  const relativeTime = useRelativeTimeHours(timestamp, 300000); // Update every 5 minutes
  return <span>{relativeTime}</span>;
}

// Platform icons mapping
const platformIcons = {
  facebook: Facebook,
  instagram: Instagram,
  linkedin: Linkedin,
  google_gbp: Building2,
  tiktok_ads: Target,
  google_ads: Target,
  whatsapp: MessageSquare
};

// Platform categories
const platformCategories = {
  facebook: "social",
  instagram: "social", 
  linkedin: "social",
  google_gbp: "local",
  tiktok_ads: "advertising",
  google_ads: "advertising",
  whatsapp: "messaging"
};

interface PlatformIntegration {
  platform: string;
  name: string;
  description: string;
  icon: string;
  connect_url: string;
  status: "connected" | "disconnected" | "error" | "pending";
  last_sync?: string;
  error_message?: string;
}

// Real integrations data - fetched from API
const getIntegrations = async (): Promise<PlatformIntegration[]> => {
  try {
    const response = await fetch('/api/v1/integrations', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch integrations');
    }
    
    const data = await response.json();
    return data.integrations || [];
  } catch (error) {
    console.error('Error fetching integrations:', error);
    // Return default integrations if API fails
    return [
      {
        platform: "facebook",
        name: "Facebook",
        description: "Connect your Facebook pages and Instagram business accounts",
        icon: "facebook",
        connect_url: "/api/v1/oauth/meta/authorize",
        status: "disconnected"
      },
      {
        platform: "linkedin",
        name: "LinkedIn",
        description: "Manage your LinkedIn company page and personal profile",
        icon: "linkedin",
        connect_url: "/api/v1/oauth/linkedin/authorize",
        status: "disconnected"
      }
    ];
  }
};

const categories = [
  { id: "all", name: "All Integrations" },
  { id: "social", name: "Social Media" },
  { id: "advertising", name: "Advertising" },
  { id: "local", name: "Local Business" },
  { id: "messaging", name: "Messaging" }
];

export default function IntegrationsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [integrations, setIntegrations] = useState<PlatformIntegration[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch integrations on component mount
  useEffect(() => {
    const fetchIntegrations = async () => {
      setLoading(true);
      try {
        const data = await getIntegrations();
        setIntegrations(data);
      } catch (error) {
        console.error('Failed to load integrations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchIntegrations();
  }, []);

  const filteredIntegrations = (integrations || []).filter(integration => {
    const matchesSearch = integration.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         integration.description.toLowerCase().includes(searchTerm.toLowerCase());
    const category = platformCategories[integration.platform as keyof typeof platformCategories] || "other";
    const matchesCategory = selectedCategory === "all" || category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const connectedIntegrations = (integrations || []).filter(i => i.status === "connected");
  const disconnectedIntegrations = (integrations || []).filter(i => i.status === "disconnected");
  const errorIntegrations = (integrations || []).filter(i => i.status === "error");

  const formatLastSync = (lastSync: string | null) => {
    if (!lastSync) return "Never";
    return <RelativeTime timestamp={lastSync} />;
  };

  const handleConnect = (integration: PlatformIntegration) => {
    console.log(`Connecting to ${integration.platform}`);
    // Update status to pending
    setIntegrations(prev => prev.map(i => 
      i.platform === integration.platform 
        ? { ...i, status: "pending" as const }
        : i
    ));
    
    // Simulate connection process
    setTimeout(() => {
      setIntegrations(prev => prev.map(i => 
        i.platform === integration.platform 
          ? { ...i, status: "connected" as const, last_sync: new Date().toISOString() }
          : i
      ));
    }, 2000);
  };

  const handleDisconnect = (integration: PlatformIntegration) => {
    console.log(`Disconnecting from ${integration.platform}`);
    setIntegrations(prev => prev.map(i => 
      i.platform === integration.platform 
        ? { ...i, status: "disconnected" as const, last_sync: undefined }
        : i
    ));
  };

  const handleReconnect = (integration: PlatformIntegration) => {
    console.log(`Reconnecting to ${integration.platform}`);
    setIntegrations(prev => prev.map(i => 
      i.platform === integration.platform 
        ? { ...i, status: "pending" as const }
        : i
    ));
    
    setTimeout(() => {
      setIntegrations(prev => prev.map(i => 
        i.platform === integration.platform 
          ? { ...i, status: "connected" as const, last_sync: new Date().toISOString() }
          : i
      ));
    }, 2000);
  };

  const getPlatformIcon = (platform: string) => {
    const IconComponent = platformIcons[platform as keyof typeof platformIcons];
    return IconComponent ? <IconComponent className="h-6 w-6" /> : <div className="h-6 w-6 bg-muted rounded" />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Loader2 className="h-4 w-4 text-yellow-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'status-success';
      case 'error':
        return 'status-error';
      case 'pending':
        return 'status-warning';
      default:
        return 'status-info';
    }
  };

  return (
    <div className="h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Integrations</h1>
          <p className="text-muted-foreground">Connect your favorite platforms and services</p>
        </div>
        <div className="flex items-center gap-2">
          <QuickHelp context="integrations" />
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Integration
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="card-lattice">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Connected</p>
                <p className="text-2xl font-bold text-foreground">{connectedIntegrations.length}</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="card-lattice">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Disconnected</p>
                <p className="text-2xl font-bold text-foreground">{disconnectedIntegrations.length}</p>
              </div>
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="card-lattice">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Errors</p>
                <p className="text-2xl font-bold text-foreground">{errorIntegrations.length}</p>
              </div>
              <XCircle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="card-lattice">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total</p>
                <p className="text-2xl font-bold text-foreground">{integrations.length}</p>
              </div>
              <Zap className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search integrations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-background border border-border rounded-md px-3 py-2 text-sm"
          >
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Integrations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredIntegrations.map((integration) => (
          <Card key={integration.platform} className="card-lattice card-lattice-hover">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getPlatformIcon(integration.icon)}
                  <div>
                    <CardTitle className="text-lg">{integration.name}</CardTitle>
                    <p className="text-sm text-muted-foreground">{integration.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(integration.status)}
                  <Badge className={cn("text-xs", getStatusColor(integration.status))}>
                    {integration.status}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {integration.last_sync && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <span>Last sync: {formatLastSync(integration.last_sync)}</span>
                </div>
              )}
              
              {integration.error_message && (
                <div className="flex items-center gap-2 text-sm text-red-500">
                  <AlertTriangle className="h-4 w-4" />
                  <span>{integration.error_message}</span>
                </div>
              )}

              <div className="flex gap-2">
                {integration.status === 'connected' && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDisconnect(integration)}
                      className="flex-1"
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Disconnect
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(integration.connect_url, '_blank')}
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </>
                )}
                
                {integration.status === 'disconnected' && (
                  <Button
                    size="sm"
                    onClick={() => handleConnect(integration)}
                    className="flex-1"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Connect
                  </Button>
                )}
                
                {integration.status === 'error' && (
                  <Button
                    size="sm"
                    onClick={() => handleReconnect(integration)}
                    className="flex-1"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reconnect
                  </Button>
                )}
                
                {integration.status === 'pending' && (
                  <Button
                    variant="outline"
                    size="sm"
                    disabled
                    className="flex-1"
                  >
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Connecting...
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}