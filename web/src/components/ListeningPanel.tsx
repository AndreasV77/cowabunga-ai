import type { DraftSummary, RatedObservation, Score } from '../types';
import type { useListening } from '../hooks/useListening';

function ScoreField({ label, value, onChange, replay = false }: { label: string; value: Score; onChange: (value: Score) => void; replay?: boolean }) {
  return <label>{label}<select value={value ?? ''} onChange={event => onChange(event.target.value === '' ? null : Number(event.target.value) as Score)}>
    <option value="">Not assessed</option><option value="0">0 · {replay ? 'No' : 'Absent / weak'}</option>
    <option value="1">1 · {replay ? 'Maybe' : 'Partial / uncertain'}</option><option value="2">2 · {replay ? 'Yes' : 'Clear / fulfilled'}</option>
  </select></label>;
}

function ObservationGroup({ title, hint, items, onChange }: { title: string; hint: string; items: RatedObservation[]; onChange: (items: RatedObservation[]) => void }) {
  return <fieldset className="observation-group"><legend>{title}</legend><p>{hint}</p>
    {items.map((item, index) => <div className="observation-row" key={item.id}>
      <ScoreField label={item.label} value={item.score} onChange={score => onChange(items.map((value, i) => i === index ? { ...value, score } : value))}/>
      <label>Observation · {item.label}<textarea rows={2} maxLength={4000} value={item.note} onChange={event => onChange(items.map((value, i) => i === index ? { ...value, note: event.target.value } : value))}/></label>
    </div>)}
  </fieldset>;
}

export default function ListeningPanel({ notebook: n, drafts }: { notebook: ReturnType<typeof useListening>; drafts: DraftSummary[] }) {
  const a = n.assessment;
  const generation = (patch: Partial<typeof a.generation>) => n.setAssessment({ ...a, generation: { ...a.generation, ...patch } });
  const setting = (key: string, value: string) => generation({ settings: { ...a.generation.settings, [key]: value === '' ? null : Number(value) } });
  return <details className="listening-panel"><summary>Listening notebook · execution, sound and replay value</summary>
    <p className="listening-intro">Keep what the music does, how the render sounds and whether you want to replay it separate. Empty means not assessed. There is no combined score.</p>
    <fieldset disabled={n.busy} className="listening-shell">
      <div className="draft-controls"><label>Listening notes for saved draft<select value={n.chosenDraft} onChange={event => n.setChosenDraft(event.target.value)}>
        <option value="">Choose a saved draft</option>{drafts.map(draft => <option key={draft.id} value={draft.id}>{draft.title}</option>)}
      </select></label><button disabled={!n.chosenDraft} onClick={n.loadDraft}>Load listening notes</button></div>
      {n.draft && <>
        <p className="listening-target">Notes for <strong>{n.draft.title}</strong>. This notebook stays attached to this draft when you change the workbench direction.</p>
        <div className="report-list" aria-label="Saved listening reports">{n.reports.map(report => <button key={report.id} aria-pressed={report.id === n.active?.id} onClick={() => n.openReport(report)}>{report.title}</button>)}<button onClick={n.newReport}>New listening report</button></div>
        <div className="draft-heading"><h2>{n.active ? 'Listening report' : 'New listening report'}</h2><span>{n.dirty ? 'Unsaved notes' : n.active ? `Saved · revision ${n.active.revision}` : 'Not saved yet'}</span></div>
        <label>Listening report name<input value={n.title} maxLength={120} onChange={event => n.setTitle(event.target.value)}/></label>
        <div className="listening-grid">
          <label>Provider<input value={a.generation.provider} maxLength={100} onChange={event => generation({ provider: event.target.value })}/></label>
          <label>Actual model<input value={a.generation.model} maxLength={100} onChange={event => generation({ model: event.target.value })}/></label>
          <label>Weirdness · if applicable<input type="number" min={0} max={100} value={a.generation.settings.weirdness as number ?? ''} onChange={event => setting('weirdness', event.target.value)}/></label>
          <label>Style Influence · if applicable<input type="number" min={0} max={100} value={a.generation.settings.style_influence as number ?? ''} onChange={event => setting('style_influence', event.target.value)}/></label>
        </div>
        <label>Song link or reference<input value={a.generation.song_reference} maxLength={2000} onChange={event => generation({ song_reference: event.target.value })}/></label>
        <label>Input identity and generation context<textarea rows={3} maxLength={4000} value={a.generation.input_note} onChange={event => generation({ input_note: event.target.value })}/></label>
        <ObservationGroup title="Musical execution" hint="Were the requested voices, instruments, rhythms and transitions realized?" items={a.musical_execution} onChange={items => n.setAssessment({ ...a, musical_execution: items })}/>
        <ObservationGroup title="Sound quality" hint="Judge body, clarity and fullness separately from the musical arrangement." items={a.sound_quality} onChange={items => n.setAssessment({ ...a, sound_quality: items })}/>
        <fieldset className="observation-group"><legend>Personal listening value</legend><div className="listening-grid">
          <ScoreField replay label="Immediate replay desire" value={a.listening_value.immediate_replay} onChange={value => n.setAssessment({ ...a, listening_value: { ...a.listening_value, immediate_replay: value } })}/>
          <ScoreField replay label="Replay desire on a later listen" value={a.listening_value.later_replay} onChange={value => n.setAssessment({ ...a, listening_value: { ...a.listening_value, later_replay: value } })}/>
        </div><label>Later listening · when and in what context?<textarea rows={2} maxLength={2000} value={a.listening_value.later_listening_context} onChange={event => n.setAssessment({ ...a, listening_value: { ...a.listening_value, later_listening_context: event.target.value } })}/></label></fieldset>
        <fieldset className="observation-group"><legend>Reported problems</legend><p>Record presence directly. “None heard” is a positive outcome, not a failed musical score.</p>
          <div className="listening-grid">{(['sung_instructions', 'omitted_lyrics', 'merged_voices'] as const).map(key => <label key={key}>{({ sung_instructions: 'Sung instructions', omitted_lyrics: 'Omitted lyrics', merged_voices: 'Unintentionally merged voices' })[key]}<select value={a.problems[key]} onChange={event => n.setAssessment({ ...a, problems: { ...a.problems, [key]: event.target.value } })}><option value="unknown">Not assessed</option><option value="none">None heard</option><option value="present">Present</option></select></label>)}</div>
          <label>Problem notes<textarea rows={2} maxLength={4000} value={a.problems.note} onChange={event => n.setAssessment({ ...a, problems: { ...a.problems, note: event.target.value } })}/></label>
        </fieldset>
        <label>Interpretation or suspected cause · separate from observations<textarea rows={3} maxLength={8000} value={a.interpretation} onChange={event => n.setAssessment({ ...a, interpretation: event.target.value })}/></label>
        {n.active && <details className="original-evidence"><summary>Original evidence and linked draft · retained unchanged</summary>
          <p>User listening report. Effects are not independently verified. Linked draft revision: {n.active.draft_snapshot.revision}.</p>
          <pre>{JSON.stringify({ raw_report: n.active.original_assessment.raw_report, original_assessment: n.active.original_assessment, draft_snapshot: n.active.draft_snapshot }, null, 2)}</pre>
        </details>}
        <div className="draft-controls"><button disabled={!n.title.trim()} onClick={n.save}>Save listening report</button><button disabled={!n.active || n.dirty} onClick={n.download}>Export listening JSON</button></div>
      </>}
    </fieldset>
    <div aria-live="polite">{n.error && <p className="error" role="alert">{n.error}</p>}{n.notice && <p className="notice" role="status">{n.notice}</p>}</div>
  </details>;
}
