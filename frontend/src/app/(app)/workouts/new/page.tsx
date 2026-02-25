"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Loader2, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Exercise {
  exercise_id: string;
  name: string;
}

interface SetEntry {
  weight: string;
  reps: string;
  set_type: string;
}

interface ExerciseEntry {
  exercise_id: string;
  sets: SetEntry[];
}

export default function NewWorkoutPage() {
  const router = useRouter();
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [clientId, setClientId] = useState("");
  const [notes, setNotes] = useState("");
  const [entries, setEntries] = useState<ExerciseEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    api
      .get<{ data: Exercise[] }>("/v1/exercises")
      .then((res) => setExercises(res.data))
      .catch(() => {});
  }, []);

  const addExercise = useCallback(() => {
    setEntries((prev) => [
      ...prev,
      { exercise_id: "", sets: [{ weight: "", reps: "", set_type: "standard" }] },
    ]);
  }, []);

  const removeExercise = useCallback((idx: number) => {
    setEntries((prev) => prev.filter((_, i) => i !== idx));
  }, []);

  const addSet = useCallback((exIdx: number) => {
    setEntries((prev) =>
      prev.map((entry, i) =>
        i === exIdx
          ? {
              ...entry,
              sets: [
                ...entry.sets,
                { weight: "", reps: "", set_type: "standard" },
              ],
            }
          : entry
      )
    );
  }, []);

  const removeSet = useCallback((exIdx: number, setIdx: number) => {
    setEntries((prev) =>
      prev.map((entry, i) =>
        i === exIdx
          ? { ...entry, sets: entry.sets.filter((_, si) => si !== setIdx) }
          : entry
      )
    );
  }, []);

  const updateExercise = useCallback(
    (exIdx: number, exerciseId: string) => {
      setEntries((prev) =>
        prev.map((entry, i) =>
          i === exIdx ? { ...entry, exercise_id: exerciseId } : entry
        )
      );
    },
    []
  );

  const updateSet = useCallback(
    (exIdx: number, setIdx: number, field: keyof SetEntry, value: string) => {
      setEntries((prev) =>
        prev.map((entry, i) =>
          i === exIdx
            ? {
                ...entry,
                sets: entry.sets.map((s, si) =>
                  si === setIdx ? { ...s, [field]: value } : s
                ),
              }
            : entry
        )
      );
    },
    []
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId || entries.length === 0) {
      toast.error("Select a client and add at least one exercise");
      return;
    }

    setIsLoading(true);
    try {
      const workout_exercises = entries
        .filter((e) => e.exercise_id)
        .map((entry, order) => ({
          exercise_id: entry.exercise_id,
          order_index: order,
          sets: entry.sets
            .filter((s) => s.reps)
            .map((s, si) => ({
              set_number: si + 1,
              weight: s.weight ? parseFloat(s.weight) : null,
              reps: parseInt(s.reps),
              set_type: s.set_type,
            })),
        }));

      await api.post("/v1/workouts", {
        client_id: clientId,
        notes: notes || null,
        exercises: workout_exercises,
      });
      toast.success("Workout logged");
      router.push("/workouts");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to log workout");
    } finally {
      setIsLoading(false);
    }
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
        <h1 className="text-3xl font-bold tracking-tight">Log Workout</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Workout Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
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
              <Label>Notes</Label>
              <Textarea
                placeholder="Workout notes..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {entries.map((entry, exIdx) => (
          <Card key={exIdx}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
              <CardTitle className="text-base">
                Exercise {exIdx + 1}
              </CardTitle>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => removeExercise(exIdx)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select
                value={entry.exercise_id}
                onValueChange={(v) => updateExercise(exIdx, v)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select exercise" />
                </SelectTrigger>
                <SelectContent>
                  {exercises.map((ex) => (
                    <SelectItem key={ex.exercise_id} value={ex.exercise_id}>
                      {ex.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Separator />

              {entry.sets.map((set, setIdx) => (
                <div key={setIdx} className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground w-8">
                    #{setIdx + 1}
                  </span>
                  <Input
                    placeholder="Weight"
                    type="number"
                    step="0.5"
                    value={set.weight}
                    onChange={(e) =>
                      updateSet(exIdx, setIdx, "weight", e.target.value)
                    }
                    className="w-24"
                  />
                  <span className="text-sm text-muted-foreground">x</span>
                  <Input
                    placeholder="Reps"
                    type="number"
                    value={set.reps}
                    onChange={(e) =>
                      updateSet(exIdx, setIdx, "reps", e.target.value)
                    }
                    className="w-20"
                  />
                  <Select
                    value={set.set_type}
                    onValueChange={(v) =>
                      updateSet(exIdx, setIdx, "set_type", v)
                    }
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="standard">Standard</SelectItem>
                      <SelectItem value="warmup">Warmup</SelectItem>
                      <SelectItem value="drop_set">Drop Set</SelectItem>
                      <SelectItem value="amrap">AMRAP</SelectItem>
                      <SelectItem value="rest_pause">Rest Pause</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removeSet(exIdx, setIdx)}
                    disabled={entry.sets.length === 1}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              ))}

              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => addSet(exIdx)}
              >
                <Plus className="mr-2 h-3 w-3" />
                Add Set
              </Button>
            </CardContent>
          </Card>
        ))}

        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={addExercise}
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Exercise
        </Button>

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Save Workout
        </Button>
      </form>
    </div>
  );
}
