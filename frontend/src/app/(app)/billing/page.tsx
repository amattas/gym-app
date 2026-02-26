"use client";

import { useEffect, useState } from "react";
import { CreditCard, Loader2, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

interface StripeAccount {
  stripe_account_id: string;
  onboarding_status: string;
  charges_enabled: boolean;
  payouts_enabled: boolean;
  processing_fee_percentage: number | null;
  pass_fees_to_client: boolean;
}

interface DiscountCode {
  discount_code_id: string;
  code: string;
  discount_type: string;
  amount: number;
  times_used: number;
  max_uses: number | null;
  is_active: boolean;
}

export default function BillingPage() {
  const [account, setAccount] = useState<StripeAccount | null>(null);
  const [discounts, setDiscounts] = useState<DiscountCode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showDiscount, setShowDiscount] = useState(false);
  const [code, setCode] = useState("");
  const [discountType, setDiscountType] = useState("percentage");
  const [amount, setAmount] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    Promise.allSettled([
      api.get<{ data: StripeAccount }>("/v1/billing/stripe/account"),
      api.get<{ data: DiscountCode[] }>("/v1/billing/discount-codes"),
    ]).then(([acctResult, discountResult]) => {
      if (acctResult.status === "fulfilled") setAccount(acctResult.value.data);
      if (discountResult.status === "fulfilled") setDiscounts(discountResult.value.data);
      setIsLoading(false);
    });
  }, []);

  async function handleCreateDiscount(e: React.FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post("/v1/billing/discount-codes", {
        code,
        discount_type: discountType,
        amount: parseFloat(amount),
      });
      toast.success("Discount code created");
      setShowDiscount(false);
      setCode("");
      setAmount("");
      const res = await api.get<{ data: DiscountCode[] }>("/v1/billing/discount-codes");
      setDiscounts(res.data);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleConnect() {
    try {
      const res = await api.post<{ onboarding_url: string }>("/v1/billing/stripe/connect", {
        return_url: window.location.href,
        refresh_url: window.location.href,
      });
      window.open(res.onboarding_url, "_blank");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to connect");
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
      <div className="flex items-center gap-4">
        <CreditCard className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
          <p className="text-muted-foreground">Stripe payments and discount codes</p>
        </div>
      </div>

      <Tabs defaultValue="stripe">
        <TabsList>
          <TabsTrigger value="stripe">Stripe Account</TabsTrigger>
          <TabsTrigger value="discounts">Discount Codes</TabsTrigger>
        </TabsList>

        <TabsContent value="stripe">
          <Card>
            <CardHeader>
              <CardTitle>Stripe Connect</CardTitle>
            </CardHeader>
            <CardContent>
              {account ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Status</p>
                      <Badge
                        variant={
                          account.onboarding_status === "complete" ? "default" : "secondary"
                        }
                      >
                        {account.onboarding_status}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Charges</p>
                      <Badge variant={account.charges_enabled ? "default" : "secondary"}>
                        {account.charges_enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Processing Fee</p>
                      <p>{account.processing_fee_percentage ?? "N/A"}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Pass Fees to Client</p>
                      <p>{account.pass_fees_to_client ? "Yes" : "No"}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="mb-4 text-muted-foreground">
                    Connect your Stripe account to accept payments
                  </p>
                  <Button onClick={handleConnect}>Connect Stripe</Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="discounts">
          <div className="flex justify-end mb-4">
            <Dialog open={showDiscount} onOpenChange={setShowDiscount}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" /> New Code
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Discount Code</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreateDiscount} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Code</Label>
                    <Input value={code} onChange={(e) => setCode(e.target.value)} required />
                  </div>
                  <div className="space-y-2">
                    <Label>Amount</Label>
                    <Input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
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
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Used</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {discounts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8">
                      No discount codes
                    </TableCell>
                  </TableRow>
                ) : (
                  discounts.map((d) => (
                    <TableRow key={d.discount_code_id}>
                      <TableCell className="font-mono">{d.code}</TableCell>
                      <TableCell>{d.discount_type}</TableCell>
                      <TableCell>
                        {d.discount_type === "percentage" ? `${d.amount}%` : `$${d.amount}`}
                      </TableCell>
                      <TableCell>
                        {d.times_used}
                        {d.max_uses ? ` / ${d.max_uses}` : ""}
                      </TableCell>
                      <TableCell>
                        <Badge variant={d.is_active ? "default" : "secondary"}>
                          {d.is_active ? "Active" : "Inactive"}
                        </Badge>
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
