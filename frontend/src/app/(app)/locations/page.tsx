"use client";

import { useEffect, useState } from "react";
import { MapPin } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface Location {
  location_id: string;
  name: string;
  address: string | null;
  city: string | null;
  state: string | null;
  capacity: number | null;
  is_active: boolean;
}

export default function LocationsPage() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      const gymId = localStorage.getItem("gym_id");
      if (!gymId) return;
      try {
        const res = await api.get<{ data: Location[] }>(
          `/v1/gyms/${gymId}/locations`
        );
        setLocations(res.data);
      } catch {}
    };
    load().finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Locations</h1>
        <p className="text-muted-foreground">Your gym locations</p>
      </div>

      {locations.length === 0 ? (
        <p className="text-center text-muted-foreground py-16">
          No locations configured
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {locations.map((loc) => (
            <Card key={loc.location_id}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  {loc.name}
                </CardTitle>
                <Badge variant={loc.is_active ? "default" : "secondary"}>
                  {loc.is_active ? "Active" : "Inactive"}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-1 text-sm text-muted-foreground">
                {loc.address && <p>{loc.address}</p>}
                {(loc.city || loc.state) && (
                  <p>
                    {[loc.city, loc.state].filter(Boolean).join(", ")}
                  </p>
                )}
                {loc.capacity && <p>Capacity: {loc.capacity}</p>}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
