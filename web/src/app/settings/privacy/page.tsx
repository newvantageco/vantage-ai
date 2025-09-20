"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  DownloadIcon,
  TrashIcon,
  AlertTriangleIcon,
  CheckIcon,
  XIcon,
  ClockIcon,
  FileTextIcon,
  ShieldIcon,
  Loader2Icon,
  ExternalLinkIcon,
  InfoIcon
} from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface DataSummary {
  organization_id: string;
  organization_name: string;
  data_summary: {
    users: number;
    channels: number;
    posts: number;
    analytics_events: number;
    subscriptions: number;
    invoices: number;
  };
  oldest_data: string | null;
  data_retention_policy: string;
  last_export: string | null;
  last_deletion_request: string | null;
}

interface Export {
  id: string;
  format_type: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  expires_at: string;
  file_size: number | null;
  error_message: string | null;
}

interface DeletionRequest {
  id: string;
  reason: string;
  status: string;
  created_at: string;
  scheduled_for: string;
  completed_at: string | null;
  canceled_at: string | null;
  error_message: string | null;
}

export default function PrivacyPage() {
  const [dataSummary, setDataSummary] = useState<DataSummary | null>(null);
  const [exports, setExports] = useState<Export[]>([]);
  const [deletions, setDeletions] = useState<DeletionRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [exportFormat, setExportFormat] = useState("json");

  // Fetch privacy data
  useEffect(() => {
    const fetchPrivacyData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [summaryRes, exportsRes, deletionsRes] = await Promise.all([
          fetch('/api/v1/privacy/summary'),
          fetch('/api/v1/privacy/exports?limit=10'),
          fetch('/api/v1/privacy/deletions?limit=10')
        ]);

        if (!summaryRes.ok || !exportsRes.ok || !deletionsRes.ok) {
          throw new Error('Failed to fetch privacy data');
        }

        const [summaryData, exportsData, deletionsData] = await Promise.all([
          summaryRes.json(),
          exportsRes.json(),
          deletionsRes.json()
        ]);

        setDataSummary(summaryData);
        setExports(exportsData.exports);
        setDeletions(deletionsData.deletions);

      } catch (err) {
        console.error('Error fetching privacy data:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchPrivacyData();
  }, []);

  // Handle data export
  const handleExport = async () => {
    try {
      setExporting(true);
      
      const response = await fetch('/api/v1/privacy/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format_type: exportFormat
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create export');
      }

      const data = await response.json();
      
      // Refresh exports list
      const exportsRes = await fetch('/api/v1/privacy/exports?limit=10');
      if (exportsRes.ok) {
        const exportsData = await exportsRes.json();
        setExports(exportsData.exports);
      }

      // Show success message
      alert(`Export started! Job ID: ${data.job_id}`);

    } catch (err) {
      console.error('Error creating export:', err);
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setExporting(false);
    }
  };

  // Handle data deletion
  const handleDelete = async (reason: string) => {
    try {
      setDeleting(true);
      
      const response = await fetch('/api/v1/privacy/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          reason: reason
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create deletion request');
      }

      const data = await response.json();
      
      // Refresh deletions list
      const deletionsRes = await fetch('/api/v1/privacy/deletions?limit=10');
      if (deletionsRes.ok) {
        const deletionsData = await deletionsRes.json();
        setDeletions(deletionsData.deletions);
      }

      // Show success message
      alert(`Deletion request created! This will be processed in 24 hours. Request ID: ${data.deletion_id}`);

    } catch (err) {
      console.error('Error creating deletion request:', err);
      setError(err instanceof Error ? err.message : 'Deletion request failed');
    } finally {
      setDeleting(false);
    }
  };

  // Handle export download
  const handleDownload = async (exportId: string) => {
    try {
      const response = await fetch(`/api/v1/privacy/export/${exportId}/download`);
      
      if (!response.ok) {
        throw new Error('Failed to download export');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `data_export_${exportId}.${exportFormat}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (err) {
      console.error('Error downloading export:', err);
      setError(err instanceof Error ? err.message : 'Download failed');
    }
  };

  // Format file size
  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return "Unknown";
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + " " + sizes[i];
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get status badge
  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { color: "bg-yellow-100 text-yellow-800", icon: ClockIcon },
      processing: { color: "bg-blue-100 text-blue-800", icon: Loader2Icon },
      completed: { color: "bg-green-100 text-green-800", icon: CheckIcon },
      failed: { color: "bg-red-100 text-red-800", icon: XIcon },
      canceled: { color: "bg-gray-100 text-gray-800", icon: XIcon }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    const IconComponent = config.icon;
    
    return (
      <Badge className={config.color}>
        <IconComponent className="h-3 w-3 mr-1" />
        {status}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 p-6">
        <div className="max-w-4xl mx-auto flex items-center justify-center h-96">
          <div className="text-center">
            <Loader2Icon className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading privacy settings...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Privacy & Data</h1>
            <p className="text-slate-600 text-lg mt-2">
              Manage your data export and deletion requests
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <ShieldIcon className="h-6 w-6 text-blue-500" />
            <span className="text-sm text-gray-600">GDPR Compliant</span>
          </div>
        </div>

        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Data Summary */}
        {dataSummary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileTextIcon className="h-5 w-5 mr-2" />
                Data Summary
              </CardTitle>
              <CardDescription>
                Overview of your organization's data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{dataSummary.data_summary.users}</div>
                  <div className="text-sm text-gray-600">Users</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{dataSummary.data_summary.posts}</div>
                  <div className="text-sm text-gray-600">Posts</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{dataSummary.data_summary.analytics_events}</div>
                  <div className="text-sm text-gray-600">Analytics Events</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{dataSummary.data_summary.channels}</div>
                  <div className="text-sm text-gray-600">Channels</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{dataSummary.data_summary.subscriptions}</div>
                  <div className="text-sm text-gray-600">Subscriptions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-indigo-600">{dataSummary.data_summary.invoices}</div>
                  <div className="text-sm text-gray-600">Invoices</div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold mb-2">Data Retention Policy</h4>
                <p className="text-sm text-gray-600">{dataSummary.data_retention_policy}</p>
                {dataSummary.oldest_data && (
                  <p className="text-sm text-gray-500 mt-2">
                    Oldest data: {formatDate(dataSummary.oldest_data)}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Data Export */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <DownloadIcon className="h-5 w-5 mr-2" />
              Data Export
            </CardTitle>
            <CardDescription>
              Download a copy of your organization's data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4">
              <div>
                <label className="text-sm font-medium">Export Format</label>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="json">JSON</option>
                  <option value="csv">CSV</option>
                  <option value="zip">ZIP (Multiple formats)</option>
                </select>
              </div>
              <Button
                onClick={handleExport}
                disabled={exporting}
                className="mt-6"
              >
                {exporting ? (
                  <Loader2Icon className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <DownloadIcon className="h-4 w-4 mr-2" />
                )}
                {exporting ? "Creating Export..." : "Export Data"}
              </Button>
            </div>
            
            <div className="text-sm text-gray-600">
              <InfoIcon className="h-4 w-4 inline mr-1" />
              Exports are available for 7 days and include all your organization's data in the selected format.
            </div>
          </CardContent>
        </Card>

        {/* Export History */}
        {exports.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Export History</CardTitle>
              <CardDescription>
                Your recent data exports
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {exports.map((export_item) => (
                  <div key={export_item.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileTextIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <div className="font-medium">
                          Export {export_item.id.slice(0, 8)}...
                        </div>
                        <div className="text-sm text-gray-600">
                          {export_item.format_type.toUpperCase()} • {formatDate(export_item.created_at)}
                          {export_item.file_size && ` • ${formatFileSize(export_item.file_size)}`}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusBadge(export_item.status)}
                      {export_item.status === "completed" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(export_item.id)}
                        >
                          <DownloadIcon className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Data Deletion */}
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center text-red-600">
              <TrashIcon className="h-5 w-5 mr-2" />
              Data Deletion
            </CardTitle>
            <CardDescription>
              Permanently delete all your organization's data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertTriangleIcon className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                <strong>Warning:</strong> This action cannot be undone. All your data will be permanently deleted after a 24-hour grace period.
              </AlertDescription>
            </Alert>
            
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" disabled={deleting}>
                  {deleting ? (
                    <Loader2Icon className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <TrashIcon className="h-4 w-4 mr-2" />
                  )}
                  {deleting ? "Processing..." : "Delete All Data"}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action will permanently delete all data for your organization, including:
                    <ul className="list-disc list-inside mt-2 space-y-1">
                      <li>All user accounts and profiles</li>
                      <li>All posts and content</li>
                      <li>All analytics data</li>
                      <li>All billing and subscription information</li>
                      <li>All integrations and settings</li>
                    </ul>
                    <br />
                    This action cannot be undone. You will have 24 hours to cancel this request.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={() => handleDelete("User requested data deletion")}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    Yes, delete all data
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </CardContent>
        </Card>

        {/* Deletion History */}
        {deletions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Deletion Requests</CardTitle>
              <CardDescription>
                Your data deletion requests
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {deletions.map((deletion) => (
                  <div key={deletion.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <TrashIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <div className="font-medium">
                          Deletion Request {deletion.id.slice(0, 8)}...
                        </div>
                        <div className="text-sm text-gray-600">
                          {formatDate(deletion.created_at)}
                          {deletion.reason && ` • ${deletion.reason}`}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusBadge(deletion.status)}
                      {deletion.status === "pending" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            // TODO: Implement cancel deletion
                            alert("Cancel deletion functionality not implemented yet");
                          }}
                        >
                          <XIcon className="h-4 w-4 mr-1" />
                          Cancel
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
