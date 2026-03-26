interface GatewayConfig {
    gatewayUrl: string;
    orgId: string;
    apiKey: string;
}

function getConfig(): GatewayConfig {
    const pub = useRuntimeConfig().public as any;
    return {
        gatewayUrl: pub.gatewayUrl || '',
        orgId: pub.tenantOrgId || '',
        apiKey: pub.qsApiKey || '',
    };
}

function qsUrl(endpoint: string): string {
    const { gatewayUrl, orgId } = getConfig();
    return `${gatewayUrl}/api/qs/${orgId}${endpoint}`;
}

function apiHeaders(contentType?: string): Record<string, string> {
    const h: Record<string, string> = { 'X-Api-Key': getConfig().apiKey };
    if (contentType) h['Content-Type'] = contentType;
    return h;
}

export async function searchEntities(name: string, maxResults = 5) {
    const resp = await fetch(qsUrl('/entities/search'), {
        method: 'POST',
        headers: apiHeaders('application/json'),
        body: JSON.stringify({ queries: [{ queryId: 1, query: name }], maxResults }),
    });
    if (!resp.ok) throw new Error(`Entity search failed: ${resp.status}`);
    return resp.json();
}

let _schema: any = null;

export async function getSchema() {
    if (_schema) return _schema;
    const resp = await fetch(qsUrl('/elemental/metadata/schema'), { headers: apiHeaders() });
    if (!resp.ok) throw new Error(`Schema fetch failed: ${resp.status}`);
    _schema = await resp.json();
    return _schema;
}

export async function getPidMap(): Promise<Map<string, number>> {
    const schema = await getSchema();
    const props = schema.schema?.properties ?? schema.properties ?? [];
    return new Map(props.map((p: any) => [p.name, p.pid]));
}

export async function getPropertyValues(eids: string[], pids: number[], includeAttributes = false) {
    const params = new URLSearchParams();
    params.set('eids', JSON.stringify(eids));
    params.set('pids', JSON.stringify(pids));
    if (includeAttributes) params.set('include_attributes', 'true');
    const resp = await fetch(qsUrl('/elemental/entities/properties'), {
        method: 'POST',
        headers: apiHeaders('application/x-www-form-urlencoded'),
        body: params.toString(),
    });
    if (!resp.ok) throw new Error(`Property values fetch failed: ${resp.status}`);
    return resp.json();
}

export async function getEntityReport(neid: string) {
    const resp = await fetch(qsUrl(`/entities/${neid}/report`), { headers: apiHeaders() });
    if (!resp.ok) throw new Error(`Entity report failed: ${resp.status}`);
    const data = await resp.json();
    return data.report ?? data;
}
