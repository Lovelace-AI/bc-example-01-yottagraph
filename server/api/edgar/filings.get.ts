import { getDb } from '~/server/utils/neon';

export default defineEventHandler(async (event) => {
    const sql = getDb();
    if (!sql) return { configured: false, filings: [] };

    const { ticker } = getQuery(event) as { ticker?: string };
    if (!ticker) throw createError({ statusCode: 400, statusMessage: 'ticker is required' });

    const rows = await sql`
    SELECT * FROM filings
    WHERE company_ticker = ${ticker}
    ORDER BY filing_date DESC NULLS LAST
    LIMIT 100
  `;
    return { configured: true, filings: rows };
});
