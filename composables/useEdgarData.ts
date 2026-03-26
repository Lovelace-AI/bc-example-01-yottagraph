export interface Company {
    ticker: string;
    name: string;
    neid: string | null;
    cik: string | null;
    last_sync_at: string | null;
    filing_count: number;
    latest_financials: {
        total_revenue: number | null;
        net_income: number | null;
        total_assets: number | null;
        total_liabilities: number | null;
        shareholders_equity: number | null;
        shares_outstanding: number | null;
        filing_date: string | null;
    } | null;
}

export interface Filing {
    id: number;
    company_ticker: string;
    accession_number: string | null;
    form_type: string | null;
    filing_date: string | null;
    name: string | null;
    neid: string | null;
}

export interface FinancialRecord {
    id: number;
    company_ticker: string;
    filing_date: string;
    total_revenue: number | null;
    net_income: number | null;
    total_assets: number | null;
    total_liabilities: number | null;
    shareholders_equity: number | null;
    shares_outstanding: number | null;
    synced_at: string;
}

export function formatLargeNumber(value: number | null | undefined): string {
    if (value == null) return '—';
    const abs = Math.abs(value);
    const sign = value < 0 ? '-' : '';
    if (abs >= 1e12) return `${sign}$${(abs / 1e12).toFixed(1)}T`;
    if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(1)}B`;
    if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(1)}M`;
    if (abs >= 1e3) return `${sign}$${(abs / 1e3).toFixed(0)}K`;
    return `${sign}$${abs}`;
}

export function useEdgarData() {
    const companies = ref<Company[]>([]);
    const dbConfigured = ref(true);
    const loading = ref(false);
    const syncing = ref(false);
    const error = ref<string | null>(null);

    async function fetchCompanies() {
        loading.value = true;
        error.value = null;
        try {
            const res = await $fetch<{ configured: boolean; companies: Company[] }>(
                '/api/edgar/companies'
            );
            dbConfigured.value = res.configured;
            companies.value = res.companies;
        } catch (e: any) {
            error.value = e.data?.statusMessage || e.message || 'Failed to load';
        } finally {
            loading.value = false;
        }
    }

    async function fetchFilings(ticker: string): Promise<Filing[]> {
        const res = await $fetch<{ configured: boolean; filings: Filing[] }>('/api/edgar/filings', {
            params: { ticker },
        });
        return res.filings;
    }

    async function fetchFinancials(ticker: string): Promise<FinancialRecord[]> {
        const res = await $fetch<{ configured: boolean; financials: FinancialRecord[] }>(
            '/api/edgar/financials',
            { params: { ticker } }
        );
        return res.financials;
    }

    async function sync() {
        syncing.value = true;
        error.value = null;
        try {
            await $fetch('/api/edgar/sync', { method: 'POST' });
            await fetchCompanies();
        } catch (e: any) {
            error.value = e.data?.statusMessage || e.message || 'Sync failed';
        } finally {
            syncing.value = false;
        }
    }

    return {
        companies: readonly(companies),
        dbConfigured: readonly(dbConfigured),
        loading: readonly(loading),
        syncing: readonly(syncing),
        error,
        fetchCompanies,
        fetchFilings,
        fetchFinancials,
        sync,
    };
}
