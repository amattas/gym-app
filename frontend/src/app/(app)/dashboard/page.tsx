"use client";

import { useEffect, useState } from "react";
import { BarChart3, Calendar, TrendingUp, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

interface DashboardStats {
  total_clients: number;
  active_memberships: number;
  schedules_today: number;
  check_ins_today: number;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    const gymId = localStorage.getItem("gym_id");
    if (gymId) {
      api
        .get<{ data: DashboardStats }>(
          `/v1/gyms/${gymId}/analytics/dashboard?period=30`
        )
        .then((res) => setStats(res.data))
        .catch(() => {});
    }
  }, []);

  const cards = [
    {
      title: "Total Clients",
      value: stats?.total_clients ?? "—",
      icon: Users,
    },
    {
      title: "Active Memberships",
      value: stats?.active_memberships ?? "—",
      icon: TrendingUp,
    },
    {
      title: "Schedules Today",
      value: stats?.schedules_today ?? "—",
      icon: Calendar,
    },
    {
      title: "Check-ins Today",
      value: stats?.check_ins_today ?? "—",
      icon: BarChart3,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.first_name}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {card.title}
              </CardTitle>
              <card.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
