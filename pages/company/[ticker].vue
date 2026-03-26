<template>
    <div class="d-flex flex-column fill-height">
        <div class="flex-shrink-0 pa-4 pb-0">
            <div class="d-flex align-center ga-3 mb-1">
                <v-btn icon variant="text" size="small" to="/">
                    <v-icon>mdi-arrow-left</v-icon>
                </v-btn>
                <v-icon :color="ticker === 'AAPL' ? '#a3aaae' : '#e31937'" size="28">
                    {{ ticker === 'AAPL' ? 'mdi-apple' : 'mdi-car-electric' }}
                </v-icon>
                <h1 class="text-h5" style="font-family: var(--font-headline); font-weight: 400">
                    {{ companyName }}
                </h1>
                <v-chip color="primary">{{ ticker }}</v-chip>
            </div>
        </div>

        <div class="flex-grow-1 overflow-y-auto pa-4 pt-2">
            <v-progress-circular v-if="loading" indeterminate class="d-block mx-auto my-8" />

            <template v-else>
                <v-tabs v-model="tab" class="mb-4">
                    <v-tab value="financials">Financials</v-tab>
                    <v-tab value="filings">Filings</v-tab>
                    <v-tab value="chart">Trend Chart</v-tab>
                </v-tabs>

                <v-window v-model="tab">
                    <v-window-item value="financials">
                        <v-data-table
                            :headers="finHeaders"
                            :items="financials"
                            density="comfortable"
                            hover
                            items-per-page="25"
                        >
                            <template v-slot:item.filing_date="{ value }">
                                {{ value?.split('T')[0] ?? '—' }}
                            </template>
                            <template v-slot:item.total_revenue="{ value }">
                                {{ fmt(value) }}
                            </template>
                            <template v-slot:item.net_income="{ value }">
                                {{ fmt(value) }}
                            </template>
                            <template v-slot:item.total_assets="{ value }">
                                {{ fmt(value) }}
                            </template>
                            <template v-slot:item.total_liabilities="{ value }">
                                {{ fmt(value) }}
                            </template>
                            <template v-slot:item.shareholders_equity="{ value }">
                                {{ fmt(value) }}
                            </template>
                            <template v-slot:item.shares_outstanding="{ value }">
                                {{ fmtShares(value) }}
                            </template>
                            <template v-slot:no-data>
                                <v-empty-state
                                    headline="No financial data"
                                    text="Run a sync from the dashboard"
                                    icon="mdi-chart-line"
                                    density="compact"
                                />
                            </template>
                        </v-data-table>
                    </v-window-item>

                    <v-window-item value="filings">
                        <v-data-table
                            :headers="filingHeaders"
                            :items="filings"
                            density="comfortable"
                            hover
                            items-per-page="25"
                        >
                            <template v-slot:item.filing_date="{ value }">
                                {{ value?.split('T')[0] ?? '—' }}
                            </template>
                            <template v-slot:no-data>
                                <v-empty-state
                                    headline="No filings"
                                    text="Run a sync from the dashboard"
                                    icon="mdi-file-document-outline"
                                    density="compact"
                                />
                            </template>
                        </v-data-table>
                    </v-window-item>

                    <v-window-item value="chart">
                        <v-card class="pa-4" style="min-height: 400px">
                            <canvas ref="chartCanvas" />
                            <v-empty-state
                                v-if="!financials.length"
                                headline="No data for chart"
                                text="Sync data first to see trends"
                                icon="mdi-chart-line"
                            />
                        </v-card>
                    </v-window-item>
                </v-window>
            </template>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { Chart, registerables } from 'chart.js';
    import {
        useEdgarData,
        formatLargeNumber,
        type Filing,
        type FinancialRecord,
    } from '~/composables/useEdgarData';

    Chart.register(...registerables);

    const route = useRoute();
    const ticker = computed(() => String(route.params.ticker).toUpperCase());
    const tab = ref('financials');

    const edgar = useEdgarData();
    const loading = ref(true);
    const financials = ref<FinancialRecord[]>([]);
    const filings = ref<Filing[]>([]);
    const chartCanvas = ref<HTMLCanvasElement | null>(null);
    let chart: Chart | null = null;

    const companyName = computed(() => {
        const co = edgar.companies.value.find((c) => c.ticker === ticker.value);
        return co?.name ?? ticker.value;
    });

    const fmt = formatLargeNumber;
    function fmtShares(value: number | null | undefined): string {
        if (value == null) return '—';
        const abs = Math.abs(value);
        if (abs >= 1e9) return `${(abs / 1e9).toFixed(1)}B`;
        if (abs >= 1e6) return `${(abs / 1e6).toFixed(0)}M`;
        return String(value);
    }

    const finHeaders = [
        { title: 'Date', key: 'filing_date', sortable: true },
        { title: 'Revenue', key: 'total_revenue', sortable: true },
        { title: 'Net Income', key: 'net_income', sortable: true },
        { title: 'Assets', key: 'total_assets', sortable: true },
        { title: 'Liabilities', key: 'total_liabilities', sortable: true },
        { title: 'Equity', key: 'shareholders_equity', sortable: true },
        { title: 'Shares', key: 'shares_outstanding', sortable: true },
    ];

    const filingHeaders = [
        { title: 'Form', key: 'form_type', sortable: true },
        { title: 'Date', key: 'filing_date', sortable: true },
        { title: 'Name', key: 'name', sortable: true },
        { title: 'Accession #', key: 'accession_number', sortable: false },
    ];

    function renderChart() {
        if (!chartCanvas.value || !financials.value.length) return;
        chart?.destroy();

        const sorted = [...financials.value].sort(
            (a, b) => new Date(a.filing_date).getTime() - new Date(b.filing_date).getTime()
        );
        const labels = sorted.map((f) => f.filing_date.split('T')[0]);

        chart = new Chart(chartCanvas.value, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Revenue',
                        data: sorted.map((f) => f.total_revenue),
                        borderColor: '#3fea00',
                        backgroundColor: 'rgba(63, 234, 0, 0.08)',
                        fill: true,
                        tension: 0.3,
                    },
                    {
                        label: 'Net Income',
                        data: sorted.map((f) => f.net_income),
                        borderColor: '#003bff',
                        backgroundColor: 'rgba(0, 59, 255, 0.08)',
                        fill: true,
                        tension: 0.3,
                    },
                    {
                        label: 'Total Assets',
                        data: sorted.map((f) => f.total_assets),
                        borderColor: '#ff5c00',
                        backgroundColor: 'rgba(255, 92, 0, 0.08)',
                        fill: false,
                        tension: 0.3,
                        borderDash: [5, 5],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                scales: {
                    x: {
                        ticks: { color: '#757575', maxTicksLimit: 12 },
                        grid: { color: '#1c1c1c' },
                    },
                    y: {
                        ticks: {
                            color: '#757575',
                            callback: (v) => formatLargeNumber(v as number),
                        },
                        grid: { color: '#1c1c1c' },
                    },
                },
                plugins: {
                    legend: { labels: { color: '#e5e5e5' } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) =>
                                `${ctx.dataset.label}: ${formatLargeNumber(ctx.raw as number)}`,
                        },
                    },
                },
            },
        });
    }

    watch(tab, (t) => {
        if (t === 'chart') nextTick(renderChart);
    });

    onMounted(async () => {
        try {
            await edgar.fetchCompanies();
            const [fin, fil] = await Promise.all([
                edgar.fetchFinancials(ticker.value),
                edgar.fetchFilings(ticker.value),
            ]);
            financials.value = fin;
            filings.value = fil;
        } catch {
            // handled by empty states
        } finally {
            loading.value = false;
        }
    });

    onUnmounted(() => chart?.destroy());
</script>
