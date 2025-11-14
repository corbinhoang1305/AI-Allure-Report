"use client";

import { Activity, LayoutDashboard, FolderKanban, Flame, FileBarChart, Target, Zap, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard", badge: null },
  { icon: FolderKanban, label: "Projects", href: "/projects", badge: null },
  { icon: Flame, label: "Flaky Tests (AI)", href: "/flaky-tests", badge: null },
  { icon: FileBarChart, label: "Test Runs", href: "/test-runs", badge: null },
  { icon: Target, label: "Root Cause Analysis (AI)", href: "/rca", badge: "AI", active: true },
  { icon: Zap, label: "Test Optimization (AI)", href: "/optimization", badge: null },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-gray-800 bg-qualify-dark-darker flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2 border-b border-gray-800 px-6 py-4">
        <Activity className="h-6 w-6 text-qualify-teal" />
        <span className="text-lg font-bold text-white">QUALIFY.AI</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.active && pathname.startsWith("/rca"));
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-qualify-teal/10 text-qualify-teal"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="flex-1">{item.label}</span>
              {item.badge && (
                <span className="rounded-full bg-qualify-teal px-2 py-0.5 text-xs font-semibold text-white">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className="border-t border-gray-800 p-3">
        <div className="mb-3 space-y-1">
          <div className="text-xs font-semibold text-gray-500 px-3 py-1">Integrations</div>
          <Link
            href="/settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 hover:bg-gray-800 hover:text-white"
          >
            <Settings className="h-5 w-5" />
            <span>Settings</span>
          </Link>
        </div>

        {/* User Profile */}
        <div className="flex items-center gap-3 rounded-lg bg-gray-800 px-3 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-qualify-teal text-sm font-semibold text-white">
            U
          </div>
          <div className="flex-1 text-xs">
            <div className="font-medium text-white">User</div>
            <div className="text-gray-400">Admin</div>
          </div>
        </div>
      </div>
    </aside>
  );
}

