"use client";

import { useEffect, useState, useCallback } from "react";
import { CreditCard, Pause, XCircle, Play } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface PlanTemplate {
  plan_template_id: string;
  name: string;
  plan_type: string;
  status: string;
}

interface Membership {
  client_membership_id: string;
  client_id: string;
  plan_type: string;
  status: string;
  started_at: string;
  expires_at: string | null;
}

export default function MembershipsPage() {
  const [templates, setTemplates] = useState<PlanTemplate[]>([]);
  const [memberships, setMemberships] = useState<Membership[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [membershipsLoading, setMembershipsLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ data: PlanTemplate[] }>("/v1/plan-templates")
      .then((res) => setTemplates(res.data))
      .catch((err) => {
        toast.error(
          err instanceof Error ? err.message : "Failed to load plan templates"
        );
      })
      .finally(() => setIsLoading(false));
  }, []);

  const fetchMemberships = useCallback(async () => {
    setMembershipsLoading(true);
    try {
      const res = await api.get<{ data: Membership[] }>("/v1/memberships");
      setMemberships(res.data);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to load memberships"
      );
    } finally {
      setMembershipsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMemberships();
  }, [fetchMemberships]);

  async function handlePause(id: string) {
    try {
      await api.post(`/v1/memberships/${id}/pause`);
      toast.success("Membership paused");
      fetchMemberships();
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to pause membership"
      );
    }
  }

  async function handleUnpause(id: string) {
    try {
      await api.post(`/v1/memberships/${id}/unpause`);
      toast.success("Membership resumed");
      fetchMemberships();
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to resume membership"
      );
    }
  }

  async function handleCancel(id: string) {
    try {
      await api.post(`/v1/memberships/${id}/cancel`);
      toast.success("Membership cancelled");
      fetchMemberships();
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to cancel membership"
      );
    }
  }

  const statusVariant = (status: string) => {
    switch (status) {
      case "active":
      case "trial":
        return "default" as const;
      case "paused":
        return "secondary" as const;
      case "cancelled":
      case "expired":
        return "destructive" as const;
      default:
        return "outline" as const;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <CreditCard className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Memberships</h1>
          <p className="text-muted-foreground">
            Plan templates and member subscriptions
          </p>
        </div>
      </div>

      <Tabs defaultValue="memberships">
        <TabsList>
          <TabsTrigger value="memberships">Active Memberships</TabsTrigger>
          <TabsTrigger value="templates">Plan Templates</TabsTrigger>
        </TabsList>

        <TabsContent value="memberships">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Client</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Started</TableHead>
                  <TableHead>Expires</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {membershipsLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8">
                      Loading...
                    </TableCell>
                  </TableRow>
                ) : memberships.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8">
                      No memberships found
                    </TableCell>
                  </TableRow>
                ) : (
                  memberships.map((m) => (
                    <TableRow key={m.client_membership_id}>
                      <TableCell className="font-mono text-sm">
                        {m.client_id.slice(0, 8)}...
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{m.plan_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusVariant(m.status)}>
                          {m.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {new Date(m.started_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {m.expires_at
                          ? new Date(m.expires_at).toLocaleDateString()
                          : "\u2014"}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {(m.status === "active" || m.status === "trial") && (
                            <>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() =>
                                  handlePause(m.client_membership_id)
                                }
                              >
                                <Pause className="h-3 w-3 mr-1" />
                                Pause
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() =>
                                  handleCancel(m.client_membership_id)
                                }
                              >
                                <XCircle className="h-3 w-3 mr-1" />
                                Cancel
                              </Button>
                            </>
                          )}
                          {m.status === "paused" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                handleUnpause(m.client_membership_id)
                              }
                            >
                              <Play className="h-3 w-3 mr-1" />
                              Resume
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        <TabsContent value="templates">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center py-8">
                      Loading...
                    </TableCell>
                  </TableRow>
                ) : templates.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center py-8">
                      No plan templates found
                    </TableCell>
                  </TableRow>
                ) : (
                  templates.map((t) => (
                    <TableRow key={t.plan_template_id}>
                      <TableCell className="font-medium">{t.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{t.plan_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            t.status === "active" ? "default" : "secondary"
                          }
                        >
                          {t.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
