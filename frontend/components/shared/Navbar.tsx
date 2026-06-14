"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { ConnectionIndicator } from "@/components/shared/ConnectionIndicator";
import { useWebSocketStatus } from "@/hooks/useWebSocket";

const links = [
  { href: "/", label: "Alerts" },
  { href: "/agent", label: "Agent" },
  { href: "/watch", label: "Watch" },
  { href: "/heatmap", label: "Heatmap" }
];

export function Navbar() {
  const pathname = usePathname();
  const { connectionState } = useWebSocketStatus();

  return (
    <header className="sticky top-0 z-40 border-b border-hairline bg-canvas/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-[1400px] items-center gap-6 px-4 lg:px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold text-ink">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-ink text-white">
            <ShieldCheck size={16} />
          </span>
          Zeham
        </Link>
        <nav className="flex flex-1 items-center gap-1 overflow-x-auto">
          {links.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-full px-3 py-2 text-sm transition ${
                  active ? "bg-canvas-soft-2 text-ink" : "text-body hover:bg-canvas-soft hover:text-ink"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
        <ConnectionIndicator state={connectionState} />
      </div>
    </header>
  );
}
