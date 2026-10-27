import type { BuildRequest } from './types';

export async function api<T>(url: string, body?: unknown, method: 'POST' | 'PUT' = 'POST'): Promise<T> {
  const response = await fetch(url, body === undefined ? {} : { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(typeof payload.detail === 'string' ? payload.detail : 'This selection could not be loaded. Check the local server and try again.');
  }
  return response.json();
}

export async function fetchContextExport(request: BuildRequest, selectedIds: string[], format: 'json' | 'markdown'): Promise<string> {
  const response = await fetch('/api/export', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...request, selected_ids: selectedIds, format }),
  });
  if (!response.ok) {
    const payload = await response.json();
    throw new Error(typeof payload.detail === 'string' ? payload.detail : 'Export failed. Rebuild the selection and try again.');
  }
  return response.text();
}
