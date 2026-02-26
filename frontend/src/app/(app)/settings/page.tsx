"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Gym {
  gym_id: string;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  settings: Record<string, unknown> | null;
}

export default function SettingsPage() {
  const [gym, setGym] = useState<Gym | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      const gymId = localStorage.getItem("gym_id");
      if (!gymId) return;
      try {
        const res = await api.get<{ data: Gym }>(`/v1/gyms/${gymId}`);
        setGym(res.data);
        setName(res.data.name);
        setEmail(res.data.email || "");
        setPhone(res.data.phone || "");
      } catch {}
    };
    load().finally(() => setIsLoading(false));
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!gym) return;

    try {
      await api.patch(`/v1/gyms/${gym.gym_id}`, {
        name,
        email: email || null,
        phone: phone || null,
      });
      toast.success("Settings saved");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save");
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your gym profile</p>
      </div>

      <Separator />

      <form onSubmit={handleSave}>
        <Card>
          <CardHeader>
            <CardTitle>Gym Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="gym-name">Gym Name</Label>
              <Input
                id="gym-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gym-email">Email</Label>
              <Input
                id="gym-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gym-phone">Phone</Label>
              <Input
                id="gym-phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <Button type="submit">Save Changes</Button>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
