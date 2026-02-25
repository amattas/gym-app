"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";

interface WorkoutSet {
  set_number: number;
  weight: number | null;
  reps: number;
  set_type: string;
}

interface WorkoutExercise {
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

  useEffect(() => {
    api
      .get<{ data: Workout }>(`/v1/workouts/${workoutId}`)
      .then((res) => setWorkout(res.data))
      .catch(() => router.push("/workouts"));
  }, [workoutId, router]);

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
        workout.exercises.map((ex, idx) => (
          <Card key={idx}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">
                {ex.exercise_name || `Exercise ${idx + 1}`}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {ex.sets.map((set) => (
                  <div
                    key={set.set_number}
                    className="flex items-center gap-4 text-sm"
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
    </div>
  );
}
