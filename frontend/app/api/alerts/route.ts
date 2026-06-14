import { NextResponse } from "next/server";
import { getAlerts } from "@/lib/api";

export async function GET() {
  return NextResponse.json(await getAlerts());
}
