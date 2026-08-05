import {
  CheckCircle2,
  Eye,
  Inbox,
  LayoutGrid,
  ListTodo,
  Loader2,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface ColumnMeta {
  icon: LucideIcon;
  accent: string;
  chipBg: string;
}

const COLUMN_META: Record<string, ColumnMeta> = {
  backlog: { icon: Inbox, accent: "#94a3b8", chipBg: "rgba(148,163,184,0.12)" },
  todo: { icon: ListTodo, accent: "#209dd7", chipBg: "rgba(32,157,215,0.12)" },
  "in-progress": { icon: Loader2, accent: "#ecad0a", chipBg: "rgba(236,173,10,0.12)" },
  review: { icon: Eye, accent: "#a855f7", chipBg: "rgba(168,85,247,0.12)" },
  done: { icon: CheckCircle2, accent: "#22c55e", chipBg: "rgba(34,197,94,0.12)" },
};

export function getColumnMeta(id: string): ColumnMeta {
  const key = (id || "").replace(/^col-/, "");
  return COLUMN_META[key] ?? { icon: LayoutGrid, accent: "#ecad0a", chipBg: "rgba(236,173,10,0.12)" };
}
