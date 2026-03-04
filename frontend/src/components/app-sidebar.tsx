"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Bell,
  Calendar,
  Camera,
  ClipboardCheck,
  CreditCard,
  Dumbbell,
  FileText,
  Globe,
  Home,
  MapPin,
  Ruler,
  Settings,
  Shield,
  Target,
  Users,
  UserCog,
  Wallet,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const navSections = [
  {
    label: "Overview",
    items: [
      { title: "Dashboard", href: "/dashboard", icon: Home },
      { title: "Analytics", href: "/analytics", icon: BarChart3 },
    ],
  },
  {
    label: "People",
    items: [
      { title: "Clients", href: "/clients", icon: Users },
      { title: "Trainers", href: "/trainers", icon: UserCog },
      { title: "Accounts", href: "/accounts", icon: Users },
    ],
  },
  {
    label: "Training",
    items: [
      { title: "Workouts", href: "/workouts", icon: Dumbbell },
      { title: "Programs", href: "/programs", icon: FileText },
      { title: "Exercises", href: "/exercises", icon: Dumbbell },
      { title: "Measurements", href: "/measurements", icon: Ruler },
      { title: "Goals", href: "/goals", icon: Target },
      { title: "Progress Photos", href: "/progress-photos", icon: Camera },
    ],
  },
  {
    label: "Operations",
    items: [
      { title: "Schedules", href: "/schedules", icon: Calendar },
      { title: "Check-ins", href: "/check-ins", icon: ClipboardCheck },
      { title: "Memberships", href: "/memberships", icon: CreditCard },
      { title: "Locations", href: "/locations", icon: MapPin },
    ],
  },
  {
    label: "Billing",
    items: [
      { title: "Billing", href: "/billing", icon: Wallet },
      { title: "Agreements", href: "/agreements", icon: FileText },
      { title: "Usage", href: "/usage", icon: BarChart3 },
    ],
  },
  {
    label: "System",
    items: [
      { title: "Notifications", href: "/notifications", icon: Bell },
      { title: "Audit Logs", href: "/audit-logs", icon: Shield },
      { title: "Domains", href: "/domains", icon: Globe },
      { title: "Settings", href: "/settings", icon: Settings },
    ],
  },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar>
      <SidebarHeader className="border-b px-6 py-4">
        <Link href="/dashboard" className="flex items-center gap-2">
          <Dumbbell className="h-6 w-6" />
          <span className="text-lg font-semibold">Gym Manager</span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        {navSections.map((section) => (
          <SidebarGroup key={section.label}>
            <SidebarGroupLabel>{section.label}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {section.items.map((item) => (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      asChild
                      isActive={pathname.startsWith(item.href)}
                    >
                      <Link href={item.href}>
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
    </Sidebar>
  );
}
