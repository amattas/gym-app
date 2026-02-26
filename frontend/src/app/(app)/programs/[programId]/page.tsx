"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface ProgramDay {
  program_day_id: string;
  name: string;
  order_index: number;
}

interface DayExercise {
  program_day_exercise_id: string;
  exercise_id: string;
  order_index: number;
  default_sets: number | null;
  default_reps: number | null;
  rest_seconds: number | null;
}

export default function ProgramDetailPage() {
  const params = useParams();
  const router = useRouter();
  const programId = params.programId as string;
  const [days, setDays] = useState<ProgramDay[]>([]);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [dayExercises, setDayExercises] = useState<DayExercise[]>([]);
  const [newDayName, setNewDayName] = useState("");
  const [dayDialogOpen, setDayDialogOpen] = useState(false);

  const fetchDays = useCallback(() => {
    return api
      .get<{ data: ProgramDay[] }>(`/v1/programs/${programId}/days`)
      .then((res) => setDays(res.data))
      .catch((err) => {
        toast.error(err instanceof Error ? err.message : "Failed to load program days");
      });
  }, [programId]);

  useEffect(() => {
    fetchDays();
  }, [fetchDays]);

  useEffect(() => {
    if (selectedDay) {
      api
        .get<{ data: DayExercise[] }>(
          `/v1/program-days/${selectedDay}/exercises`
        )
        .then((res) => setDayExercises(res.data))
        .catch((err) => {
          toast.error(err instanceof Error ? err.message : "Failed to load exercises");
          setDayExercises([]);
        });
    }
  }, [selectedDay]);

  async function handleAddDay(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post(`/v1/programs/${programId}/days`, {
        name: newDayName,
        order_index: days.length,
      });
      setNewDayName("");
      setDayDialogOpen(false);
      fetchDays();
      toast.success("Day added");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to add day");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/programs")}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">Program Builder</h1>
          <p className="text-muted-foreground">
            Manage days and exercises
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Days</h2>
            <Dialog open={dayDialogOpen} onOpenChange={setDayDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="mr-2 h-3 w-3" />
                  Add Day
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Program Day</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleAddDay} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Day Name</Label>
                    <Input
                      value={newDayName}
                      onChange={(e) => setNewDayName(e.target.value)}
                      placeholder="e.g., Day 1 - Push"
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full">
                    Add
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {days.length === 0 ? (
            <p className="text-sm text-muted-foreground">No days yet</p>
          ) : (
            days.map((day) => (
              <Card
                key={day.program_day_id}
                className={`cursor-pointer transition-colors ${
                  selectedDay === day.program_day_id
                    ? "border-primary"
                    : "hover:border-muted-foreground/25"
                }`}
                onClick={() => setSelectedDay(day.program_day_id)}
              >
                <CardContent className="py-3 px-4">
                  <p className="font-medium">{day.name}</p>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        <div className="lg:col-span-2">
          {selectedDay ? (
            <Card>
              <CardHeader>
                <CardTitle>
                  {days.find((d) => d.program_day_id === selectedDay)?.name ||
                    "Day"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dayExercises.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">
                    No exercises added to this day yet
                  </p>
                ) : (
                  <div className="space-y-3">
                    {dayExercises.map((ex, idx) => (
                      <div
                        key={ex.program_day_exercise_id}
                        className="flex items-center gap-4 text-sm"
                      >
                        <span className="text-muted-foreground w-6">
                          {idx + 1}.
                        </span>
                        <span className="flex-1 font-medium">
                          Exercise {ex.exercise_id.slice(0, 8)}...
                        </span>
                        <span className="text-muted-foreground">
                          {ex.default_sets || "—"}x{ex.default_reps || "—"}
                        </span>
                        {ex.rest_seconds && (
                          <span className="text-muted-foreground">
                            {ex.rest_seconds}s rest
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className="flex h-64 items-center justify-center text-muted-foreground">
              Select a day to view exercises
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
