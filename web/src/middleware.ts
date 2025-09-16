import { NextResponse } from "next/server";

export default function middleware(req: any) {
  // Skip authentication entirely for now
  return NextResponse.next();
}

export const config = { matcher: ["/((?!_next|.*\\..*|api).*)"] };