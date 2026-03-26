import { getDb } from '~/server/utils/neon';

export default defineEventHandler(async () => {
    const sql = getDb();
    if (!sql) return { configured: false, companies: [] };

    try {
        const rows = await sql`
      SELECT c.*,
        (SELECT COUNT(*)::int FROM filings f WHERE f.company_ticker = c.ticker) AS filing_count,
        (SELECT json_build_object(
          'total_revenue', fin.total_revenue,
          'net_income', fin.net_income,
          'total_assets', fin.total_assets,
          'total_liabilities', fin.total_liabilities,
          'shareholders_equity', fin.shareholders_equity,
          'shares_outstanding', fin.shares_outstanding,
          'filing_date', fin.filing_date
        ) FROM financials fin
         WHERE fin.company_ticker = c.ticker
         ORDER BY fin.filing_date DESC LIMIT 1) AS latest_financials
      FROM companies c
      ORDER BY c.ticker
    `;
        return { configured: true, companies: rows };
    } catch (e: any) {
        if (e.message?.includes('does not exist')) {
            return { configured: true, companies: [] };
        }
        throw e;
    }
});
