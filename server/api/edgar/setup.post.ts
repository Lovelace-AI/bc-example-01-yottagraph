import { getDb } from '~/server/utils/neon';

export default defineEventHandler(async () => {
    const sql = getDb();
    if (!sql) throw createError({ statusCode: 503, statusMessage: 'Database not configured' });

    await sql`CREATE TABLE IF NOT EXISTS companies (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    neid TEXT,
    cik TEXT,
    last_sync_at TIMESTAMPTZ
  )`;

    await sql`CREATE TABLE IF NOT EXISTS filings (
    id SERIAL PRIMARY KEY,
    company_ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    accession_number TEXT,
    form_type TEXT,
    filing_date DATE,
    name TEXT,
    neid TEXT,
    UNIQUE(company_ticker, neid)
  )`;

    await sql`CREATE TABLE IF NOT EXISTS financials (
    id SERIAL PRIMARY KEY,
    company_ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    filing_date DATE NOT NULL,
    total_revenue NUMERIC,
    net_income NUMERIC,
    total_assets NUMERIC,
    total_liabilities NUMERIC,
    shareholders_equity NUMERIC,
    shares_outstanding NUMERIC,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_ticker, filing_date)
  )`;

    return { ok: true };
});
