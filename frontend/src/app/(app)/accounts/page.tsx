"use client";

import { useState } from "react";
import { Users, Loader2, Plus, Search } from "lucide-react";
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

interface Account {
  account_id: string;
  account_type: string;
  billing_email: string | null;
  created_at: string;
}

interface Member {
  client_id: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  role?: string;
}

export default function AccountsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [accountType, setAccountType] = useState("individual");
  const [billingEmail, setBillingEmail] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [searchId, setSearchId] = useState("");
  const [account, setAccount] = useState<Account | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showAddMember, setShowAddMember] = useState(false);
  const [newMemberClientId, setNewMemberClientId] = useState("");
  const [isAddingMember, setIsAddingMember] = useState(false);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post("/v1/accounts", {
        account_type: accountType,
        billing_email: billingEmail || null,
      });
      toast.success("Account created");
      setShowCreate(false);
      setBillingEmail("");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!searchId) return;
    setIsSearching(true);
    try {
      const [acctRes, membersRes] = await Promise.all([
        api.get<{ data: Account }>(`/v1/accounts/${encodeURIComponent(searchId)}`),
        api
          .get<{ data: Member[] }>(`/v1/accounts/${encodeURIComponent(searchId)}/members`)
          .catch((err) => { toast.error(err instanceof Error ? err.message : "Failed to load account members"); return { data: [] as Member[] }; }),
      ]);
      setAccount(acctRes.data);
      setMembers(membersRes.data);
    } catch {
      toast.error("Account not found");
      setAccount(null);
      setMembers([]);
    } finally {
      setIsSearching(false);
    }
  }

  async function handleAddMember(e: React.FormEvent) {
    e.preventDefault();
    if (!account) return;
    setIsAddingMember(true);
    try {
      await api.post(`/v1/accounts/${account.account_id}/members`, {
        client_id: newMemberClientId,
      });
      toast.success("Member added");
      setShowAddMember(false);
      setNewMemberClientId("");
      const res = await api.get<{ data: Member[] }>(
        `/v1/accounts/${account.account_id}/members`
      );
      setMembers(res.data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to add member");
    } finally {
      setIsAddingMember(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Users className="h-8 w-8 text-muted-foreground" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Accounts</h1>
            <p className="text-muted-foreground">Family and individual accounts</p>
          </div>
        </div>
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" /> New Account
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Account</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label>Account Type</Label>
                <Select value={accountType} onValueChange={setAccountType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="individual">Individual</SelectItem>
                    <SelectItem value="family">Family</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Billing Email</Label>
                <Input
                  type="email"
                  value={billingEmail}
                  onChange={(e) => setBillingEmail(e.target.value)}
                />
              </div>
              <Button type="submit" disabled={isCreating} className="w-full">
                {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create Account
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle>Search Account</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex items-end gap-4">
            <div className="flex-1 space-y-2">
              <Label>Account ID</Label>
              <Input
                placeholder="Enter account UUID"
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={isSearching || !searchId}>
              {isSearching ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Search className="mr-2 h-4 w-4" />
              )}
              Search
            </Button>
          </form>
        </CardContent>
      </Card>

      {account && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Account Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Account ID</p>
                  <p className="font-mono text-sm">{account.account_id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Type</p>
                  <Badge variant="outline">{account.account_type}</Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Billing Email</p>
                  <p>{account.billing_email || "\u2014"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Created</p>
                  <p>{new Date(account.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Members</h2>
            <Dialog open={showAddMember} onOpenChange={setShowAddMember}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="mr-2 h-4 w-4" /> Add Member
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Member</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleAddMember} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Client ID</Label>
                    <Input
                      placeholder="Enter client UUID"
                      value={newMemberClientId}
                      onChange={(e) => setNewMemberClientId(e.target.value)}
                      required
                    />
                  </div>
                  <Button type="submit" disabled={isAddingMember} className="w-full">
                    {isAddingMember && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Add Member
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Client ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-8">
                      No members
                    </TableCell>
                  </TableRow>
                ) : (
                  members.map((m) => (
                    <TableRow key={m.client_id}>
                      <TableCell className="font-mono text-sm">
                        {m.client_id.slice(0, 8)}...
                      </TableCell>
                      <TableCell>
                        {m.first_name && m.last_name
                          ? `${m.first_name} ${m.last_name}`
                          : "\u2014"}
                      </TableCell>
                      <TableCell>{m.email || "\u2014"}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{m.role || "member"}</Badge>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </>
      )}
    </div>
  );
}
