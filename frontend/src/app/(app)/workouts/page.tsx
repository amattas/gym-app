"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
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

interface Workout {
  workout_id: string;
  client_id: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  notes: string | null;
  created_at: string;
}

const statusColors: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  in_progress: "default",
  completed: "secondary",
  cancelled: "destructive",
  planned: "outline",
};

export default function WorkoutsPage() {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ data: Workout[] }>("/v1/workouts")
      .then((res) => setWorkouts(res.data))
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workouts</h1>
          <p className="text-muted-foreground">Log and track workouts</p>
        </div>
        <Button asChild>
          <Link href="/workouts/new">
            <Plus className="mr-2 h-4 w-4" />
            New Workout
          </Link>
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Started</TableHead>
              <TableHead>Completed</TableHead>
              <TableHead>Notes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : workouts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  No workouts found
                </TableCell>
              </TableRow>
            ) : (
              workouts.map((w) => (
                <TableRow key={w.workout_id}>
                  <TableCell>
                    <Link
                      href={`/workouts/${w.workout_id}`}
                      className="font-medium hover:underline"
                    >
                      {new Date(w.created_at).toLocaleDateString()}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusColors[w.status] || "outline"}>
                      {w.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {w.started_at
                      ? new Date(w.started_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "—"}
                  </TableCell>
                  <TableCell>
                    {w.completed_at
                      ? new Date(w.completed_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "—"}
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {w.notes || "—"}
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
