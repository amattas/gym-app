"use client";

import { useState } from "react";
import { Camera, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function ProgressPhotosPage() {
  const [clientId, setClientId] = useState("");
  const [photos, setPhotos] = useState<
    { photo_id: string; notes: string | null; captured_at: string }[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId) return;
    setIsLoading(true);
    try {
      const res = await api.get<{
        data: { photo_id: string; notes: string | null; captured_at: string }[];
      }>(`/v1/clients/${clientId}/progress-photos`);
      setPhotos(res.data);
    } catch {
      toast.error("Failed to load photos");
      setPhotos([]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Camera className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Progress Photos</h1>
          <p className="text-muted-foreground">View client progress photos</p>
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
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Search
            </Button>
          </form>
        </CardContent>
      </Card>

      {photos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {photos.map((p) => (
            <Card key={p.photo_id}>
              <CardContent className="pt-6">
                <div className="aspect-square bg-muted rounded flex items-center justify-center mb-2">
                  <Camera className="h-12 w-12 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground">
                  {new Date(p.captured_at).toLocaleDateString()}
                </p>
                {p.notes && <p className="text-sm mt-1">{p.notes}</p>}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
