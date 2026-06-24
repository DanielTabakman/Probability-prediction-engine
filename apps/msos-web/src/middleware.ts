import { randomUUID } from "crypto";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { MSOS_SESSION_COOKIE } from "@/lib/msosSession";

export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  if (!request.cookies.get(MSOS_SESSION_COOKIE)?.value) {
    response.cookies.set(MSOS_SESSION_COOKIE, randomUUID(), {
      path: "/",
      maxAge: 60 * 60 * 24 * 365,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
    });
  }
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
