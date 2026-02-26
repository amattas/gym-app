"use client";

import { useState } from "react";
import { Target, Search, Plus, Loader2, Pencil, Trash2, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Goal {
  goal_id: string;
  client_id: string;
  goal_type: string;
  target_value: number;
  current_value: number;
  target_date: string | null;
  status: string;
  notes: string | null;
  created_at: string;
}

const statusVariant: Record<string, "default" | "secondary" | "destructive"> = {
  active: "default",
  completed: "secondary",
  abandoned: "destructive",
};

export default function GoalsPage() {
  const [clientId, setClientId] = useState("");
  const [searchedClientId, setSearchedClientId] = useState("");
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [goalType, setGoalType] = useState("");
  const [targetValue, setTargetValue] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [notes, setNotes] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [editGoal, setEditGoal] = useState<Goal | null>(null);
  const [editCurrentValue, setEditCurrentValue] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  async function refreshGoals() {
    if (!searchedClientId) return;
    const res = await api.get<{ data: Goal[] }>(
      `/v1/clients/${encodeURIComponent(searchedClientId)}/goals`
    );
    setGoals(res.data);
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId) return;
    setIsLoading(true);
    try {
      const res = await api.get<{ data: Goal[] }>(
        `/v1/clients/${encodeURIComponent(clientId)}/goals`
      );
      setGoals(res.data);
      setSearchedClientId(clientId);
    } catch {
      toast.error("Failed to load goals");
      setGoals([]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post(`/v1/clients/${encodeURIComponent(searchedClientId)}/goals`, {
        goal_type: goalType,
        target_value: parseFloat(targetValue),
        target_date: targetDate || null,
        notes: notes || null,
      });
      toast.success("Goal created");
      setShowAdd(false);
      setGoalType("");
      setTargetValue("");
      setTargetDate("");
      setNotes("");
      await refreshGoals();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create goal");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleUpdate(e: React.FormEvent) {
    e.preventDefault();
    if (!editGoal) return;
    setIsUpdating(true);
    try {
      await api.put(
        `/v1/clients/${encodeURIComponent(searchedClientId)}/goals/${editGoal.goal_id}`,
        {
          current_value: parseFloat(editCurrentValue),
          notes: editNotes || null,
        }
      );
      toast.success("Goal updated");
      setEditGoal(null);
      await refreshGoals();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update");
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleStatusChange(goal: Goal, status: string) {
    try {
      await api.put(
        `/v1/clients/${encodeURIComponent(searchedClientId)}/goals/${goal.goal_id}`,
        { status }
      );
      toast.success(`Goal marked as ${status}`);
      await refreshGoals();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update status");
    }
  }

  async function handleDelete(goal: Goal) {
    try {
      await api.delete(
        `/v1/clients/${encodeURIComponent(searchedClientId)}/goals/${goal.goal_id}`
      );
      toast.success("Goal deleted");
      await refreshGoals();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete");
    }
  }

  function openEdit(goal: Goal) {
    setEditGoal(goal);
    setEditCurrentValue(String(goal.current_value));
    setEditNotes(goal.notes || "");
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Target className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Goals</h1>
          <p className="text-muted-foreground">Track client fitness goals</p>
        </div>
      </div>

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle>Search by Client</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex items-end gap-4">
            <div className="flex-1 space-y-2">
              <Label>Client ID</Label>
              <Input
                placeholder="Enter client UUID"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={isLoading || !clientId}>
              {isLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Search className="mr-2 h-4 w-4" />
              )}
              Search
            </Button>
          </form>
        </CardContent>
      </Card>

      {searchedClientId && (
        <>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Client Goals</h2>
            <Dialog open={showAdd} onOpenChange={setShowAdd}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" /> Add Goal
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Goal</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleAdd} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Goal Type</Label>
                    <Input
                      placeholder="e.g. weight loss, bench press PR"
                      value={goalType}
                      onChange={(e) => setGoalType(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Target Value</Label>
                    <Input
                      type="number"
                      step="0.1"
                      value={targetValue}
                      onChange={(e) => setTargetValue(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Target Date</Label>
                    <Input
                      type="date"
                      value={targetDate}
                      onChange={(e) => setTargetDate(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Notes</Label>
                    <Textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Optional notes..."
                    />
                  </div>
                  <Button type="submit" disabled={isCreating} className="w-full">
                    {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Create Goal
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <Dialog open={!!editGoal} onOpenChange={(open) => !open && setEditGoal(null)}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Update Progress</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleUpdate} className="space-y-4">
                <div className="space-y-2">
                  <Label>Current Value</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={editCurrentValue}
                    onChange={(e) => setEditCurrentValue(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Notes</Label>
                  <Textarea
                    value={editNotes}
                    onChange={(e) => setEditNotes(e.target.value)}
                  />
                </div>
                <Button type="submit" disabled={isUpdating} className="w-full">
                  {isUpdating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Update
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          {goals.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {goals.map((goal) => {
                const pct =
                  goal.target_value > 0
                    ? Math.min(
                        Math.round((goal.current_value / goal.target_value) * 100),
                        100
                      )
                    : 0;
                return (
                  <Card key={goal.goal_id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">{goal.goal_type}</CardTitle>
                        <Badge variant={statusVariant[goal.status] || "default"}>
                          {goal.status}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span>
                          {goal.current_value} / {goal.target_value}
                        </span>
                        <span className="text-muted-foreground">{pct}%</span>
                      </div>
                      <Progress value={pct} />
                      {goal.target_date && (
                        <p className="text-sm text-muted-foreground">
                          Target: {new Date(goal.target_date).toLocaleDateString()}
                        </p>
                      )}
                      {goal.notes && (
                        <p className="text-sm text-muted-foreground">{goal.notes}</p>
                      )}
                      <div className="flex gap-1 pt-2">
                        {goal.status === "active" && (
                          <>
                            <Button size="sm" variant="outline" onClick={() => openEdit(goal)}>
                              <Pencil className="mr-1 h-3 w-3" /> Update
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusChange(goal, "completed")}
                            >
                              <Check className="mr-1 h-3 w-3" /> Complete
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleStatusChange(goal, "abandoned")}
                            >
                              Abandon
                            </Button>
                          </>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDelete(goal)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No goals found</p>
          )}
        </>
      )}
    </div>
  );
}
