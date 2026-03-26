import { getDb } from '~/server/utils/neon';

export default defineEventHandler(async (event) => {
    const sql = getDb();
    if (!sql) return { configured: false, financials: [] };

    const { ticker } = getQuery(event) as { ticker?: string };
    if (!ticker) throw createError({ statusCode: 400, statusMessage: 'ticker is required' });

    const rows = await sql`
    SELECT * FROM financials
    WHERE company_ticker = ${ticker}
    ORDER BY filing_date ASC
  `;
    return { configured: true, financials: rows };
});
