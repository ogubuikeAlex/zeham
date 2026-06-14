"use client";

import { useEffect, useState } from "react";
import { relativeTime } from "@/lib/formatters";

export function RelativeTime({ value }: { value: string }) {
  const [label, setLabel] = useState(() => relativeTime(value));
  useEffect(() => {
    const id = setInterval(() => setLabel(relativeTime(value)), 15000);
    return () => clearInterval(id);
  }, [value]);
  return <time dateTime={value}>{label}</time>;
}
