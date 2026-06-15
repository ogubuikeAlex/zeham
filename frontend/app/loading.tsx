import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";

export default function Loading() {
  return (
    <div className="mx-auto max-w-[1400px] px-4 py-10 lg:px-6">
      <LoadingSkeleton rows={6} />
    </div>
  );
}
