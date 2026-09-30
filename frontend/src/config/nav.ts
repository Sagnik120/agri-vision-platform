import { History, LayoutDashboard, ScanLine, Settings, type LucideIcon } from "lucide-react";

import type { MessageKey } from "@/core/i18n";

export interface NavItem {
  href: string;
  label: MessageKey;
  icon: LucideIcon;
  /** Rendered as the raised centre button in the mobile tab bar. */
  primary?: boolean;
}

/** Single source of truth for app navigation — add new sections here. */
export const APP_NAV: NavItem[] = [
  { href: "/dashboard", label: "nav.dashboard", icon: LayoutDashboard },
  { href: "/diagnose", label: "nav.diagnose", icon: ScanLine, primary: true },
  { href: "/history", label: "nav.history", icon: History },
  { href: "/settings", label: "nav.settings", icon: Settings },
];
