import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (!request.nextUrl.pathname.startsWith("/operator")) {
    return NextResponse.next();
  }

  const allowed = (process.env.MSOS_OPERATOR_EMAIL ?? "").trim().toLowerCase();
  if (!allowed) {
    if (process.env.NODE_ENV === "development") {
      return NextResponse.next();
    }
    return new NextResponse("Operator routes require MSOS_OPERATOR_EMAIL", { status: 503 });
  }

  const email = request.headers.get("cf-access-authenticated-user-email");
  if ((email ?? "").trim().toLowerCase() !== allowed) {
    return new NextResponse("Not found", { status: 404 });
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/operator/:path*"],
};
