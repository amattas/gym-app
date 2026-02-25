"use client";

import { useEffect, useState } from "react";
import { Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";

interface Schedule {
  schedule_id: string;
  client_id: string;
  trainer_id: string;
  scheduled_start: string;
  scheduled_end: string;
  status: string;
  notes: string | null;
}

const statusColors: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  confirmed: "default",
  tentative: "outline",
  completed: "secondary",
  canceled: "destructive",
  no_show: "destructive",
};

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ data: Schedule[] }>("/v1/schedules")
      .then((res) => setSchedules(res.data))
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Calendar className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Schedules</h1>
          <p className="text-muted-foreground">
            Session scheduling and management
          </p>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Time</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Notes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : schedules.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  No schedules found
                </TableCell>
              </TableRow>
            ) : (
              schedules.map((s) => (
                <TableRow key={s.schedule_id}>
                  <TableCell>
                    {new Date(s.scheduled_start).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {new Date(s.scheduled_start).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}{" "}
                    -{" "}
                    {new Date(s.scheduled_end).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusColors[s.status] || "outline"}>
                      {s.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {s.notes || "—"}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
