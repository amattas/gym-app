"use client";

import { useEffect, useState } from "react";
import { BarChart3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface DashboardData {
  total_clients: number;
  active_memberships: number;
  new_clients_this_period: number;
  total_workouts: number;
  total_check_ins: number;
}

export default function AnalyticsPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      const gymId = localStorage.getItem("gym_id");
      if (!gymId) return;
      try {
        const res = await api.get<{ data: DashboardData }>(
          `/v1/gyms/${gymId}/analytics/dashboard?period=30`
        );
        setData(res.data);
      } catch {}
    };
    load().finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const metrics = data
    ? [
        { label: "Total Clients", value: data.total_clients },
        { label: "Active Memberships", value: data.active_memberships },
        { label: "New Clients (30d)", value: data.new_clients_this_period },
        { label: "Workouts (30d)", value: data.total_workouts },
        { label: "Check-ins (30d)", value: data.total_check_ins },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <BarChart3 className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Gym performance metrics (last 30 days)
          </p>
        </div>
      </div>

      {data ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {metrics.map((m) => (
            <Card key={m.label}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {m.label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{m.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <p className="text-center text-muted-foreground py-16">
          No analytics data available
        </p>
      )}
    </div>
  );
}
