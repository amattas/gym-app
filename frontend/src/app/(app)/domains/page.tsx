"use client";

import { useEffect, useState } from "react";
import { Globe, Loader2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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

interface CustomDomain {
  domain_id: string;
  domain: string;
  domain_type: string;
  status: string;
  dns_records: Record<string, unknown> | null;
  verified_at: string | null;
}

export default function DomainsPage() {
  const [domains, setDomains] = useState<CustomDomain[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [domain, setDomain] = useState("");
  const [domainType, setDomainType] = useState("email");
  const [isCreating, setIsCreating] = useState(false);

  function fetchDomains() {
    api
      .get<{ data: CustomDomain[] }>("/v1/domains")
      .then((res) => setDomains(res.data))
      .catch((err) => {
        toast.error(err instanceof Error ? err.message : "Failed to load domains");
      })
      .finally(() => setIsLoading(false));
  }

  useEffect(() => {
    fetchDomains();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post("/v1/domains", { domain, domain_type: domainType });
      toast.success("Domain added");
      setShowCreate(false);
      setDomain("");
      fetchDomains();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to add");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleDelete(domainId: string) {
    try {
      await api.delete(`/v1/domains/${domainId}`);
      toast.success("Domain deleted");
      fetchDomains();
    } catch {
      toast.error("Failed to delete domain");
    }
  }

  async function handleVerify(domainId: string) {
    try {
      await api.post(`/v1/domains/${domainId}/verify`);
      toast.success("Verification started");
      fetchDomains();
    } catch {
      toast.error("Verification failed");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Globe className="h-8 w-8 text-muted-foreground" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Custom Domains</h1>
            <p className="text-muted-foreground">Email and login domain configuration</p>
          </div>
        </div>
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Add Domain
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Custom Domain</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label>Domain</Label>
                <Input
                  placeholder="mail.yourgym.com"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Type</Label>
                <Select value={domainType} onValueChange={setDomainType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="login">Login</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" disabled={isCreating} className="w-full">
                {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Add Domain
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Domain</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : domains.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  No custom domains configured
                </TableCell>
              </TableRow>
            ) : (
              domains.map((d) => (
                <TableRow key={d.domain_id}>
                  <TableCell className="font-medium">{d.domain}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{d.domain_type}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        d.status === "active"
                          ? "default"
                          : d.status === "failed"
                            ? "destructive"
                            : "secondary"
                      }
                    >
                      {d.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {d.status === "pending" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleVerify(d.domain_id)}
                        >
                          Verify
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDelete(d.domain_id)}
                      >
                        Delete
                      </Button>
                    </div>
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
