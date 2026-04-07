import { NextResponse } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api-base-url";

type RouteContext = {
  params: Promise<{
    id: string;
  }>;
};

export async function POST(_: Request, context: RouteContext) {
  const { id } = await context.params;
  const backendUrl = new URL(`/api/clusters/${id}/resummarize`, getServerApiBaseUrl());

  try {
    const response = await fetch(backendUrl.toString(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : { detail: (await response.text()) || "Request failed" };

    if (!response.ok) {
      console.error("[api-proxy] resummarize request failed", {
        status: response.status,
        backendUrl: backendUrl.toString(),
        payload,
      });
      return NextResponse.json(payload, { status: response.status });
    }

    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    console.error("[api-proxy] resummarize request errored", {
      backendUrl: backendUrl.toString(),
      error,
    });
    return NextResponse.json({ detail: "Editorial service unavailable" }, { status: 502 });
  }
}
