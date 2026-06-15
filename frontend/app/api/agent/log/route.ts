import { NextResponse } from "next/server";
import { getDetectionLogs } from "@/lib/api";

export async function GET() {
  return NextResponse.json(await getDetectionLogs());
}
