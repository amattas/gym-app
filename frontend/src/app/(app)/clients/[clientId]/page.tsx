"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Mail, Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Client {
  client_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  date_of_birth: string | null;
  gender: string | null;
  status: string;
  notes: string | null;
  created_at: string;
}

interface Goal {
  goal_id: string;
  goal_type: string;
  target_value: number | null;
  current_value: number | null;
  status: string;
}

interface Measurement {
  measurement_id: string;
  measurement_type: string;
  value: number;
  unit: string;
  measured_at: string;
}

export default function ClientDetailPage() {
  const params = useParams();
  const router = useRouter();
  const clientId = params.clientId as string;
  const [client, setClient] = useState<Client | null>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [measurements, setMeasurements] = useState<Measurement[]>([]);

  useEffect(() => {
    api
      .get<{ data: Client }>(`/v1/clients/${clientId}`)
      .then((res) => setClient(res.data))
      .catch(() => router.push("/clients"));

    api
      .get<{ data: Goal[] }>(`/v1/clients/${clientId}/goals`)
      .then((res) => setGoals(res.data))
      .catch((err) => {
        toast.error(err instanceof Error ? err.message : "Failed to load goals");
      });

    api
      .get<{ data: Measurement[] }>(`/v1/clients/${clientId}/measurements`)
      .then((res) => setMeasurements(res.data))
      .catch((err) => {
        toast.error(err instanceof Error ? err.message : "Failed to load measurements");
      });
  }, [clientId, router]);

  if (!client) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/clients")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">
            {client.first_name} {client.last_name}
          </h1>
          <div className="flex items-center gap-4 text-muted-foreground">
            {client.email && (
              <span className="flex items-center gap-1">
                <Mail className="h-3 w-3" /> {client.email}
              </span>
            )}
            {client.phone && (
              <span className="flex items-center gap-1">
                <Phone className="h-3 w-3" /> {client.phone}
              </span>
            )}
          </div>
        </div>
        <Badge variant={client.status === "active" ? "default" : "secondary"}>
          {client.status}
        </Badge>
      </div>

      <Separator />

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="goals">Goals</TabsTrigger>
          <TabsTrigger value="measurements">Measurements</TabsTrigger>
          <TabsTrigger value="workouts">Workouts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">
                  Personal Info
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Date of Birth</span>
                  <span>{client.date_of_birth || "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Gender</span>
                  <span>{client.gender || "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Member Since</span>
                  <span>
                    {new Date(client.created_at).toLocaleDateString()}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {client.notes || "No notes yet."}
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="goals" className="space-y-4">
          {goals.length === 0 ? (
            <p className="text-muted-foreground py-8 text-center">
              No goals set
            </p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {goals.map((goal) => (
                <Card key={goal.goal_id}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">
                      {goal.goal_type}
                    </CardTitle>
                    <Badge variant="outline">{goal.status}</Badge>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {goal.current_value != null && goal.target_value != null
                        ? `${goal.current_value} / ${goal.target_value}`
                        : "No target set"}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="measurements" className="space-y-4">
          {measurements.length === 0 ? (
            <p className="text-muted-foreground py-8 text-center">
              No measurements recorded
            </p>
          ) : (
            <div className="grid gap-4 md:grid-cols-3">
              {measurements.map((m) => (
                <Card key={m.measurement_id}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">
                      {m.measurement_type}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {m.value} {m.unit}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(m.measured_at).toLocaleDateString()}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="workouts">
          <p className="text-muted-foreground py-8 text-center">
            Workout history coming in the next release
          </p>
        </TabsContent>
      </Tabs>
    </div>
  );
}
