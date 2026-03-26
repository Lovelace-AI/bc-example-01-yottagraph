import { neon, type NeonQueryFunction } from '@neondatabase/serverless';

let _sql: NeonQueryFunction | null = null;

/**
 * Check whether Neon Postgres is configured with a valid connection string.
 * Returns false for Vercel's encrypted blobs that only work in deployed builds.
 */
export function isDbConfigured(): boolean {
    const url = process.env.DATABASE_URL;
    return Boolean(url && (url.startsWith('postgres') || url.startsWith('pg:')));
}

/**
 * Get the Neon SQL query function. Uses DATABASE_URL env var that Vercel
 * auto-injects when a Neon store is connected.
 *
 * Returns null if DATABASE_URL is not set or contains an encrypted blob
 * (Vercel encrypts integration env vars; they only work in deployed builds).
 */
export function getDb(): NeonQueryFunction | null {
    if (_sql) return _sql;
    const url = process.env.DATABASE_URL;
    if (!url || !url.startsWith('postgres')) return null;
    _sql = neon(url);
    return _sql;
}
