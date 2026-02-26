"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, Plus, Play, CheckCircle, Trophy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface WorkoutSet {
  set_id?: string;
  set_number: number;
  weight: number | null;
  reps: number;
  set_type: string;
  is_pr?: boolean;
  completed?: boolean;
}

interface WorkoutExercise {
  workout_exercise_id?: string;
  exercise_id: string;
  exercise_name: string;
  order_index: number;
  sets: WorkoutSet[];
}

interface Workout {
  workout_id: string;
  client_id: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  notes: string | null;
  exercises: WorkoutExercise[];
  created_at: string;
}

export default function WorkoutDetailPage() {
  const params = useParams();
  const router = useRouter();
  const workoutId = params.workoutId as string;
  const [workout, setWorkout] = useState<Workout | null>(null);
  const [editingSet, setEditingSet] = useState<{ exIdx: number; setIdx: number } | null>(null);
  const [editWeight, setEditWeight] = useState("");
  const [editReps, setEditReps] = useState("");
  const [addSetExIdx, setAddSetExIdx] = useState<number | null>(null);
  const [newWeight, setNewWeight] = useState("");
  const [newReps, setNewReps] = useState("");
  const [isActioning, setIsActioning] = useState(false);

  function fetchWorkout() {
    api
      .get<{ data: Workout }>(`/v1/workouts/${workoutId}`)
      .then((res) => setWorkout(res.data))
      .catch(() => router.push("/workouts"));
  }

  useEffect(() => {
    fetchWorkout();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workoutId]);

  async function handleStart() {
    setIsActioning(true);
    try {
      await api.post(`/v1/workouts/${workoutId}/start`);
      toast.success("Workout started");
      fetchWorkout();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to start");
    } finally {
      setIsActioning(false);
    }
  }

  async function handleComplete() {
    setIsActioning(true);
    try {
      await api.post(`/v1/workouts/${workoutId}/complete`);
      toast.success("Workout completed");
      fetchWorkout();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to complete");
    } finally {
      setIsActioning(false);
    }
  }

  function startEditing(exIdx: number, setIdx: number, set: WorkoutSet) {
    setEditingSet({ exIdx, setIdx });
    setEditWeight(set.weight != null ? String(set.weight) : "");
    setEditReps(String(set.reps));
  }

  async function handleSaveSet() {
    if (!editingSet || !workout) return;
    const ex = workout.exercises[editingSet.exIdx];
    const set = ex.sets[editingSet.setIdx];
    const setId = set.set_id;
    const exerciseId = ex.workout_exercise_id || ex.exercise_id;
    try {
      await api.patch(
        `/v1/workouts/${workoutId}/exercises/${exerciseId}/sets/${setId}`,
        {
          weight_kg: editWeight ? parseFloat(editWeight) : null,
          reps: parseInt(editReps),
        }
      );
      toast.success("Set updated");
      setEditingSet(null);
      fetchWorkout();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update set");
    }
  }

  async function handleAddSet(exIdx: number) {
    if (!workout) return;
    const ex = workout.exercises[exIdx];
    const exerciseId = ex.workout_exercise_id || ex.exercise_id;
    try {
      await api.post(
        `/v1/workouts/${workoutId}/exercises/${exerciseId}/sets`,
        {
          weight_kg: newWeight ? parseFloat(newWeight) : null,
          reps: parseInt(newReps),
          completed: true,
        }
      );
      toast.success("Set added");
      setAddSetExIdx(null);
      setNewWeight("");
      setNewReps("");
      fetchWorkout();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to add set");
    }
  }

  if (!workout) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/workouts")}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">
            Workout — {new Date(workout.created_at).toLocaleDateString()}
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <Badge>{workout.status}</Badge>
            {workout.started_at && (
              <span className="text-sm text-muted-foreground">
                Started{" "}
                {new Date(workout.started_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            )}
            {workout.completed_at && (
              <span className="text-sm text-muted-foreground">
                — Completed{" "}
                {new Date(workout.completed_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {workout.status === "scheduled" && (
            <Button onClick={handleStart} disabled={isActioning}>
              {isActioning ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Start Workout
            </Button>
          )}
          {workout.status === "in_progress" && (
            <Button onClick={handleComplete} disabled={isActioning}>
              {isActioning ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle className="mr-2 h-4 w-4" />
              )}
              Complete Workout
            </Button>
          )}
        </div>
      </div>

      {workout.notes && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm">{workout.notes}</p>
          </CardContent>
        </Card>
      )}

      <Separator />

      {workout.exercises?.length > 0 ? (
        workout.exercises.map((ex, exIdx) => (
          <Card key={exIdx}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">
                  {ex.exercise_name || `Exercise ${exIdx + 1}`}
                </CardTitle>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setAddSetExIdx(exIdx);
                    setNewWeight("");
                    setNewReps("");
                  }}
                >
                  <Plus className="mr-1 h-3 w-3" /> Add Set
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {ex.sets.map((set, setIdx) => (
                  <div
                    key={set.set_number}
                    className="flex items-center gap-4 text-sm cursor-pointer hover:bg-muted/50 rounded px-2 py-1 -mx-2"
                    onClick={() => startEditing(exIdx, setIdx, set)}
                  >
                    <span className="text-muted-foreground w-8">
                      #{set.set_number}
                    </span>
                    <span className="font-medium">
                      {set.weight != null ? `${set.weight} lbs` : "BW"} x{" "}
                      {set.reps} reps
                    </span>
                    {set.set_type !== "standard" && (
                      <Badge variant="outline" className="text-xs">
                        {set.set_type}
                      </Badge>
                    )}
                    {set.is_pr && (
                      <Badge variant="default" className="text-xs gap-1">
                        <Trophy className="h-3 w-3" /> PR
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))
      ) : (
        <p className="text-center text-muted-foreground py-8">
          No exercises recorded
        </p>
      )}

      <Dialog
        open={editingSet !== null}
        onOpenChange={(open) => !open && setEditingSet(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Set</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Weight</Label>
              <Input
                type="number"
                step="0.5"
                value={editWeight}
                onChange={(e) => setEditWeight(e.target.value)}
                placeholder="Body weight if empty"
              />
            </div>
            <div className="space-y-2">
              <Label>Reps</Label>
              <Input
                type="number"
                value={editReps}
                onChange={(e) => setEditReps(e.target.value)}
                required
              />
            </div>
            <Button onClick={handleSaveSet} className="w-full">
              Save
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog
        open={addSetExIdx !== null}
        onOpenChange={(open) => !open && setAddSetExIdx(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Set</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Weight</Label>
              <Input
                type="number"
                step="0.5"
                value={newWeight}
                onChange={(e) => setNewWeight(e.target.value)}
                placeholder="Body weight if empty"
              />
            </div>
            <div className="space-y-2">
              <Label>Reps</Label>
              <Input
                type="number"
                value={newReps}
                onChange={(e) => setNewReps(e.target.value)}
                required
              />
            </div>
            <Button
              onClick={() => addSetExIdx !== null && handleAddSet(addSetExIdx)}
              className="w-full"
              disabled={!newReps}
            >
              Add Set
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
