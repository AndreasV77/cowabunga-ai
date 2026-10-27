import { useEffect, useState } from 'react';
import { api } from '../api';
import type { Item, LibraryHit, LibraryPage } from '../types';

export function useLibrary() {
  const [query, setQuery] = useState('');
  const [scope, setScope] = useState<'all' | 'v6_core'>('all');
  const [kind, setKind] = useState('');
  const [page, setPage] = useState<LibraryPage | null>(null);
  const [inspected, setInspected] = useState<LibraryHit | null>(null);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const changed = !!page && (query.trim() !== page.query || scope !== page.scope || (kind || null) !== page.kind);

  useEffect(() => {
    const close = (event: KeyboardEvent) => { if (event.key === 'Escape') setInspectorOpen(false); };
    window.addEventListener('keydown', close);
    return () => window.removeEventListener('keydown', close);
  }, []);

  async function search(limit = 20) {
    if (busy) return;
    setBusy(true); setError(''); setNotice('');
    const params = new URLSearchParams({ q: query.trim(), scope, limit: String(limit) });
    if (kind) params.set('kind', kind);
    try {
      const result = await api<LibraryPage>(`/api/library?${params}`);
      setPage(result);
      setInspected(current => result.items.find(hit => current?.snapshot_id === hit.snapshot_id && current.record.id === hit.record.id) ?? null);
      setInspectorOpen(false);
    }
    catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function exportRecord(hit: LibraryHit) {
    if (exporting) return;
    setExporting(true); setError(''); setNotice('');
    try {
      const bundle = await api<unknown>('/api/library/export', { snapshot_id: hit.snapshot_id, record_id: hit.record.id });
      const url = URL.createObjectURL(new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' }));
      const link = document.createElement('a'); link.href = url; link.download = 'reference-record.json'; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice('Reference exported with its source, license and evidence metadata.');
    } catch (err) { setError((err as Error).message); }
    finally { setExporting(false); }
  }

  const inspectedItem: Item | undefined = inspected ? { snapshot_id: inspected.snapshot_id, v6_core: inspected.v6_core, uses: [], record: inspected.record } : undefined;
  return { query, setQuery, scope, setScope, kind, setKind, page, changed, busy, exporting, error, notice, search, exportRecord,
    inspectedItem, inspectedSource: inspected?.source, inspectorOpen,
    inspect: (hit: LibraryHit) => { setInspected(hit); setInspectorOpen(true); },
    closeInspector: () => setInspectorOpen(false) };
}
