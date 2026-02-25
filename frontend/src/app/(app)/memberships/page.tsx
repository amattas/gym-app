"use client";

import { useEffect, useState } from "react";
import { CreditCard } from "lucide-react";
import { Badge } from "@/components/ui/badge";
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

interface PlanTemplate {
  plan_template_id: string;
  name: string;
  plan_type: string;
  status: string;
}

export default function MembershipsPage() {
  const [templates, setTemplates] = useState<PlanTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ data: PlanTemplate[] }>("/v1/plan-templates")
      .then((res) => setTemplates(res.data))
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

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

      <Tabs defaultValue="templates">
        <TabsList>
          <TabsTrigger value="templates">Plan Templates</TabsTrigger>
        </TabsList>

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
