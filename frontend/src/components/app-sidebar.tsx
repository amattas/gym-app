"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Calendar,
  ClipboardCheck,
  CreditCard,
  Dumbbell,
  FileText,
  Home,
  MapPin,
  Settings,
  Users,
  UserCog,
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

const navItems = [
  { title: "Dashboard", href: "/dashboard", icon: Home },
  { title: "Clients", href: "/clients", icon: Users },
  { title: "Trainers", href: "/trainers", icon: UserCog },
  { title: "Workouts", href: "/workouts", icon: Dumbbell },
  { title: "Programs", href: "/programs", icon: FileText },
  { title: "Schedules", href: "/schedules", icon: Calendar },
  { title: "Check-ins", href: "/check-ins", icon: ClipboardCheck },
  { title: "Memberships", href: "/memberships", icon: CreditCard },
  { title: "Locations", href: "/locations", icon: MapPin },
  { title: "Exercises", href: "/exercises", icon: Dumbbell },
  { title: "Analytics", href: "/analytics", icon: BarChart3 },
  { title: "Settings", href: "/settings", icon: Settings },
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
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => (
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
      </SidebarContent>
    </Sidebar>
  );
}
