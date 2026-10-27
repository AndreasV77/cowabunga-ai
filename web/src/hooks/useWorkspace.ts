import { useEffect, useRef, useState } from 'react';
import { api } from '../api';
import type { BuildRequest, Defaults, Draft, DraftSummary, DraftReferencePack, LibraryHit, Packet } from '../types';
import type { useWorkbench } from './useWorkbench';

const emptyForm = (defaults: Defaults): BuildRequest => ({ concept_ids: [], intent: '', target_model: defaults.target_model, supplementary: defaults.supplementary, limit: 24 });
const initialDefaults: Defaults = { revision: 0, target_model: 'v6', supplementary: false, prompt_language: 'en' };

export function useWorkspace(workbench: ReturnType<typeof useWorkbench>) {
  const [drafts, setDrafts] = useState<DraftSummary[]>([]);
  const [defaults, setDefaults] = useState(initialDefaults);
  const [active, setActive] = useState<Draft | null>(null);
  const [title, setTitle] = useState('');
  const [references, setReferences] = useState<LibraryHit[]>([]);
  const [activeSnapshots, setActiveSnapshots] = useState<Record<string, string> | null>(null);
  const [exporting, setExporting] = useState(false);
  const [chosen, setChosen] = useState('');
  const [baseline, setBaseline] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const selectedIds = workbench.packet && !workbench.dirty ? [...workbench.included].sort() : null;
  const payload = { title: title.trim(), form: workbench.request, selected_ids: selectedIds,
    catalog_sha256: selectedIds ? workbench.packet!.catalog_sha256 : null,
    library_records: references.map(hit => ({ snapshot_id: hit.snapshot_id, record_id: hit.record.id })) };
  const signature = JSON.stringify(payload);
  const currentSignature = useRef(signature);
  currentSignature.current = signature;
  const unsaved = baseline === null
    ? !!(title || references.length || workbench.intent || workbench.selected.length || workbench.packet || workbench.model !== defaults.target_model || workbench.supplementary !== defaults.supplementary)
    : signature !== baseline;
  const { initializeDefaults, restore } = workbench;

  useEffect(() => {
    let live = true;
    Promise.all([api<Defaults>('/api/preferences'), api<DraftSummary[]>('/api/drafts'), api<Record<string, string>>('/api/library/active-snapshots')]).then(([settings, list, snapshots]) => {
      if (live) { setDefaults(settings); setDrafts(list); setActiveSnapshots(snapshots); initializeDefaults(settings); setReady(true); }
    }).catch(err => { if (live) setError(err.message); });
    return () => { live = false; };
  }, [initializeDefaults]);

  useEffect(() => {
    const protect = (event: BeforeUnloadEvent) => { if (unsaved) { event.preventDefault(); event.returnValue = ''; } };
    window.addEventListener('beforeunload', protect);
    return () => window.removeEventListener('beforeunload', protect);
  }, [unsaved]);

  async function save(asNew = false) {
    if (!title.trim() || busy || !ready || workbench.busy) return;
    setBusy(true); setError(''); setNotice('');
    const submitted = signature;
    try {
      const document = await api<Draft>(active && !asNew ? `/api/drafts/${active.id}` : '/api/drafts',
        { ...payload, revision: active && !asNew ? active.revision : 0, copy_from: asNew && active ? { draft_id: active.id, revision: active.revision } : null }, active && !asNew ? 'PUT' : 'POST');
      setActive(document); setChosen(document.id); setBaseline(submitted);
      setDrafts(list => [document, ...list.filter(item => item.id !== document.id)]);
      setNotice(`Draft saved locally with ${document.selection?.library?.items.length ?? 0} pinned library references${document.selection?.packet ? ' and its concept selection' : ''}.`);
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function open() {
    if (!chosen || busy || (unsaved && !window.confirm('Discard unsaved changes and open this draft?'))) return;
    setBusy(true); setError(''); setNotice('');
    const started = currentSignature.current;
    try {
      const [document, snapshots] = await Promise.all([api<Draft>(`/api/drafts/${chosen}`), api<Record<string, string>>('/api/library/active-snapshots')]);
      let result: { packet: Packet | null; selected_ids: string[] } = { packet: null, selected_ids: [] };
      let warning = '';
      try { result = await api(`/api/drafts/${chosen}/restore-context`, {}); }
      catch (err) { warning = `Direction restored. Saved references could not be restored: ${(err as Error).message}`; }
      if (started !== currentSignature.current) throw new Error('Your direction changed while loading. Open the draft again when ready.');
      restore(document.form, result.packet, result.selected_ids);
      setActive(document); setTitle(document.title); setChosen(document.id);
      const restoredReferences = document.selection?.library?.items ?? [];
      setReferences(restoredReferences); setActiveSnapshots(snapshots);
      const inactiveCount = restoredReferences.filter(hit => !Object.values(snapshots).includes(hit.snapshot_id)).length;
      if (inactiveCount) warning += `${warning ? ' ' : ''}${inactiveCount} library references retain historical source versions. Remove and re-add from search only if you want a newer version.`;
      setBaseline(JSON.stringify({ title: document.title, form: document.form,
        selected_ids: result.packet ? [...result.selected_ids].sort() : null,
        catalog_sha256: result.packet?.catalog_sha256 ?? null,
        library_records: restoredReferences.map(hit => ({ snapshot_id: hit.snapshot_id, record_id: hit.record.id })) }));
      setNotice(warning || `Opened “${document.title}”.`);
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  function newDraft() {
    if (unsaved && !window.confirm('Discard unsaved changes and start a new draft?')) return;
    restore(emptyForm(defaults)); setTitle(''); setActive(null); setChosen(''); setReferences([]);
    setBaseline(JSON.stringify({ title: '', form: emptyForm(defaults), selected_ids: null, catalog_sha256: null, library_records: [] }));
    setError(''); setNotice('New draft started with your saved defaults.');
  }

  async function saveDefaults() {
    setBusy(true); setError(''); setNotice('');
    try {
      const saved = await api<Defaults>('/api/preferences', { revision: defaults.revision,
        target_model: workbench.model, supplementary: workbench.supplementary }, 'PUT');
      setDefaults(saved); setNotice('Model and source scope saved as defaults for new drafts.');
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  function toggleReference(hit: LibraryHit) {
    const matches = (value: LibraryHit) => value.snapshot_id === hit.snapshot_id && value.record.id === hit.record.id;
    if (!references.some(matches) && references.length >= 50) { setError('Keep at most 50 library references per draft.'); return; }
    if (!references.some(matches)) setActiveSnapshots(current => ({ ...current, [hit.source.id]: hit.snapshot_id }));
    setReferences(current => current.some(matches) ? current.filter(value => !matches(value)) : [...current, hit]);
    setNotice('');
  }

  async function exportReferences() {
    if (!active || unsaved || exporting || busy) return;
    setExporting(true); setError(''); setNotice('');
    try {
      const pack = await api<DraftReferencePack>(`/api/drafts/${active.id}/reference-pack?revision=${active.revision}`);
      const url = URL.createObjectURL(new Blob([JSON.stringify(pack, null, 2)], { type: 'application/json' }));
      const link = document.createElement('a'); link.href = url; link.download = 'draft-references.json'; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice(`Saved reference pack exported${pack.inactive_library_records.length || pack.inactive_context_snapshots.length ? ' with historical sources explicitly marked' : ''}.`);
    } catch (err) { setError((err as Error).message); }
    finally { setExporting(false); }
  }

  const inactiveReferences = references.filter(hit => activeSnapshots !== null && !Object.values(activeSnapshots).includes(hit.snapshot_id));
  const canExportReferences = !!active && !unsaved && !busy && !exporting && (references.length > 0 || !!active.selection?.selected_ids?.length);

  return { references, inactiveReferences, toggleReference, exportReferences, canExportReferences,
    drafts, defaults, active, title, setTitle, chosen, setChosen, busy, ready, error, notice, unsaved,
    save, open, newDraft, saveDefaults };
}
