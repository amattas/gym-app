"use client";

import { useCallback, useEffect, useState } from "react";
import { Plus, Search, Trash2, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Exercise {
  exercise_id: string;
  name: string;
  muscle_group: string | null;
  equipment: string | null;
  description: string | null;
}

const MUSCLE_GROUPS = [
  "chest",
  "back",
  "shoulders",
  "biceps",
  "triceps",
  "legs",
  "core",
  "glutes",
  "calves",
  "forearms",
  "full_body",
];

export default function ExercisesPage() {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [search, setSearch] = useState("");
  const [muscleFilter, setMuscleFilter] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newMuscle, setNewMuscle] = useState("");
  const [newEquipment, setNewEquipment] = useState("");
  const [editExercise, setEditExercise] = useState<Exercise | null>(null);
  const [editName, setEditName] = useState("");
  const [editMuscle, setEditMuscle] = useState("");
  const [editEquipment, setEditEquipment] = useState("");

  const fetchExercises = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await api.get<{ data: Exercise[] }>("/v1/exercises");
      setExercises(res.data);
    } catch {
      setExercises([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExercises();
  }, [fetchExercises]);

  const filtered = exercises.filter((e) => {
    const matchesSearch =
      e.name.toLowerCase().includes(search.toLowerCase()) ||
      e.muscle_group?.toLowerCase().includes(search.toLowerCase());
    const matchesMuscle =
      !muscleFilter || e.muscle_group?.toLowerCase() === muscleFilter.toLowerCase();
    return matchesSearch && matchesMuscle;
  });

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/v1/exercises", {
        name: newName,
        muscle_group: newMuscle || null,
        equipment: newEquipment || null,
      });
      toast.success("Exercise created");
      setDialogOpen(false);
      setNewName("");
      setNewMuscle("");
      setNewEquipment("");
      fetchExercises();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create");
    }
  }

  function openEdit(exercise: Exercise) {
    setEditExercise(exercise);
    setEditName(exercise.name);
    setEditMuscle(exercise.muscle_group || "");
    setEditEquipment(exercise.equipment || "");
  }

  async function handleEdit(e: React.FormEvent) {
    e.preventDefault();
    if (!editExercise) return;
    try {
      await api.patch(`/v1/exercises/${editExercise.exercise_id}`, {
        name: editName,
        muscle_group: editMuscle || null,
        equipment: editEquipment || null,
      });
      toast.success("Exercise updated");
      setEditExercise(null);
      fetchExercises();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update");
    }
  }

  async function handleDelete(exerciseId: string) {
    try {
      await api.delete(`/v1/exercises/${exerciseId}`);
      toast.success("Exercise deleted");
      setExercises(exercises.filter((e) => e.exercise_id !== exerciseId));
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Exercises</h1>
          <p className="text-muted-foreground">Exercise library</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Exercise
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>New Exercise</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="muscle">Muscle Group</Label>
                <Input
                  id="muscle"
                  value={newMuscle}
                  onChange={(e) => setNewMuscle(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="equipment">Equipment</Label>
                <Input
                  id="equipment"
                  value={newEquipment}
                  onChange={(e) => setNewEquipment(e.target.value)}
                />
              </div>
              <Button type="submit" className="w-full">
                Create
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search exercises..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={muscleFilter} onValueChange={setMuscleFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All muscle groups" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All muscle groups</SelectItem>
            {MUSCLE_GROUPS.map((mg) => (
              <SelectItem key={mg} value={mg}>
                {mg.replace("_", " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((exercise) => (
            <Card key={exercise.exercise_id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{exercise.name}</CardTitle>
                  <div className="flex gap-1">
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-7 w-7"
                      onClick={() => openEdit(exercise)}
                    >
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-7 w-7 text-destructive"
                      onClick={() => handleDelete(exercise.exercise_id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex gap-2">
                {exercise.muscle_group && (
                  <Badge variant="outline">{exercise.muscle_group}</Badge>
                )}
                {exercise.equipment && (
                  <Badge variant="secondary">{exercise.equipment}</Badge>
                )}
              </CardContent>
            </Card>
          ))}
          {filtered.length === 0 && (
            <p className="col-span-full text-center text-muted-foreground py-8">
              No exercises found
            </p>
          )}
        </div>
      )}

      <Dialog
        open={editExercise !== null}
        onOpenChange={(open) => !open && setEditExercise(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Exercise</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEdit} className="space-y-4">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Muscle Group</Label>
              <Input
                value={editMuscle}
                onChange={(e) => setEditMuscle(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Equipment</Label>
              <Input
                value={editEquipment}
                onChange={(e) => setEditEquipment(e.target.value)}
              />
            </div>
            <Button type="submit" className="w-full">
              Save Changes
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
