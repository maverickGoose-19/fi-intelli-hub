import {
  clusterMapMock,
  clustersMock,
  dashboardMock,
  entitiesMock,
  predictionAnalyticsMock,
  sourcesMock,
} from "@/lib/mock-data";
import { getServerApiBaseUrl } from "@/lib/api-base-url";
import { Cluster, DashboardResponse, Entity, PredictionAnalyticsResponse, Source } from "@/lib/types";

const IS_BUILD_TIME = process.env.NEXT_PHASE === "phase-production-build";
const HAS_EXPLICIT_API_BASE_URL = Boolean(
  process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL,
);

async function fetchFromApi<T>(path: string, fallback: T): Promise<T> {
  if (IS_BUILD_TIME && !HAS_EXPLICIT_API_BASE_URL) {
    return fallback;
  }
  const apiBaseUrl = getServerApiBaseUrl();
  try {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      next: { revalidate: 30 },
    });
    if (!response.ok) {
      console.error(`[api] request failed`, { path, status: response.status, apiBaseUrl });
      throw new Error(`Request failed for ${path}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    console.error(`[api] falling back to mock payload`, { path, apiBaseUrl, error });
    return fallback;
  }
}

export async function getCurrentDashboard(): Promise<DashboardResponse> {
  return fetchFromApi("/api/dashboard/current", dashboardMock);
}

export async function getPredictionAnalytics(): Promise<PredictionAnalyticsResponse> {
  return fetchFromApi("/api/predictions/next-race", predictionAnalyticsMock);
}

export async function getClusters(): Promise<Cluster[]> {
  const payload = await fetchFromApi<{ items: Cluster[] }>("/api/clusters", { items: clustersMock });
  return payload.items;
}

export async function getCluster(id: string): Promise<Cluster | null> {
  const payload = await fetchFromApi<{ cluster: Cluster | null }>(`/api/clusters/${id}`, {
    cluster: clusterMapMock[id] || null,
  });
  return payload.cluster;
}

export async function getSources(): Promise<Source[]> {
  const payload = await fetchFromApi<{ items: Source[] }>("/api/sources", { items: sourcesMock });
  return payload.items;
}

export async function getEntities(): Promise<Entity[]> {
  const payload = await fetchFromApi<{ items: Entity[] }>("/api/entities", { items: entitiesMock });
  return payload.items;
}

export async function syncLatestOpenF1(includeArticles: boolean = true) {
  const response = await fetch(`/api/sync/openf1?include_articles=${includeArticles ? "true" : "false"}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Sync failed" }));
    throw new Error(payload.detail || "Sync failed");
  }
  return response.json() as Promise<{
    sync: {
      status: string;
      message: string;
    };
  }>;
}
