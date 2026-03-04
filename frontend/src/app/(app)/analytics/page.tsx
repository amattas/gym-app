"use client";

import { useEffect, useState } from "react";
import { BarChart3, Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface DashboardData {
  total_clients: number;
  active_memberships: number;
  new_clients_this_period: number;
  total_workouts: number;
  total_check_ins: number;
}

interface ClientWorkoutStats {
  total_workouts: number;
  avg_duration_minutes: number;
  completion_rate: number;
}

const DAY_OPTIONS = [7, 14, 30, 60, 90];

export default function AnalyticsPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [clientId, setClientId] = useState("");
  const [clientStats, setClientStats] = useState<ClientWorkoutStats | null>(null);
  const [clientDays, setClientDays] = useState(30);
  const [isClientLoading, setIsClientLoading] = useState(false);

  useEffect(() => {
    const gymId = localStorage.getItem("gym_id");
    if (!gymId) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    api
      .get<{ data: DashboardData }>(
        `/v1/gyms/${gymId}/analytics/dashboard?period=${days}`
      )
      .then((res) => setData(res.data))
      .catch((err) => {
        toast.error(err instanceof Error ? err.message : "Failed to load analytics");
        setData(null);
      })
      .finally(() => setIsLoading(false));
  }, [days]);

  async function handleClientSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId) return;
    setIsClientLoading(true);
    try {
      const res = await api.get<{ data: ClientWorkoutStats }>(
        `/v1/clients/${encodeURIComponent(clientId)}/analytics/workouts?days=${clientDays}`
      );
      setClientStats(res.data);
    } catch {
      toast.error("Failed to load client analytics");
      setClientStats(null);
    } finally {
      setIsClientLoading(false);
    }
  }

  useEffect(() => {
    if (!clientId) return;
    setIsClientLoading(true);
    api
      .get<{ data: ClientWorkoutStats }>(
        `/v1/clients/${encodeURIComponent(clientId)}/analytics/workouts?days=${clientDays}`
      )
      .then((res) => setClientStats(res.data))
      .catch((err) => {
        toast.error(err instanceof Error ? err.message : "Failed to load client analytics");
        setClientStats(null);
      })
      .finally(() => setIsClientLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clientDays]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <BarChart3 className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Gym performance and client metrics
          </p>
        </div>
      </div>

      <Tabs defaultValue="gym">
        <TabsList>
          <TabsTrigger value="gym">Gym Overview</TabsTrigger>
          <TabsTrigger value="client">Client Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="gym" className="space-y-4">
          <div className="flex items-center gap-2">
            {DAY_OPTIONS.map((d) => (
              <Button
                key={d}
                variant={days === d ? "default" : "outline"}
                size="sm"
                onClick={() => setDays(d)}
              >
                {d}d
              </Button>
            ))}
          </div>

          {isLoading ? (
            <div className="flex h-64 items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          ) : data ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Active Clients
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">{data.total_clients}</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Total Workouts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">{data.total_workouts}</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Check-ins
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">{data.total_check_ins}</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    New Memberships
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">
                    {data.new_clients_this_period}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Active Memberships
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">{data.active_memberships}</p>
                </CardContent>
              </Card>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-16">
              No analytics data available
            </p>
          )}
        </TabsContent>

        <TabsContent value="client" className="space-y-4">
          <Card className="max-w-lg">
            <CardHeader>
              <CardTitle>Search Client</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleClientSearch} className="flex items-end gap-4">
                <div className="flex-1 space-y-2">
                  <Label>Client ID</Label>
                  <Input
                    placeholder="Enter client UUID"
                    value={clientId}
                    onChange={(e) => setClientId(e.target.value)}
                  />
                </div>
                <Button type="submit" disabled={isClientLoading || !clientId}>
                  {isClientLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="mr-2 h-4 w-4" />
                  )}
                  Search
                </Button>
              </form>
            </CardContent>
          </Card>

          {clientStats && (
            <>
              <div className="flex items-center gap-2">
                {DAY_OPTIONS.map((d) => (
                  <Button
                    key={d}
                    variant={clientDays === d ? "default" : "outline"}
                    size="sm"
                    onClick={() => setClientDays(d)}
                  >
                    {d}d
                  </Button>
                ))}
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Total Workouts
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">
                      {clientStats.total_workouts}
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Avg Duration
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">
                      {clientStats.avg_duration_minutes}
                      <span className="text-lg text-muted-foreground ml-1">min</span>
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Completion Rate
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">
                      {clientStats.completion_rate}
                      <span className="text-lg text-muted-foreground ml-1">%</span>
                    </p>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
