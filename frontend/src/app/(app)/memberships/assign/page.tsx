"use client";

import { useEffect, useState } from "react";
import { CreditCard, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface PlanTemplate {
  plan_template_id: string;
  name: string;
  plan_type: string;
}

export default function AssignMembershipPage() {
  const [templates, setTemplates] = useState<PlanTemplate[]>([]);
  const [clientId, setClientId] = useState("");
  const [templateId, setTemplateId] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    api
      .get<{ data: PlanTemplate[] }>("/v1/plan-templates?status=active")
      .then((res) => setTemplates(res.data))
      .catch(() => {});
  }, []);

  async function handleAssign(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId || !templateId) return;
    setIsLoading(true);
    try {
      await api.post(`/v1/clients/${clientId}/memberships`, {
        plan_template_id: templateId,
      });
      toast.success("Membership assigned");
      setClientId("");
      setTemplateId("");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to assign");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <CreditCard className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Assign Membership</h1>
          <p className="text-muted-foreground">Assign a membership plan to a client</p>
        </div>
      </div>

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle>New Assignment</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAssign} className="space-y-4">
            <div className="space-y-2">
              <Label>Client ID</Label>
              <Input
                placeholder="Enter client UUID"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Plan Template</Label>
              <Select value={templateId} onValueChange={setTemplateId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a plan" />
                </SelectTrigger>
                <SelectContent>
                  {templates.map((t) => (
                    <SelectItem key={t.plan_template_id} value={t.plan_template_id}>
                      {t.name} ({t.plan_type})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" disabled={isLoading || !clientId || !templateId}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Assign Membership
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
