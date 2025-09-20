"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  CreditCard, 
  TrendingUp, 
  Users, 
  AlertTriangle, 
  CheckCircle,
  Download,
  Settings,
  BarChart3
} from "lucide-react";

interface BillingData {
  has_subscription: boolean;
  plan: {
    id: number;
    name: string;
    display_name: string;
    description: string;
    price: number;
    currency: string;
    billing_interval: string;
    features: string[];
    limits: {
      ai_requests: number;
      ai_tokens: number;
      content_posts: number;
      team_members: number;
      integrations: number;
    };
  } | null;
  subscription: {
    id: number;
    status: string;
    current_period_start: string;
    current_period_end: string;
    canceled_at: string | null;
  } | null;
  usage: {
    month: string;
    ai_requests: number;
    content_posts: number;
    team_members: number;
    integrations: number;
    plan_limits: {
      ai_requests: number;
      ai_tokens: number;
      content_posts: number;
      team_members: number;
      integrations: number;
    };
    usage_percentage: {
      ai_requests: number;
      content_posts: number;
      team_members: number;
      integrations: number;
    };
    overage: {
      posts: number;
      ai_requests: number;
      amount: number;
    };
  };
  can_upgrade: boolean;
  can_downgrade: boolean;
}

interface Alert {
  type: string;
  severity: string;
  message: string;
  action: string;
  created_at: string;
}

export default function BillingPage() {
  const [billingData, setBillingData] = useState<BillingData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBillingData();
    fetchAlerts();
  }, []);

  const fetchBillingData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/billing/demo/status');
      if (!response.ok) throw new Error('Failed to fetch billing data');
      const data = await response.json();
      setBillingData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/billing/demo/alerts');
      if (!response.ok) throw new Error('Failed to fetch alerts');
      const data = await response.json();
      setAlerts(data.alerts || []);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    }
  };

  const handleUpgrade = async () => {
    try {
      const response = await fetch('/api/v1/billing/checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: 'pro',
          success_url: window.location.href,
          cancel_url: window.location.href
        })
      });
      const data = await response.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      console.error('Failed to create checkout session:', err);
    }
  };

  const handleCancel = async () => {
    if (confirm('Are you sure you want to cancel your subscription?')) {
      try {
        const response = await fetch('/api/v1/billing/cancel-subscription', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ immediately: false })
        });
        if (response.ok) {
          fetchBillingData();
        }
      } catch (err) {
        console.error('Failed to cancel subscription:', err);
      }
    }
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount / 100);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'trialing': return 'bg-blue-100 text-blue-800';
      case 'past_due': return 'bg-red-100 text-red-800';
      case 'canceled': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'border-red-200 bg-red-50 text-red-800';
      case 'medium': return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'low': return 'border-blue-200 bg-blue-50 text-blue-800';
      default: return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Billing Dashboard</h1>
          <p className="text-gray-600">Manage your subscription and usage</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => window.location.reload()}>
            <Settings className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert, index) => (
            <Alert key={index} className={getSeverityColor(alert.severity)}>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="font-medium">{alert.message}</div>
                <div className="text-sm mt-1">{alert.action}</div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
          <TabsTrigger value="plans">Plans</TabsTrigger>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Current Plan */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Current Plan</CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {billingData?.plan?.display_name || 'No Plan'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {billingData?.plan ? formatCurrency(billingData.plan.price, billingData.plan.currency) : 'Free'}
                  {billingData?.plan?.billing_interval && ` / ${billingData.plan.billing_interval}`}
                </p>
                {billingData?.subscription && (
                  <Badge className={`mt-2 ${getStatusColor(billingData.subscription.status)}`}>
                    {billingData.subscription.status}
                  </Badge>
                )}
              </CardContent>
            </Card>

            {/* Usage Overview */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">AI Requests</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {billingData?.usage.ai_requests || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  of {billingData?.usage.plan_limits.ai_requests || 0} limit
                </p>
                <Progress 
                  value={billingData?.usage.usage_percentage.ai_requests || 0} 
                  className="mt-2"
                />
              </CardContent>
            </Card>

            {/* Content Posts */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Content Posts</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {billingData?.usage.content_posts || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  of {billingData?.usage.plan_limits.content_posts || 0} limit
                </p>
                <Progress 
                  value={billingData?.usage.usage_percentage.content_posts || 0} 
                  className="mt-2"
                />
              </CardContent>
            </Card>

            {/* Team Members */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Team Members</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {billingData?.usage.team_members || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  of {billingData?.usage.plan_limits.team_members || 0} limit
                </p>
                <Progress 
                  value={billingData?.usage.usage_percentage.team_members || 0} 
                  className="mt-2"
                />
              </CardContent>
            </Card>
          </div>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Subscription Actions</CardTitle>
              <CardDescription>
                Manage your subscription and billing
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                {billingData?.can_upgrade && (
                  <Button onClick={handleUpgrade} className="flex-1">
                    Upgrade Plan
                  </Button>
                )}
                {billingData?.can_downgrade && (
                  <Button variant="outline" className="flex-1">
                    Downgrade Plan
                  </Button>
                )}
                {billingData?.subscription && (
                  <Button variant="outline" onClick={handleCancel}>
                    Cancel Subscription
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="usage" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Usage Details</CardTitle>
              <CardDescription>
                Current month usage breakdown
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {billingData?.usage && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">AI Requests</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Used</span>
                        <span>{billingData.usage.ai_requests} / {billingData.usage.plan_limits.ai_requests}</span>
                      </div>
                      <Progress value={billingData.usage.usage_percentage.ai_requests} />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-medium">Content Posts</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Used</span>
                        <span>{billingData.usage.content_posts} / {billingData.usage.plan_limits.content_posts}</span>
                      </div>
                      <Progress value={billingData.usage.usage_percentage.content_posts} />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-medium">Team Members</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Used</span>
                        <span>{billingData.usage.team_members} / {billingData.usage.plan_limits.team_members}</span>
                      </div>
                      <Progress value={billingData.usage.usage_percentage.team_members} />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-medium">Integrations</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Used</span>
                        <span>{billingData.usage.integrations} / {billingData.usage.plan_limits.integrations}</span>
                      </div>
                      <Progress value={billingData.usage.usage_percentage.integrations} />
                    </div>
                  </div>
                </div>
              )}

              {billingData?.usage?.overage?.amount && billingData.usage.overage.amount > 0 && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="font-medium">Overage Charges</div>
                    <div className="text-sm mt-1">
                      You have {formatCurrency(billingData.usage.overage.amount)} in overage charges this month.
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="plans" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Available Plans</CardTitle>
              <CardDescription>
                Choose the plan that best fits your needs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <p className="text-gray-500">Plan comparison will be loaded here</p>
                <Button className="mt-4" onClick={() => fetch('/api/v1/billing/plans')}>
                  Load Plans
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="invoices" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Billing History</CardTitle>
              <CardDescription>
                View and download your invoices
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <p className="text-gray-500">Invoice history will be loaded here</p>
                <Button className="mt-4" onClick={() => fetch('/api/v1/billing/invoices')}>
                  Load Invoices
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
