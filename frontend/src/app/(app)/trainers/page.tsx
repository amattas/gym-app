"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
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

interface Trainer {
  trainer_id: string;
  first_name: string;
  last_name: string;
  email: string;
  specialties: string[] | null;
  is_active: boolean;
}

export default function TrainersPage() {
  const [trainers, setTrainers] = useState<Trainer[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ data: Trainer[] }>("/v1/trainers")
      .then((res) => setTrainers(res.data))
      .catch((err) => { toast.error(err instanceof Error ? err.message : "Failed to load trainers"); })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Trainers</h1>
        <p className="text-muted-foreground">Manage your training staff</p>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Specialties</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : trainers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  No trainers found
                </TableCell>
              </TableRow>
            ) : (
              trainers.map((trainer) => (
                <TableRow key={trainer.trainer_id}>
                  <TableCell className="font-medium">
                    {trainer.first_name} {trainer.last_name}
                  </TableCell>
                  <TableCell>{trainer.email}</TableCell>
                  <TableCell>
                    <div className="flex gap-1 flex-wrap">
                      {trainer.specialties?.map((s) => (
                        <Badge key={s} variant="outline" className="text-xs">
                          {s}
                        </Badge>
                      )) || "—"}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={trainer.is_active ? "default" : "secondary"}
                    >
                      {trainer.is_active ? "Active" : "Inactive"}
                    </Badge>
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
