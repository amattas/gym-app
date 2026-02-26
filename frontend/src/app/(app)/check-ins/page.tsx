"use client";

import { useEffect, useState, useCallback } from "react";
import { ClipboardCheck, Loader2, UserCheck, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
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

interface CheckIn {
  check_in_id: string;
  client_id: string;
  check_in_method: string;
  checked_in_at: string;
  checked_out_at: string | null;
}

interface Location {
  location_id: string;
  name: string;
}

interface Occupancy {
  active_count: number;
  capacity?: number;
}

export default function CheckInsPage() {
  const [checkIns, setCheckIns] = useState<CheckIn[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [clientId, setClientId] = useState("");
  const [isChecking, setIsChecking] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState("");
  const [occupancy, setOccupancy] = useState<Occupancy | null>(null);
  const [filterDate, setFilterDate] = useState("");

  useEffect(() => {
    api
      .get<{ data: Location[] }>("/v1/locations")
      .then((res) => setLocations(res.data))
      .catch(() => {});
  }, []);

  const fetchCheckIns = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedLocation) params.set("location_id", selectedLocation);
      if (filterDate) params.set("date", filterDate);
      const qs = params.toString();
      const res = await api.get<{ data: CheckIn[] }>(
        `/v1/check-ins${qs ? `?${qs}` : ""}`
      );
      setCheckIns(res.data);
    } catch {
      setCheckIns([]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedLocation, filterDate]);

  useEffect(() => {
    fetchCheckIns();
  }, [fetchCheckIns]);

  useEffect(() => {
    if (!selectedLocation) {
      setOccupancy(null);
      return;
    }
    api
      .get<{ data: Occupancy }>(
        `/v1/locations/${selectedLocation}/occupancy`
      )
      .then((res) => setOccupancy(res.data))
      .catch(() => setOccupancy(null));
  }, [selectedLocation]);

  async function handleCheckIn(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId) return;
    setIsChecking(true);

    try {
      await api.post("/v1/check-ins", {
        client_id: clientId,
        check_in_method: "manual",
        ...(selectedLocation ? { location_id: selectedLocation } : {}),
      });
      toast.success("Client checked in");
      setClientId("");
      fetchCheckIns();
      if (selectedLocation) {
        api
          .get<{ data: Occupancy }>(
            `/v1/locations/${selectedLocation}/occupancy`
          )
          .then((res) => setOccupancy(res.data))
          .catch(() => {});
      }
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Check-in failed"
      );
    } finally {
      setIsChecking(false);
    }
  }

  async function handleCheckout(checkInId: string) {
    try {
      await api.post(`/v1/check-ins/${checkInId}/checkout`);
      toast.success("Checked out");
      fetchCheckIns();
      if (selectedLocation) {
        api
          .get<{ data: Occupancy }>(
            `/v1/locations/${selectedLocation}/occupancy`
          )
          .then((res) => setOccupancy(res.data))
          .catch(() => {});
      }
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Checkout failed"
      );
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <ClipboardCheck className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Check-ins</h1>
          <p className="text-muted-foreground">
            Manage gym attendance
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {occupancy && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <MapPin className="h-4 w-4" />
                Current Occupancy
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {occupancy.active_count}
                {occupancy.capacity && (
                  <span className="text-lg text-muted-foreground ml-1">
                    / {occupancy.capacity}
                  </span>
                )}
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="flex items-end gap-4 flex-wrap">
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Location</Label>
          <Select value={selectedLocation} onValueChange={setSelectedLocation}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All locations" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All locations</SelectItem>
              {locations.map((loc) => (
                <SelectItem key={loc.location_id} value={loc.location_id}>
                  {loc.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Date</Label>
          <Input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            className="w-48"
          />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserCheck className="h-5 w-5" />
            Quick Check-in
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCheckIn} className="flex items-end gap-4">
            <div className="flex-1 space-y-2">
              <Label>Client ID</Label>
              <Input
                placeholder="Enter client UUID or scan QR"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={isChecking || !clientId}>
              {isChecking && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Check In
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Client</TableHead>
              <TableHead>Method</TableHead>
              <TableHead>Checked In</TableHead>
              <TableHead>Checked Out</TableHead>
              <TableHead>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : checkIns.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  No check-ins today
                </TableCell>
              </TableRow>
            ) : (
              checkIns.map((ci) => (
                <TableRow key={ci.check_in_id}>
                  <TableCell className="font-mono text-sm">
                    {ci.client_id.slice(0, 8)}...
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{ci.check_in_method}</Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(ci.checked_in_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </TableCell>
                  <TableCell>
                    {ci.checked_out_at
                      ? new Date(ci.checked_out_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "\u2014"}
                  </TableCell>
                  <TableCell>
                    {!ci.checked_out_at && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleCheckout(ci.check_in_id)}
                      >
                        Checkout
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
