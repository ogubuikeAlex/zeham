import type { LucideIcon } from "lucide-react";

export function EmptyState({ icon: Icon, title, message, action }: { icon: LucideIcon; title: string; message: string; action?: React.ReactNode }) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center rounded-lg border border-dashed border-hairline bg-canvas p-10 text-center">
      <Icon className="mb-3 text-mute" size={28} />
      <h3 className="text-base font-medium text-ink">{title}</h3>
      <p className="mt-1 max-w-md text-sm text-body">{message}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
