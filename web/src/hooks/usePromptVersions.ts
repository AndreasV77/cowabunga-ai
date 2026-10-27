import { useEffect, useState } from 'react';
import { api } from '../api';
import type { Draft, PromptText, PromptVersion, PromptVersionPage, PromptVersionSummary } from '../types';

const emptyText = (): PromptText => ({ schema_version: '1.0', language: 'en', style_prompt: '', lyrics: '' });
const signature = (content: PromptText, note: string, draft: Draft, basedOn: string | null) => JSON.stringify({ content, note, draft_revision: draft.revision, based_on_id: basedOn });
const summary = (value: PromptVersion): PromptVersionSummary => ({ id: value.id, version: value.version, created_at: value.created_at, note: value.note, style_sha256: value.style_sha256, lyrics_sha256: value.lyrics_sha256, draft_revision: value.draft_snapshot.revision });

export function usePromptVersions() {
  const [draft, setDraft] = useState<Draft | null>(null);
  const [latestDraftRevision, setLatestDraftRevision] = useState(0);
  const [headId, setHeadId] = useState<string | null>(null);
  const [viewed, setViewed] = useState<PromptVersion | null>(null);
  const [basedOn, setBasedOn] = useState<string | null>(null);
  const [content, setContent] = useState<PromptText>(emptyText);
  const [note, setNote] = useState('');
  const [items, setItems] = useState<PromptVersionSummary[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [baseline, setBaseline] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const dirty = !!draft && baseline !== null && signature(content, note, draft, basedOn) !== baseline;
  const contextOutdated = !!draft && draft.revision !== latestDraftRevision;
  const mayDiscard = () => !dirty || window.confirm('Discard unsaved style and lyrics edits?');

  useEffect(() => {
    const protect = (event: BeforeUnloadEvent) => { if (dirty) { event.preventDefault(); event.returnValue = ''; } };
    window.addEventListener('beforeunload', protect);
    return () => window.removeEventListener('beforeunload', protect);
  }, [dirty]);

  async function loadDraft(id: string) {
    if (busy || !mayDiscard()) return;
    setBusy(true); setError(''); setNotice('');
    try {
      const [parent, page] = await Promise.all([api<Draft>(`/api/drafts/${id}`), api<PromptVersionPage>(`/api/drafts/${id}/prompt-versions`)]);
      const saved = page.head_id ? await api<PromptVersion>(`/api/drafts/${id}/prompt-versions/${page.head_id}`) : null;
      const context = saved?.draft_snapshot ?? parent;
      const text = saved?.content ?? emptyText();
      setDraft(context); setLatestDraftRevision(parent.revision); setHeadId(page.head_id);
      setItems(page.items); setHasMore(page.has_more); setViewed(saved); setBasedOn(saved?.id ?? null);
      setContent(text); setNote(saved?.note ?? '');
      setBaseline(signature(text, saved?.note ?? '', context, saved?.id ?? null));
      setNotice(saved ? `Loaded text version ${saved.version}.` : 'No saved text yet. Write the first version for this saved draft.');
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function useVersion(id: string) {
    if (!draft || busy || !mayDiscard()) return;
    setBusy(true); setError(''); setNotice('');
    try {
      const saved = await api<PromptVersion>(`/api/drafts/${draft.id}/prompt-versions/${id}`);
      const old = saved.id !== headId;
      setViewed(saved); setDraft(saved.draft_snapshot); setContent(saved.content); setBasedOn(saved.id);
      setNote(old ? `Based on version ${saved.version}` : saved.note);
      if (!old) setBaseline(signature(saved.content, saved.note, saved.draft_snapshot, saved.id));
      setNotice(old ? `Version ${saved.version} is the editing base. Saving will append a new version and preserve the existing history.` : `Loaded current text version ${saved.version}.`);
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function refreshContext() {
    if (!draft || busy) return;
    setBusy(true); setError('');
    try {
      const parent = await api<Draft>(`/api/drafts/${draft.id}`);
      setDraft(parent); setLatestDraftRevision(parent.revision);
      setNotice('Saved draft context refreshed. Your text edits are retained.');
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function more() {
    if (!draft || busy) return;
    setBusy(true); setError('');
    try {
      const page = await api<PromptVersionPage>(`/api/drafts/${draft.id}/prompt-versions?offset=${items.length}`);
      if (page.head_id !== headId) throw new Error('Text history changed. Reload and review it before requesting another page.');
      setItems(current => [...current, ...page.items]); setHasMore(page.has_more);
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function save() {
    if (!draft || busy || !dirty || contextOutdated) return;
    setBusy(true); setError(''); setNotice('');
    try {
      const saved = await api<PromptVersion>(`/api/drafts/${draft.id}/prompt-versions`, {
        draft_revision: draft.revision, expected_head_id: headId, based_on_id: basedOn, content, note,
      });
      setViewed(saved); setHeadId(saved.id); setBasedOn(saved.id); setDraft(saved.draft_snapshot);
      setBaseline(signature(saved.content, saved.note, saved.draft_snapshot, saved.id));
      setItems(current => [summary(saved), ...current]);
      setNotice(`Text version ${saved.version} saved. Earlier versions are unchanged.`);
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  function download(format: 'json' | 'style' | 'lyrics') {
    if (!viewed || dirty) return;
    const text = format === 'json' ? JSON.stringify(viewed, null, 2) : format === 'style' ? viewed.content.style_prompt : viewed.content.lyrics;
    const url = URL.createObjectURL(new Blob([text], { type: format === 'json' ? 'application/json' : 'text/plain;charset=utf-8' }));
    const link = document.createElement('a'); link.href = url;
    link.download = format === 'json' ? `prompt-v${viewed.version}.json` : `${format}-v${viewed.version}.txt`;
    link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  return { draft, latestDraftRevision, viewed, content, setContent, note, setNote, items, hasMore, dirty,
    busy, error, notice, contextOutdated, loadDraft, useVersion, refreshContext, more, save, download };
}
