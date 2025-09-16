"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface RetentionPolicy {
  messages_days: number;
  logs_days: number;
  metrics_days: number;
  created_at: string;
  updated_at: string;
}

interface PrivacyJob {
  id: string;
  job_type: string;
  status: string;
  file_url?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

interface ExportRequest {
  include_media: boolean;
  format: string;
}

interface DeleteRequest {
  confirm_org_name: string;
  delete_media: boolean;
  grace_period_days: number;
}

export default function PrivacyPage() {
  const [retentionPolicy, setRetentionPolicy] = useState<RetentionPolicy | null>(null);
  const [privacyJobs, setPrivacyJobs] = useState<PrivacyJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteForm, setDeleteForm] = useState<DeleteRequest>({
    confirm_org_name: "",
    delete_media: false,
    grace_period_days: 7
  });
  const [exportForm, setExportForm] = useState<ExportRequest>({
    include_media: true,
    format: "both"
  });
  const [orgName, setOrgName] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [retentionResponse, jobsResponse] = await Promise.all([
        api.get<RetentionPolicy>("/privacy/retention"),
        api.get<{ jobs: PrivacyJob[] }>("/privacy/jobs")
      ]);
      
      setRetentionPolicy(retentionResponse.data);
      setPrivacyJobs(jobsResponse.data.jobs);
      
