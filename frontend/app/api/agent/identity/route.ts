import { NextResponse } from "next/server";
import { getAgentIdentity } from "@/lib/api";

export async function GET() {
  return NextResponse.json(await getAgentIdentity());
}
