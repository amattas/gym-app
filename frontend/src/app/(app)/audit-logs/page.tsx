"use client";

import { useEffect, useState } from "react";
import { Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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

interface AuditLog {
  audit_log_id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  ip_address: string | null;
  created_at: string;
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("");

  useEffect(() => {
    const params = actionFilter ? `?action=${actionFilter}` : "";
    api
      .get<{ data: AuditLog[] }>(`/v1/audit-logs${params}`)
      .then((res) => setLogs(res.data))
      .catch((err) => { toast.error(err instanceof Error ? err.message : "Failed to load audit logs"); })
      .finally(() => setIsLoading(false));
  }, [actionFilter]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Shield className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Audit Logs</h1>
          <p className="text-muted-foreground">Security and activity audit trail</p>
        </div>
      </div>

      <div className="max-w-sm">
        <Input
          placeholder="Filter by action..."
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
        />
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Time</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Resource</TableHead>
              <TableHead>User</TableHead>
              <TableHead>IP</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : logs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  No audit logs found
                </TableCell>
              </TableRow>
            ) : (
              logs.map((log) => (
                <TableRow key={log.audit_log_id}>
                  <TableCell className="text-sm">
                    {new Date(log.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{log.action}</Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm">{log.resource_type}</span>
                    {log.resource_id && (
                      <span className="text-xs text-muted-foreground ml-1">
                        {log.resource_id.slice(0, 8)}...
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="font-mono text-sm">
                    {log.user_id.slice(0, 8)}...
                  </TableCell>
                  <TableCell className="text-sm">{log.ip_address ?? "—"}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
