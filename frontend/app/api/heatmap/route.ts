import { NextResponse } from "next/server";
import { getHeatmap } from "@/lib/api";

export async function GET() {
  return NextResponse.json(await getHeatmap());
}
