"use client";

import { useState } from "react";
import { Ruler, Search, Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Measurement {
  measurement_id: string;
  client_id: string;
  measurement_type: string;
  value: number;
  unit: string;
  measured_at: string;
}

const MEASUREMENT_TYPES = [
  "weight",
  "body_fat",
  "chest",
  "waist",
  "hips",
  "bicep",
  "thigh",
  "calf",
];

function getUnit(type: string): string {
  if (type === "weight") return "kg";
  if (type === "body_fat") return "%";
  return "cm";
}

export default function MeasurementsPage() {
  const [clientId, setClientId] = useState("");
  const [searchedClientId, setSearchedClientId] = useState("");
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [addType, setAddType] = useState("weight");
  const [addValue, setAddValue] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId) return;
    setIsLoading(true);
    try {
      const res = await api.get<{ data: Measurement[] }>(
        `/v1/measurements?client_id=${encodeURIComponent(clientId)}`
      );
      setMeasurements(res.data);
      setSearchedClientId(clientId);
    } catch {
      toast.error("Failed to load measurements");
      setMeasurements([]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post("/v1/measurements", {
        client_id: searchedClientId,
        measurement_type: addType,
        value: parseFloat(addValue),
        unit: getUnit(addType),
      });
      toast.success("Measurement added");
      setShowAdd(false);
      setAddValue("");
      const res = await api.get<{ data: Measurement[] }>(
        `/v1/measurements?client_id=${encodeURIComponent(searchedClientId)}`
      );
      setMeasurements(res.data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to add");
    } finally {
      setIsCreating(false);
    }
  }

  const latestByType: Record<string, Measurement> = {};
  for (const m of measurements) {
    const existing = latestByType[m.measurement_type];
    if (!existing || new Date(m.measured_at) > new Date(existing.measured_at)) {
      latestByType[m.measurement_type] = m;
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Ruler className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Measurements</h1>
          <p className="text-muted-foreground">Track client body measurements</p>
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
            <h2 className="text-xl font-semibold">Latest Measurements</h2>
            <Dialog open={showAdd} onOpenChange={setShowAdd}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" /> Add Measurement
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Measurement</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleAdd} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Client ID</Label>
                    <Input value={searchedClientId} disabled />
                  </div>
                  <div className="space-y-2">
                    <Label>Type</Label>
                    <Select value={addType} onValueChange={setAddType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {MEASUREMENT_TYPES.map((t) => (
                          <SelectItem key={t} value={t}>
                            {t.replace("_", " ")}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Value ({getUnit(addType)})</Label>
                    <Input
                      type="number"
                      step="0.1"
                      value={addValue}
                      onChange={(e) => setAddValue(e.target.value)}
                      required
                    />
                  </div>
                  <Button type="submit" disabled={isCreating} className="w-full">
                    {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Add
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {Object.keys(latestByType).length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {MEASUREMENT_TYPES.map((type) => {
                const m = latestByType[type];
                return (
                  <Card key={type}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground capitalize">
                        {type.replace("_", " ")}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {m ? (
                        <p className="text-2xl font-bold">
                          {m.value} {m.unit}
                        </p>
                      ) : (
                        <p className="text-2xl font-bold text-muted-foreground">—</p>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No measurements found
            </p>
          )}

          {measurements.length > 0 && (
            <>
              <h2 className="text-xl font-semibold">History</h2>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Value</TableHead>
                      <TableHead>Unit</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {measurements.map((m) => (
                      <TableRow key={m.measurement_id}>
                        <TableCell>
                          {new Date(m.measured_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell className="capitalize">
                          {m.measurement_type.replace("_", " ")}
                        </TableCell>
                        <TableCell>{m.value}</TableCell>
                        <TableCell>{m.unit}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
