import { useState, useEffect, useCallback } from 'react';
import { apiService, DashboardStats, RecentActivity, AnalyticsData } from '@/lib/api';

export interface RealtimeData {
  stats: DashboardStats | null;
  activity: RecentActivity[];
  analytics: AnalyticsData | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export function useRealtimeData(intervalMs: number = 30000) {
  const [data, setData] = useState<RealtimeData>({
    stats: null,
    activity: [],
    analytics: null,
    loading: true,
    error: null,
    lastUpdated: null,
  });

  const fetchData = useCallback(async () => {
    try {
      setData(prev => ({ ...prev, loading: true, error: null }));

      const [statsResponse, activityResponse, analyticsResponse] = await Promise.allSettled([
        apiService.getDashboardStats(),
        apiService.getRecentActivity(),
        apiService.getAnalytics('7d'),
      ]);

      const newData: RealtimeData = {
        stats: statsResponse.status === 'fulfilled' ? statsResponse.value.data : null,
        activity: activityResponse.status === 'fulfilled' ? activityResponse.value.data : [],
        analytics: analyticsResponse.status === 'fulfilled' ? analyticsResponse.value.data : null,
        loading: false,
        error: null,
        lastUpdated: new Date(),
      };

      setData(newData);
    } catch (error) {
      setData(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch data',
      }));
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Set up interval for real-time updates
    const interval = setInterval(fetchData, intervalMs);

    return () => clearInterval(interval);
  }, [fetchData, intervalMs]);

  const refresh = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    ...data,
    refresh,
  };
}

// Hook for specific data types
export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getDashboardStats();
      setStats(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchStats]);

  return { stats, loading, error, refresh: fetchStats };
}

export function useRecentActivity() {
  const [activity, setActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActivity = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getRecentActivity();
      setActivity(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch activity');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActivity();
    const interval = setInterval(fetchActivity, 15000); // Refresh every 15 seconds
    return () => clearInterval(interval);
  }, [fetchActivity]);

  return { activity, loading, error, refresh: fetchActivity };
}
