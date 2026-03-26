import { getDb } from '~/server/utils/neon';
import { searchEntities, getPidMap, getPropertyValues } from '~/server/utils/gateway';

const TRACKED = [
    { ticker: 'AAPL', searchName: 'Apple Inc' },
    { ticker: 'TSLA', searchName: 'Tesla Inc' },
];

const FINANCIAL_PROPS = [
    'total_revenue',
    'net_income',
    'total_assets',
    'total_liabilities',
    'shareholders_equity',
    'shares_outstanding',
];

export default defineEventHandler(async () => {
    const sql = getDb();
    if (!sql) throw createError({ statusCode: 503, statusMessage: 'Database not configured' });

    await $fetch('/api/edgar/setup', { method: 'POST' });

    const pidMap = await getPidMap();
    const results: any[] = [];

    for (const co of TRACKED) {
        try {
            const searchRes = await searchEntities(co.searchName, 3);
            const match = searchRes.results?.[0]?.matches?.find(
                (m: any) => m.flavor === 'organization'
            );
            if (!match) {
                results.push({ ticker: co.ticker, error: 'Entity not found' });
                continue;
            }
            const neid = match.neid;

            const cikPid = pidMap.get('company_cik')!;
            const tickerPid = pidMap.get('ticker')!;
            const idRes = await getPropertyValues([neid], [cikPid, tickerPid]);
            let cik = '';
            for (const v of idRes.values ?? []) {
                if (v.pid === cikPid && !cik) cik = String(v.value);
            }

            await sql`
        INSERT INTO companies (ticker, name, neid, cik, last_sync_at)
        VALUES (${co.ticker}, ${match.name}, ${neid}, ${cik}, NOW())
        ON CONFLICT (ticker) DO UPDATE SET
          name = EXCLUDED.name, neid = EXCLUDED.neid,
          cik = EXCLUDED.cik, last_sync_at = NOW()
      `;

            // Financial properties (multiple historical values per PID)
            const finPids = FINANCIAL_PROPS.map((n) => pidMap.get(n)).filter(Boolean) as number[];
            const finRes = await getPropertyValues([neid], finPids, true);
            const reversePid = new Map<number, string>();
            for (const [name, pid] of pidMap) {
                if (FINANCIAL_PROPS.includes(name)) reversePid.set(pid, name);
            }

            const byDate = new Map<string, Record<string, any>>();
            for (const v of finRes.values ?? []) {
                const date = v.recorded_at?.split('T')[0];
                if (!date) continue;
                if (!byDate.has(date)) byDate.set(date, {});
                const propName = reversePid.get(v.pid);
                if (propName) byDate.get(date)![propName] = Number(v.value);
            }

            for (const [date, m] of byDate) {
                await sql`
          INSERT INTO financials
            (company_ticker, filing_date, total_revenue, net_income,
             total_assets, total_liabilities, shareholders_equity, shares_outstanding)
          VALUES (${co.ticker}, ${date},
            ${m.total_revenue ?? null}, ${m.net_income ?? null},
            ${m.total_assets ?? null}, ${m.total_liabilities ?? null},
            ${m.shareholders_equity ?? null}, ${m.shares_outstanding ?? null})
          ON CONFLICT (company_ticker, filing_date) DO UPDATE SET
            total_revenue = COALESCE(EXCLUDED.total_revenue, financials.total_revenue),
            net_income = COALESCE(EXCLUDED.net_income, financials.net_income),
            total_assets = COALESCE(EXCLUDED.total_assets, financials.total_assets),
            total_liabilities = COALESCE(EXCLUDED.total_liabilities, financials.total_liabilities),
            shareholders_equity = COALESCE(EXCLUDED.shareholders_equity, financials.shareholders_equity),
            shares_outstanding = COALESCE(EXCLUDED.shares_outstanding, financials.shares_outstanding),
            synced_at = NOW()
        `;
            }

            // Filings via the "filed" relationship
            const filedPid = pidMap.get('filed');
            let filingCount = 0;
            if (filedPid) {
                const filedRes = await getPropertyValues([neid], [filedPid]);
                const docNeids = (filedRes.values ?? [])
                    .map((v: any) => String(v.value).padStart(20, '0'))
                    .slice(0, 30);

                if (docNeids.length > 0) {
                    const formTypePid = pidMap.get('form_type')!;
                    const filingDatePid = pidMap.get('filing_date')!;
                    const accPid = pidMap.get('accession_number')!;
                    const namePid = pidMap.get('name')!;
                    const batchPids = [formTypePid, filingDatePid, accPid, namePid].filter(Boolean);
                    const propsRes = await getPropertyValues(docNeids, batchPids);

                    const filingData = new Map<string, Record<string, string>>();
                    for (const nid of docNeids) filingData.set(nid, { neid: nid });
                    for (const v of propsRes.values ?? []) {
                        const eid = String(v.eid).padStart(20, '0');
                        const record = filingData.get(eid);
                        if (!record) continue;
                        if (v.pid === formTypePid) record.form_type = String(v.value);
                        if (v.pid === filingDatePid) record.filing_date = String(v.value);
                        if (v.pid === accPid) record.accession_number = String(v.value);
                        if (v.pid === namePid && !record.name) record.name = String(v.value);
                    }

                    for (const [docNeid, f] of filingData) {
                        await sql`
              INSERT INTO filings
                (company_ticker, accession_number, form_type, filing_date, name, neid)
              VALUES (${co.ticker}, ${f.accession_number ?? null},
                ${f.form_type ?? null}, ${f.filing_date ?? null},
                ${f.name ?? null}, ${docNeid})
              ON CONFLICT (company_ticker, neid) DO UPDATE SET
                form_type = COALESCE(EXCLUDED.form_type, filings.form_type),
                filing_date = COALESCE(EXCLUDED.filing_date, filings.filing_date),
                accession_number = COALESCE(EXCLUDED.accession_number, filings.accession_number),
                name = COALESCE(EXCLUDED.name, filings.name)
            `;
                        filingCount++;
                    }
                }
            }

            results.push({
                ticker: co.ticker,
                neid,
                financialPeriods: byDate.size,
                filings: filingCount,
            });
        } catch (err: any) {
            results.push({ ticker: co.ticker, error: err.message });
        }
    }

    return { ok: true, results };
});
