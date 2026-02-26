"use client";

import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Preferences {
  session_reminders: boolean;
  workout_updates: boolean;
  membership_alerts: boolean;
  marketing: boolean;
}

export default function NotificationsPage() {
  const [prefs, setPrefs] = useState<Preferences>({
    session_reminders: true,
    workout_updates: true,
    membership_alerts: true,
    marketing: false,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ data: Preferences }>("/v1/notifications/preferences")
      .then((res) => setPrefs(res.data))
      .catch((err) => { toast.error(err instanceof Error ? err.message : "Failed to load notification preferences"); })
      .finally(() => setIsLoading(false));
  }, []);

  async function handleToggle(key: keyof Preferences) {
    const updated = { ...prefs, [key]: !prefs[key] };
    setPrefs(updated);
    try {
      await api.put("/v1/notifications/preferences", updated);
      toast.success("Preferences updated");
    } catch {
      setPrefs(prefs);
      toast.error("Failed to update");
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Bell className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
          <p className="text-muted-foreground">Manage notification preferences</p>
        </div>
      </div>

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle>Notification Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {(
            [
              ["session_reminders", "Session Reminders", "Get reminded before scheduled sessions"],
              ["workout_updates", "Workout Updates", "Notifications when workouts are logged"],
              ["membership_alerts", "Membership Alerts", "Expiry and payment notifications"],
              ["marketing", "Marketing", "Promotional offers and news"],
            ] as const
          ).map(([key, label, desc]) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <Label className="text-base">{label}</Label>
                <p className="text-sm text-muted-foreground">{desc}</p>
              </div>
              <Switch checked={prefs[key]} onCheckedChange={() => handleToggle(key)} />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
