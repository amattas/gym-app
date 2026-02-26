"use client";

import { useEffect, useState, useCallback } from "react";
import { Calendar, Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
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

interface Schedule {
  schedule_id: string;
  client_id: string;
  trainer_id: string;
  location_id?: string;
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
  const [showCreate, setShowCreate] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [filterTrainer, setFilterTrainer] = useState("");
  const [filterClient, setFilterClient] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [newClientId, setNewClientId] = useState("");
  const [newTrainerId, setNewTrainerId] = useState("");
  const [newLocationId, setNewLocationId] = useState("");
  const [newStart, setNewStart] = useState("");
  const [newEnd, setNewEnd] = useState("");
  const [newNotes, setNewNotes] = useState("");

  const fetchSchedules = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterTrainer) params.set("trainer_id", filterTrainer);
      if (filterClient) params.set("client_id", filterClient);
      if (filterDate) params.set("date", filterDate);
      const qs = params.toString();
      const res = await api.get<{ data: Schedule[] }>(
        `/v1/schedules${qs ? `?${qs}` : ""}`
      );
      setSchedules(res.data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to load schedules");
      setSchedules([]);
    } finally {
      setIsLoading(false);
    }
  }, [filterTrainer, filterClient, filterDate]);

  useEffect(() => {
    fetchSchedules();
  }, [fetchSchedules]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post("/v1/schedules", {
        client_id: newClientId,
        trainer_id: newTrainerId,
        location_id: newLocationId || null,
        scheduled_start: newStart,
        scheduled_end: newEnd,
        notes: newNotes || null,
      });
      toast.success("Schedule created");
      setShowCreate(false);
      setNewClientId("");
      setNewTrainerId("");
      setNewLocationId("");
      setNewStart("");
      setNewEnd("");
      setNewNotes("");
      fetchSchedules();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleAction(id: string, action: string) {
    try {
      await api.post(`/v1/schedules/${id}/${action}`);
      toast.success(`Schedule ${action}ed`);
      fetchSchedules();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : `Failed to ${action}`);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Calendar className="h-8 w-8 text-muted-foreground" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Schedules</h1>
            <p className="text-muted-foreground">
              Session scheduling and management
            </p>
          </div>
        </div>
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Create Schedule
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Schedule</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label>Client ID</Label>
                <Input
                  value={newClientId}
                  onChange={(e) => setNewClientId(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Trainer ID</Label>
                <Input
                  value={newTrainerId}
                  onChange={(e) => setNewTrainerId(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Location ID</Label>
                <Input
                  value={newLocationId}
                  onChange={(e) => setNewLocationId(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Start</Label>
                <Input
                  type="datetime-local"
                  value={newStart}
                  onChange={(e) => setNewStart(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>End</Label>
                <Input
                  type="datetime-local"
                  value={newEnd}
                  onChange={(e) => setNewEnd(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Notes</Label>
                <Textarea
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                />
              </div>
              <Button type="submit" disabled={isCreating} className="w-full">
                {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-end gap-4 flex-wrap">
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Trainer ID</Label>
          <Input
            placeholder="Filter by trainer..."
            value={filterTrainer}
            onChange={(e) => setFilterTrainer(e.target.value)}
            className="w-48"
          />
        </div>
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Client ID</Label>
          <Input
            placeholder="Filter by client..."
            value={filterClient}
            onChange={(e) => setFilterClient(e.target.value)}
            className="w-48"
          />
        </div>
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Date</Label>
          <Input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            className="w-48"
          />
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Time</TableHead>
              <TableHead>Client</TableHead>
              <TableHead>Trainer</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Notes</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : schedules.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8">
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
                  <TableCell className="font-mono text-sm">
                    {s.client_id.slice(0, 8)}...
                  </TableCell>
                  <TableCell className="font-mono text-sm">
                    {s.trainer_id.slice(0, 8)}...
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusColors[s.status] || "outline"}>
                      {s.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {s.notes || "\u2014"}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {s.status === "tentative" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction(s.schedule_id, "confirm")}
                        >
                          Confirm
                        </Button>
                      )}
                      {(s.status === "tentative" || s.status === "confirmed") && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction(s.schedule_id, "cancel")}
                        >
                          Cancel
                        </Button>
                      )}
                      {s.status === "confirmed" && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAction(s.schedule_id, "complete")}
                          >
                            Complete
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleAction(s.schedule_id, "no-show")}
                          >
                            No-Show
                          </Button>
                        </>
                      )}
                    </div>
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
