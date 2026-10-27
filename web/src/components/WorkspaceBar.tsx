import type { useWorkspace } from '../hooks/useWorkspace';

export default function WorkspaceBar({ workspace }: { workspace: ReturnType<typeof useWorkspace> }) {
  const w = workspace;
  return <section className="drafts-panel" aria-label="Local drafts">
    <div className="draft-heading"><h2>Your drafts</h2><span>{w.unsaved ? 'Unsaved changes' : w.active ? `Saved · revision ${w.active.revision}` : 'Local storage'}</span></div>
    <div className="draft-controls">
      <label htmlFor="draft-name">Draft name<input id="draft-name" value={w.title} maxLength={120} onChange={event => w.setTitle(event.target.value)} placeholder="Name this musical direction"/></label>
      <button disabled={!w.ready || w.busy || !w.title.trim()} onClick={() => w.save()}>Save draft</button>
      {w.active && <button disabled={w.busy} onClick={() => w.save(true)}>Save as new</button>}
      <button disabled={!w.ready || w.busy} onClick={w.newDraft}>New draft</button>
    </div>
    <div className="draft-controls">
      <label htmlFor="saved-drafts">Saved drafts<select id="saved-drafts" value={w.chosen} onChange={event => w.setChosen(event.target.value)}>
        <option value="">Choose a saved draft</option>
        {w.drafts.map(draft => <option key={draft.id} value={draft.id}>{draft.title}</option>)}
      </select></label>
      <button disabled={!w.chosen || w.busy} onClick={w.open}>Open draft</button>
      <button disabled={!w.canExportReferences} onClick={w.exportReferences}>Export draft references</button>
    </div>
    <details><summary>Personal defaults · English prompts</summary>
      <p>New drafts start with {w.defaults.target_model.toUpperCase()} and {w.defaults.supplementary ? 'supplementary sources enabled' : 'V6 core sources only'}. Defaults are saved only when you choose to save them.</p>
      <button disabled={!w.ready || w.busy} onClick={w.saveDefaults}>Use current model and source scope as defaults</button>
    </details>
    <div aria-live="polite">{w.error && <p className="error" role="alert">{w.error}</p>}{w.notice && <p className="notice" role="status">{w.notice}</p>}</div>
  </section>;
}
