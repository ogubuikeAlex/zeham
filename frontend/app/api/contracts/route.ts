import { NextResponse } from "next/server";
import { getContracts } from "@/lib/api";

export async function GET() {
  return NextResponse.json(await getContracts());
}
