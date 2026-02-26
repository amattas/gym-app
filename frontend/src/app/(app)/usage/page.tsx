"use client";

import { useEffect, useState } from "react";
import { BarChart3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface MetricTotal {
  metric_name: string;
  total: number;
  limit: number | null;
}

export default function UsagePage() {
  const [totals, setTotals] = useState<MetricTotal[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ data: MetricTotal[] }>("/v1/usage/totals")
      .then((res) => setTotals(res.data))
      .catch((err) => { toast.error(err instanceof Error ? err.message : "Failed to load usage data"); })
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <BarChart3 className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Usage</h1>
          <p className="text-muted-foreground">Gym usage metering dashboard</p>
        </div>
      </div>

      {totals.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center py-8">
            <p className="text-muted-foreground">No usage data available</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {totals.map((m) => (
            <Card key={m.metric_name}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium capitalize">
                  {m.metric_name.replace(/_/g, " ")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{m.total}</div>
                {m.limit && (
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-sm text-muted-foreground">
                      of {m.limit} limit
                    </span>
                    <Badge
                      variant={m.total < m.limit ? "default" : "destructive"}
                    >
                      {Math.round((m.total / m.limit) * 100)}%
                    </Badge>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