      // Get org name for delete confirmation
      const orgResponse = await api.get<{ name: string }>("/orgs");
      setOrgName(orgResponse.data.name);
    } catch (error) {
      console.error("Failed to fetch privacy data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRetentionUpdate = async (field: keyof RetentionPolicy, value: number) => {
    if (!retentionPolicy) return;
    
    try {
      setSaving(true);
      const updateData: Partial<RetentionPolicy> = {};
      (updateData as any)[field] = value;
      
      await api.put("/privacy/retention", updateData);
      setRetentionPolicy({ ...retentionPolicy, ...updateData });
    } catch (error) {
      console.error("Failed to update retention policy:", error);
      alert("Failed to update retention policy. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async () => {
    try {
      setExportLoading(true);
      const response = await api.post("/privacy/export", exportForm);
      alert("Export job started. You'll be notified when it's ready.");
      fetchData(); // Refresh jobs list
    } catch (error) {
      console.error("Failed to start export:", error);
      alert("Failed to start export. Please try again.");
    } finally {
      setExportLoading(false);
    }
  };

  const handleDelete = async () => {
    if (deleteForm.confirm_org_name !== orgName) {
      alert("Organization name does not match. Please check and try again.");
      return;
    }

    try {
      setDeleteLoading(true);
      await api.post("/privacy/delete", deleteForm);
      alert("Deletion job started. Your data will be deleted after the grace period.");
      setShowDeleteModal(false);
      fetchData(); // Refresh jobs list
    } catch (error) {
      console.error("Failed to start deletion:", error);
      alert("Failed to start deletion. Please try again.");
    } finally {
      setDeleteLoading(false);
    }
  };

  const downloadExport = (job: PrivacyJob) => {
    if (job.file_url) {
      window.open(job.file_url, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Privacy & Data Management</h1>
        <p className="text-gray-600 mt-2">
          Manage your data retention policies, export your data, or delete your organization
        </p>
      </div>

      {/* Data Retention Policy */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Retention Policy</h2>
        <p className="text-gray-600 mb-6">
          Configure how long different types of data are kept before being automatically purged.
        </p>
        
        {retentionPolicy && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Messages Retention (days)
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    min="1"
                    max="3650"
                    value={retentionPolicy.messages_days}
                    onChange={(e) => handleRetentionUpdate('messages_days', parseInt(e.target.value))}
                    disabled={saving}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-500">days</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  How long to keep conversation messages
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Audit Logs Retention (days)
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    min="1"
                    max="3650"
                    value={retentionPolicy.logs_days}
                    onChange={(e) => handleRetentionUpdate('logs_days', parseInt(e.target.value))}
                    disabled={saving}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-500">days</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  How long to keep system audit logs
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Metrics Retention (days)
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    min="1"
                    max="3650"
                    value={retentionPolicy.metrics_days}
                    onChange={(e) => handleRetentionUpdate('metrics_days', parseInt(e.target.value))}
                    disabled={saving}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-500">days</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  How long to keep performance metrics
                </p>
              </div>
            </div>
            
            <div className="text-sm text-gray-500">
              Last updated: {new Date(retentionPolicy.updated_at).toLocaleString()}
            </div>
          </div>
        )}
      </div>

      {/* Data Export */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Export Your Data</h2>
        <p className="text-gray-600 mb-6">
          Download a copy of all your organization's data in JSON and CSV formats.
        </p>
        
        <div className="space-y-4">
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={exportForm.include_media}
                onChange={(e) => setExportForm({ ...exportForm, include_media: e.target.checked })}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Include media files and URLs</span>
            </label>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Export Format
            </label>
            <select
              value={exportForm.format}
              onChange={(e) => setExportForm({ ...exportForm, format: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="json">JSON only</option>
              <option value="csv">CSV only</option>
              <option value="both">Both JSON and CSV</option>
            </select>
          </div>
          
          <button
            onClick={handleExport}
            disabled={exportLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {exportLoading ? "Starting Export..." : "Start Export"}
          </button>
        </div>
      </div>

      {/* Data Deletion */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h2 className="text-xl font-semibold text-red-600 mb-4">Delete Organization</h2>
        <p className="text-gray-600 mb-6">
          <strong className="text-red-600">Warning:</strong> This action is irreversible. 
          All your data will be permanently deleted after the grace period.
        </p>
        
        <button
          onClick={() => setShowDeleteModal(true)}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Delete Organization
        </button>
      </div>

      {/* Privacy Jobs History */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Privacy Jobs</h2>
        
        {privacyJobs.length === 0 ? (
          <p className="text-gray-500">No privacy jobs found.</p>
        ) : (
          <div className="space-y-4">
            {privacyJobs.map((job) => (
              <div key={job.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">
                        {job.job_type === 'export' ? 'Data Export' : 'Data Deletion'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        job.status === 'completed' ? 'bg-green-100 text-green-800' :
                        job.status === 'failed' ? 'bg-red-100 text-red-800' :
                        job.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {job.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      Created: {new Date(job.created_at).toLocaleString()}
                      {job.completed_at && (
                        <span> • Completed: {new Date(job.completed_at).toLocaleString()}</span>
                      )}
                    </div>
                    {job.error_message && (
                      <div className="text-sm text-red-600 mt-1">
                        Error: {job.error_message}
                      </div>
                    )}
                  </div>
                  
                  {job.status === 'completed' && job.file_url && (
                    <button
                      onClick={() => downloadExport(job)}
                      className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                    >
                      Download
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-red-600 mb-4">
              Confirm Organization Deletion
            </h3>
            
            <div className="space-y-4">
              <p className="text-gray-600">
                This action will permanently delete all data for your organization. 
                This cannot be undone.
              </p>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Grace Period (days)
                </label>
                <input
                  type="number"
                  min="0"
                  max="30"
                  value={deleteForm.grace_period_days}
                  onChange={(e) => setDeleteForm({ ...deleteForm, grace_period_days: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Data will be deleted after this many days
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Organization Name
                </label>
                <input
                  type="text"
                  value={deleteForm.confirm_org_name}
                  onChange={(e) => setDeleteForm({ ...deleteForm, confirm_org_name: e.target.value })}
                  placeholder={`Type "${orgName}" to confirm`}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                />
              </div>
              
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={deleteForm.delete_media}
                    onChange={(e) => setDeleteForm({ ...deleteForm, delete_media: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Also delete media files</span>
                </label>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleteLoading || deleteForm.confirm_org_name !== orgName}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                {deleteLoading ? "Deleting..." : "Delete Organization"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
