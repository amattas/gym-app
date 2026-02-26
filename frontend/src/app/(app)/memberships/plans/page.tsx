"use client";

import { useEffect, useState } from "react";
import { CreditCard, Loader2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface PlanTemplate {
  plan_template_id: string;
  name: string;
  description: string | null;
  plan_type: string;
  status: string;
  visit_entitlement: Record<string, unknown> | null;
  plan_duration: Record<string, unknown> | null;
  is_addon: boolean;
  created_at: string;
}

export default function PlanTemplatesPage() {
  const [templates, setTemplates] = useState<PlanTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [planType, setPlanType] = useState("membership");
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    api
      .get<{ data: PlanTemplate[] }>("/v1/plan-templates")
      .then((res) => setTemplates(res.data))
      .catch((err) => { toast.error(err instanceof Error ? err.message : "Failed to load plan templates"); })
      .finally(() => setIsLoading(false));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post("/v1/plan-templates", { name, plan_type: planType });
      toast.success("Plan template created");
      setShowCreate(false);
      setName("");
      const res = await api.get<{ data: PlanTemplate[] }>("/v1/plan-templates");
      setTemplates(res.data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create");
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <CreditCard className="h-8 w-8 text-muted-foreground" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Plan Templates</h1>
            <p className="text-muted-foreground">Manage membership plan templates</p>
          </div>
        </div>
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" /> New Template
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Plan Template</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label>Plan Type</Label>
                <Select value={planType} onValueChange={setPlanType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="membership">Membership</SelectItem>
                    <SelectItem value="punch_card">Punch Card</SelectItem>
                    <SelectItem value="drop_in">Drop In</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" disabled={isCreating || !name} className="w-full">
                {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Add-on</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : templates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
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
                    <Badge variant={t.status === "active" ? "default" : "secondary"}>
                      {t.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{t.is_addon ? "Yes" : "No"}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
