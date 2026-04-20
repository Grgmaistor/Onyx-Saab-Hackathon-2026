/**
 * Module-level cache for cross-page data persistence.
 *
 * Persists across client-side navigation (Next.js App Router doesn't re-evaluate
 * modules on route change). Data lives in browser memory until a full page
 * reload or manual invalidation.
 *
 * Usage:
 *   const cached = getCached<SomeType>("knowledge:doctrine", 60_000);
 *   if (cached) return cached;
 *   const fresh = await fetchApi(...);
 *   setCached("knowledge:doctrine", fresh);
 */

type Entry = { data: unknown; ts: number };

const cache = new Map<string, Entry>();

export function getCached<T>(key: string, maxAgeMs: number): T | null {
  const entry = cache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.ts > maxAgeMs) return null;
  return entry.data as T;
}

export function setCached(key: string, data: unknown): void {
  cache.set(key, { data, ts: Date.now() });
}

export function invalidate(keyOrPrefix: string): void {
  for (const k of Array.from(cache.keys())) {
    if (k === keyOrPrefix || k.startsWith(keyOrPrefix + ":")) {
      cache.delete(k);
    }
  }
}

export function clearCache(): void {
  cache.clear();
}

/**
 * Fetches `fetcher()` or returns cached value if fresh.
 * Use this to wrap any API call where stale-while-revalidate is OK.
 */
export async function cachedFetch<T>(
  key: string,
  maxAgeMs: number,
  fetcher: () => Promise<T>,
): Promise<T> {
  const cached = getCached<T>(key, maxAgeMs);
  if (cached !== null) return cached;
  const fresh = await fetcher();
  setCached(key, fresh);
  return fresh;
}
