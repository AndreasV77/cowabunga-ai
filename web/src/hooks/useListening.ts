import { useEffect, useState } from 'react';
import { api } from '../api';
import type { Draft, ListeningAssessment, ListeningDocument, RatedObservation } from '../types';

function blankAssessment(): ListeningAssessment {
  const observations = (items: [string, string][]): RatedObservation[] => items.map(([id, label]) => ({ id, label, score: null, note: '' }));
  return {
    schema_version: '1.0', evidence_source: 'user_report', independently_verified: false,
    generation: { provider: 'Suno', model: '', settings: {}, song_reference: '', input_note: '', style_sha256: null, lyrics_sha256: null },
    musical_execution: observations([['vocal-technique', 'Requested vocal technique'], ['pop-hook', 'Clear sung hook'], ['instrumentation-groove', 'Requested instruments and rhythmic movement'], ['role-coexistence', 'Musical roles coexist'], ['shared-motif', 'Motif returns recognizably'], ['section-transition', 'Bridge and return']]),
    sound_quality: observations([['sound-body', 'Body, weight and fullness'], ['clarity', 'Clarity and separation']]),
    listening_value: { immediate_replay: null, later_replay: null, later_listening_context: '' },
    problems: { sung_instructions: 'unknown', omitted_lyrics: 'unknown', merged_voices: 'unknown', note: '' },
    interpretation: '', raw_report: null,
  };
}

export function useListening() {
  const [chosenDraft, setChosenDraft] = useState('');
  const [draft, setDraft] = useState<Draft | null>(null);
  const [reports, setReports] = useState<ListeningDocument[]>([]);
  const [active, setActive] = useState<ListeningDocument | null>(null);
  const [assessment, setAssessment] = useState<ListeningAssessment>(blankAssessment);
  const [title, setTitle] = useState('');
  const [baseline, setBaseline] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const signature = JSON.stringify({ title: title.trim(), assessment });
  const dirty = baseline !== null && signature !== baseline;
  const mayDiscard = () => !dirty || window.confirm('Discard unsaved listening notes?');

  useEffect(() => {
    const protect = (event: BeforeUnloadEvent) => { if (dirty) { event.preventDefault(); event.returnValue = ''; } };
    window.addEventListener('beforeunload', protect);
    return () => window.removeEventListener('beforeunload', protect);
  }, [dirty]);

  function edit(document: ListeningDocument | null) {
    const value = document ? structuredClone(document.assessment) : blankAssessment();
    const name = document?.title ?? '';
    setActive(document); setAssessment(value); setTitle(name);
    setBaseline(JSON.stringify({ title: name, assessment: value }));
    setError(''); setNotice('');
  }

  async function loadDraft() {
    if (!chosenDraft || busy || !mayDiscard()) return;
    setBusy(true); setError('');
    try {
      const [parent, list] = await Promise.all([api<Draft>(`/api/drafts/${chosenDraft}`), api<ListeningDocument[]>(`/api/drafts/${chosenDraft}/listening`)]);
      setDraft(parent); setReports(list); edit(null);
      setNotice(`${list.length} saved listening reports for “${parent.title}”.`);
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function save() {
    if (!draft || !title.trim() || busy) return;
    setBusy(true); setError(''); setNotice('');
    const submitted = signature;
    try {
      const base = `/api/drafts/${draft.id}/listening`;
      const document = await api<ListeningDocument>(active ? `${base}/${active.id}` : base,
        { title: title.trim(), assessment, draft_revision: active?.draft_snapshot.revision ?? draft.revision, revision: active?.revision ?? 0 }, active ? 'PUT' : 'POST');
      setActive(document); setBaseline(submitted);
      setReports(list => [document, ...list.filter(item => item.id !== document.id)]);
      setNotice('Listening report saved. Original evidence and the linked draft snapshot are retained.');
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  function download() {
    if (!active || dirty) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(active, null, 2)], { type: 'application/json' }));
    const link = document.createElement('a'); link.href = url; link.download = `listening-${active.id}.json`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  return { chosenDraft, setChosenDraft, draft, reports, active, assessment, setAssessment, title, setTitle,
    dirty, busy, error, notice, loadDraft, save, download,
    openReport: (document: ListeningDocument) => { if (mayDiscard()) edit(document); },
    newReport: () => { if (mayDiscard()) edit(null); },
  };
}
