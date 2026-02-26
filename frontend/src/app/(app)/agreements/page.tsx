"use client";

import { useEffect, useState } from "react";
import { FileText, Loader2, Plus, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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

interface AgreementTemplate {
  agreement_template_id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  requires_signature: boolean;
  created_at: string;
}

interface Envelope {
  envelope_id: string;
  signer_name: string;
  signer_email: string;
  status: string;
  created_at: string;
  signed_at: string | null;
}

export default function AgreementsPage() {
  const [templates, setTemplates] = useState<AgreementTemplate[]>([]);
  const [envelopes, setEnvelopes] = useState<Envelope[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [content, setContent] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    Promise.allSettled([
      api.get<{ data: AgreementTemplate[] }>("/v1/agreements/templates"),
      api.get<{ data: Envelope[] }>("/v1/agreements/envelopes"),
    ]).then(([tResult, eResult]) => {
      if (tResult.status === "fulfilled") setTemplates(tResult.value.data);
      if (eResult.status === "fulfilled") setEnvelopes(eResult.value.data);
      setIsLoading(false);
    });
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post("/v1/agreements/templates", { name, content });
      toast.success("Template created");
      setShowCreate(false);
      setName("");
      setContent("");
      const res = await api.get<{ data: AgreementTemplate[] }>("/v1/agreements/templates");
      setTemplates(res.data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create");
    } finally {
      setIsCreating(false);
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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <FileText className="h-8 w-8 text-muted-foreground" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Agreements</h1>
            <p className="text-muted-foreground">E-signature templates and envelopes</p>
          </div>
        </div>
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" /> New Template
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Agreement Template</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label>Content</Label>
                <Textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={6}
                  required
                />
              </div>
              <Button type="submit" disabled={isCreating} className="w-full">
                {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs defaultValue="templates">
        <TabsList>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="envelopes">Sent Agreements</TabsTrigger>
        </TabsList>

        <TabsContent value="templates">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Signature Required</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {templates.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center py-8">
                      No templates
                    </TableCell>
                  </TableRow>
                ) : (
                  templates.map((t) => (
                    <TableRow key={t.agreement_template_id}>
                      <TableCell className="font-medium">{t.name}</TableCell>
                      <TableCell>{t.requires_signature ? "Yes" : "No"}</TableCell>
                      <TableCell>
                        <Badge variant={t.is_active ? "default" : "secondary"}>
                          {t.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        <TabsContent value="envelopes">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Signer</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Signed</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {envelopes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-8">
                      No agreements sent
                    </TableCell>
                  </TableRow>
                ) : (
                  envelopes.map((e) => (
                    <TableRow key={e.envelope_id}>
                      <TableCell className="font-medium">{e.signer_name}</TableCell>
                      <TableCell>{e.signer_email}</TableCell>
                      <TableCell>
                        <Badge
                          variant={e.status === "signed" ? "default" : "secondary"}
                        >
                          {e.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {e.signed_at
                          ? new Date(e.signed_at).toLocaleDateString()
                          : "—"}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
