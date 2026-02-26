"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
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

interface Program {
  program_id: string;
  name: string;
  description: string | null;
  template_scope: string;
  created_at: string;
}

export default function ProgramsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ data: Program[] }>("/v1/programs")
      .then((res) => setPrograms(res.data))
      .catch((err) => { toast.error(err instanceof Error ? err.message : "Failed to load programs"); })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Programs</h1>
          <p className="text-muted-foreground">
            Training program templates
          </p>
        </div>
        <Button asChild>
          <Link href="/programs/new">
            <Plus className="mr-2 h-4 w-4" />
            New Program
          </Link>
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Scope</TableHead>
              <TableHead>Created</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : programs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  No programs found
                </TableCell>
              </TableRow>
            ) : (
              programs.map((p) => (
                <TableRow key={p.program_id}>
                  <TableCell>
                    <Link
                      href={`/programs/${p.program_id}`}
                      className="font-medium hover:underline"
                    >
                      {p.name}
                    </Link>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {p.description || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{p.template_scope}</Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(p.created_at).toLocaleDateString()}
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
