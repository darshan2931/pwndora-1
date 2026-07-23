'use client';

import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api } from '@/services/api';

interface DashboardData {
  profile: any;
  roadmap: any[];
  roadmapId: string | null;
  mentorContext: any;
  weeklyProgress: any[];
  dailyMission: any;
}

const DashboardDataContext = createContext<{
  data: DashboardData | null;
  loading: boolean;
  refresh: () => Promise<void>;
}>({ data: null, loading: true, refresh: async () => {} });

export function useDashboardData() {
  return useContext(DashboardDataContext);
}

export default function DashboardDataProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const d = await api.getDashboardData();
      setData(d?.data || null);
    } catch (e) {
      console.error('Failed to load dashboard data', e);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <DashboardDataContext.Provider value={{ data, loading, refresh: load }}>
      {children}
    </DashboardDataContext.Provider>
  );
}
