<template>
    <div class="d-flex flex-column fill-height">
        <div class="flex-shrink-0 pa-4 pb-0">
            <div class="d-flex align-center justify-space-between mb-4">
                <div>
                    <h1 class="text-h5" style="font-family: var(--font-headline); font-weight: 400">
                        EDGAR Tracker
                    </h1>
                    <p class="text-body-2 mt-1" style="color: var(--lv-silver)">
                        Apple &amp; Tesla financial data from SEC filings
                    </p>
                </div>
                <div class="d-flex align-center ga-3">
                    <span v-if="lastSyncTime" class="text-caption" style="color: var(--lv-silver)">
                        Last sync: {{ lastSyncTime }}
                    </span>
                    <v-btn
                        color="primary"
                        prepend-icon="mdi-sync"
                        :loading="syncing"
                        :disabled="!dbConfigured"
                        @click="edgar.sync()"
                    >
                        Sync Now
                    </v-btn>
                </div>
            </div>
        </div>

        <div class="flex-grow-1 overflow-y-auto pa-4 pt-2">
            <v-alert
                v-if="!dbConfigured"
                type="info"
                variant="tonal"
                class="mb-4"
                icon="mdi-database-off"
            >
                <div class="font-weight-medium">Database not connected</div>
                <div class="text-body-2 mt-1">
                    Push to <code>main</code> to deploy — Postgres credentials are injected
                    automatically by Vercel. Locally, the dashboard shows sample layout only.
                </div>
            </v-alert>

            <v-alert v-if="edgar.error.value" type="error" variant="tonal" class="mb-4" closable>
                {{ edgar.error.value }}
            </v-alert>

            <v-progress-circular v-if="loading" indeterminate class="d-block mx-auto my-8" />

            <v-row v-else>
                <v-col v-for="co in companies" :key="co.ticker" cols="12" md="6">
                    <v-card class="fill-height" :to="`/company/${co.ticker}`">
                        <v-card-title class="d-flex align-center ga-3 pb-1">
                            <v-icon :color="co.ticker === 'AAPL' ? '#a3aaae' : '#e31937'" size="28">
                                {{ co.ticker === 'AAPL' ? 'mdi-apple' : 'mdi-car-electric' }}
                            </v-icon>
                            <span>{{ co.name }}</span>
                            <v-chip color="primary">{{ co.ticker }}</v-chip>
                        </v-card-title>

                        <v-card-text>
                            <div v-if="co.latest_financials" class="metrics-grid">
                                <div class="metric-item">
                                    <div class="metric-label">Revenue</div>
                                    <div class="metric-value">
                                        {{ fmt(co.latest_financials.total_revenue) }}
                                    </div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-label">Net Income</div>
                                    <div class="metric-value">
                                        {{ fmt(co.latest_financials.net_income) }}
                                    </div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-label">Total Assets</div>
                                    <div class="metric-value">
                                        {{ fmt(co.latest_financials.total_assets) }}
                                    </div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-label">Liabilities</div>
                                    <div class="metric-value">
                                        {{ fmt(co.latest_financials.total_liabilities) }}
                                    </div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-label">Equity</div>
                                    <div class="metric-value">
                                        {{ fmt(co.latest_financials.shareholders_equity) }}
                                    </div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-label">Shares Out</div>
                                    <div class="metric-value">
                                        {{ fmtShares(co.latest_financials.shares_outstanding) }}
                                    </div>
                                </div>
                            </div>

                            <v-empty-state
                                v-else
                                headline="No data yet"
                                text="Run a sync to fetch EDGAR data"
                                icon="mdi-database-sync"
                                density="compact"
                                class="my-2"
                            />

                            <v-divider class="my-3" />

                            <div class="d-flex align-center justify-space-between">
                                <span class="text-caption" style="color: var(--lv-silver)">
                                    {{ co.filing_count }} filings
                                </span>
                                <span
                                    v-if="co.latest_financials?.filing_date"
                                    class="text-caption"
                                    style="color: var(--lv-silver)"
                                >
                                    Latest: {{ co.latest_financials.filing_date }}
                                </span>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>

                <v-col v-if="dbConfigured && !companies.length && !loading" cols="12">
                    <v-empty-state
                        headline="No companies tracked yet"
                        text="Click Sync Now to fetch EDGAR data for Apple and Tesla"
                        icon="mdi-file-document-outline"
                    />
                </v-col>
            </v-row>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { useEdgarData, formatLargeNumber } from '~/composables/useEdgarData';

    const edgar = useEdgarData();
    const { companies, dbConfigured, loading, syncing } = edgar;

    const fmt = formatLargeNumber;

    function fmtShares(value: number | null | undefined): string {
        if (value == null) return '—';
        const abs = Math.abs(value);
        if (abs >= 1e9) return `${(abs / 1e9).toFixed(1)}B`;
        if (abs >= 1e6) return `${(abs / 1e6).toFixed(0)}M`;
        return String(value);
    }

    const lastSyncTime = computed(() => {
        const times = companies.value
            .map((c) => c.last_sync_at)
            .filter(Boolean)
            .map((t) => new Date(t!).getTime());
        if (!times.length) return null;
        return new Date(Math.max(...times)).toLocaleString();
    });

    onMounted(() => edgar.fetchCompanies());
</script>

<style scoped>
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }

    .metric-item {
        text-align: center;
    }

    .metric-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--lv-silver);
        margin-bottom: 2px;
    }

    .metric-value {
        font-family: var(--font-mono);
        font-size: 0.95rem;
        font-weight: 500;
    }
</style>
