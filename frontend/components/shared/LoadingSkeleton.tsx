export function LoadingSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="h-20 animate-pulse rounded-lg border border-hairline bg-canvas">
          <div className="h-full rounded-lg bg-gradient-to-r from-canvas-soft via-canvas-soft-2 to-canvas-soft" />
        </div>
      ))}
    </div>
  );
}
