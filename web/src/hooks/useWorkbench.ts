import { useCallback, useEffect, useRef, useState } from 'react';
import type { BuildRequest, Concept, Defaults, Meta, Packet } from '../types';
import { api, fetchContextExport } from '../api';

export function useWorkbench() {
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState<string[]>([]);
  const [intent, setIntent] = useState('');
  const [model, setModel] = useState('v6');
  const [supplementary, setSupplementary] = useState(false);
  const [packet, setPacket] = useState<Packet | null>(null);
  const [built, setBuilt] = useState<BuildRequest | null>(null);
  const [included, setIncluded] = useState<Set<string>>(new Set());
  const [inspected, setInspected] = useState<string | null>(null);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const pending = useRef(0);
  const pristine = useRef(true);
  const [limit, setLimit] = useState(24);
  const request: BuildRequest = { concept_ids: selected, intent, target_model: model, supplementary, limit };
  const dirty = !!built && JSON.stringify(request) !== JSON.stringify(built);
  const filtered = concepts.filter(c => query.toLowerCase().split(/\s+/).every(word => `${c.label} ${c.description} ${c.aliases.join(' ')}`.toLowerCase().includes(word)));
  const inspectedItem = packet?.items.find(item => item.record.id === inspected);
  const inspectedSource = inspectedItem && packet?.sources[inspectedItem.snapshot_id];

  useEffect(() => {
    let live = true;
    Promise.all([api<Concept[]>('/api/concepts'), api<Meta>('/api/meta')]).then(([list, info]) => {
      if (live) { setConcepts(list); setMeta(info); }
    }).catch(err => live && setError(err.message));
    return () => { live = false; };
  }, []);

  useEffect(() => {
    const close = (event: KeyboardEvent) => { if (event.key === 'Escape') setInspectorOpen(false); };
    window.addEventListener('keydown', close);
    return () => window.removeEventListener('keydown', close);
  }, []);

  function toggleConcept(id: string) {
    pristine.current = false;
    setSelected(list => list.includes(id) ? list.filter(value => value !== id) : [...list, id]);
    setNotice('');
  }

  async function assemble() {
    const serial = ++pending.current;
    setBusy(true); setError(''); setNotice('');
    const submitted = { ...request, concept_ids: [...request.concept_ids] };
    try {
      const result = await api<Packet>('/api/context', submitted);
      if (serial !== pending.current) return;
      setPacket(result); setBuilt(submitted);
      setIncluded(new Set(result.items.filter(item => item.uses.some(use => use.relation === 'wording') && !('style_prompt' in item.record)).map(item => item.record.id)));
      setInspected(result.items[0]?.record.id || null);
      setInspectorOpen(false);
      setNotice(`${result.items.length} candidates assembled. Choose the wording you want to keep.`);
    } catch (err) { setError((err as Error).message); }
    finally { if (serial === pending.current) setBusy(false); }
  }

  async function exportPacket(format: 'json' | 'markdown', copy = false) {
    if (!built || dirty || !included.size) return;
    setExporting(true); setError(''); setNotice('');
    try {
      const text = await fetchContextExport(built, [...included], format);
      if (copy) {
        await navigator.clipboard.writeText(text);
        setNotice('Context copied with its sources and evidence notes.');
      } else {
        const blob = new Blob([text], { type: format === 'json' ? 'application/json' : 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a'); link.href = url; link.download = `prompt-context.${format === 'json' ? 'json' : 'md'}`;
        link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
        setNotice('Context exported with its sources and evidence notes.');
      }
    } catch (err) { setError((err as Error).message); }
    finally { setExporting(false); }
  }

  const canExport = !!packet && !dirty && included.size > 0 && !exporting && !busy;
  function toggleCandidate(id: string) {
    setIncluded(current => {
      const next = new Set(current);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  function inspectCandidate(id: string) {
    setInspected(id);
    setInspectorOpen(true);
  }

  const initializeDefaults = useCallback((defaults: Defaults) => {
    if (pristine.current) { setModel(defaults.target_model); setSupplementary(defaults.supplementary); }
  }, []);

  const restore = useCallback((form: BuildRequest, restored: Packet | null = null, ids: string[] = []) => {
    pristine.current = false;
    ++pending.current; setBusy(false);
    setSelected(form.concept_ids); setIntent(form.intent); setModel(form.target_model);
    setSupplementary(form.supplementary); setLimit(form.limit);
    setPacket(restored); setBuilt(restored ? form : null); setIncluded(new Set(ids));
    setInspected(restored?.items[0]?.record.id || null); setInspectorOpen(false);
    setError(''); setNotice('');
  }, []);

  return {
    request, initializeDefaults, restore,
    concepts, meta, query, setQuery, selected, intent, setIntent: (value: string) => { pristine.current = false; setIntent(value); },
    model, setModel: (value: string) => { pristine.current = false; setModel(value); },
    supplementary, setSupplementary: (value: boolean) => { pristine.current = false; setSupplementary(value); }, packet, included, inspected, inspectorOpen,
    inspectedItem, inspectedSource, filtered, busy, error, notice, dirty, canExport,
    toggleConcept, toggleCandidate, inspectCandidate, assemble, exportPacket,
    clearSelection: () => { pristine.current = false; setSelected([]); },
    closeInspector: () => setInspectorOpen(false),
  };
}
