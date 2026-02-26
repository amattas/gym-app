"use client";

import { useState } from "react";
import { Camera, Loader2, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Photo {
  photo_id: string;
  notes: string | null;
  captured_at: string;
  content_type?: string;
}

export default function ProgressPhotosPage() {
  const [clientId, setClientId] = useState("");
  const [searchedClientId, setSearchedClientId] = useState("");
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [storageKey, setStorageKey] = useState("");
  const [contentType, setContentType] = useState("image/jpeg");
  const [uploadNotes, setUploadNotes] = useState("");
  const [capturedAt, setCapturedAt] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId) return;
    setIsLoading(true);
    try {
      const res = await api.get<{ data: Photo[] }>(
        `/v1/clients/${clientId}/progress-photos`
      );
      setPhotos(res.data);
      setSearchedClientId(clientId);
    } catch {
      toast.error("Failed to load photos");
      setPhotos([]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!searchedClientId) return;
    setIsUploading(true);
    try {
      await api.post(`/v1/clients/${searchedClientId}/progress-photos`, {
        storage_key: storageKey,
        content_type: contentType,
        notes: uploadNotes || null,
        captured_at: capturedAt || new Date().toISOString(),
      });
      toast.success("Photo uploaded");
      setShowUpload(false);
      setStorageKey("");
      setUploadNotes("");
      setCapturedAt("");
      const res = await api.get<{ data: Photo[] }>(
        `/v1/clients/${searchedClientId}/progress-photos`
      );
      setPhotos(res.data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to upload");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete(photoId: string) {
    try {
      await api.delete(
        `/v1/clients/${searchedClientId}/progress-photos/${photoId}`
      );
      toast.success("Photo deleted");
      setPhotos(photos.filter((p) => p.photo_id !== photoId));
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete");
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

      {searchedClientId && (
        <>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Photos</h2>
            <Dialog open={showUpload} onOpenChange={setShowUpload}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" /> Upload Photo
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Upload Photo</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleUpload} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Storage Key</Label>
                    <Input
                      placeholder="e.g. photos/client123/front.jpg"
                      value={storageKey}
                      onChange={(e) => setStorageKey(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Content Type</Label>
                    <Select value={contentType} onValueChange={setContentType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="image/jpeg">image/jpeg</SelectItem>
                        <SelectItem value="image/png">image/png</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Notes</Label>
                    <Textarea
                      value={uploadNotes}
                      onChange={(e) => setUploadNotes(e.target.value)}
                      placeholder="Optional notes..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Captured At</Label>
                    <Input
                      type="date"
                      value={capturedAt}
                      onChange={(e) => setCapturedAt(e.target.value)}
                    />
                  </div>
                  <Button type="submit" disabled={isUploading} className="w-full">
                    {isUploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Upload
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {photos.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {photos.map((p) => (
                <Card key={p.photo_id}>
                  <CardContent className="pt-6">
                    <div className="aspect-square bg-muted rounded flex items-center justify-center mb-2">
                      <Camera className="h-12 w-12 text-muted-foreground" />
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-muted-foreground">
                        {new Date(p.captured_at).toLocaleDateString()}
                      </p>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-8 w-8 text-destructive"
                        onClick={() => handleDelete(p.photo_id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    {p.notes && <p className="text-sm mt-1">{p.notes}</p>}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No photos found
            </p>
          )}
        </>
      )}
    </div>
  );
}
