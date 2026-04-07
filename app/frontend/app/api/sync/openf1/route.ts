import { NextRequest, NextResponse } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api-base-url";

export async function POST(request: NextRequest) {
  const backendUrl = new URL("/api/sync/openf1", getServerApiBaseUrl());
  backendUrl.search = request.nextUrl.searchParams.toString();

  try {
    const response = await fetch(backendUrl.toString(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : { detail: (await response.text()) || "Sync failed" };

    if (!response.ok) {
      console.error("[sync-proxy] backend sync request failed", {
        status: response.status,
        backendUrl: backendUrl.toString(),
        payload,
      });
      return NextResponse.json(payload, { status: response.status });
    }

    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    console.error("[sync-proxy] backend sync request errored", {
      backendUrl: backendUrl.toString(),
      error,
    });
    return NextResponse.json({ detail: "Sync service unavailable" }, { status: 502 });
  }
}
