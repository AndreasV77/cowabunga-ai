import type { Draft } from '../types';
import type { usePromptVersions } from '../hooks/usePromptVersions';

export default function PromptEditor({ editor: e, currentDraft, workbenchUnsaved }: { editor: ReturnType<typeof usePromptVersions>; currentDraft: Draft | null; workbenchUnsaved: boolean }) {
  return <details className="prompt-editor"><summary>Style &amp; lyrics · version history</summary>
    <p>Write your own style prompt and lyrics. Each saved version keeps its exact text, fingerprints and linked draft context.</p>
    <button disabled={!currentDraft || workbenchUnsaved || e.busy} onClick={() => currentDraft && e.loadDraft(currentDraft.id)}>Load text history for saved draft</button>
    {(!currentDraft || workbenchUnsaved) && <p className="quiet">Save or open a draft before loading its text history.</p>}
    {e.draft && <>
      <p className="text-binding">Editing <strong>{e.draft.title}</strong> · saved draft revision {e.draft.revision}. Changing the workbench draft does not move these text edits.</p>
      {currentDraft?.id !== e.draft.id && <p className="changed">This editor is still attached to the draft named above. Load the current draft explicitly to switch.</p>}
      {e.contextOutdated && <p className="changed">A newer saved draft context exists. Refresh it before saving a new text version; your text edits will be retained.</p>}
      <div className="text-history" aria-label="Saved text versions">{e.items.map(item => <button key={item.id} disabled={e.busy} aria-pressed={item.id === e.viewed?.id} onClick={() => e.useVersion(item.id)}>Version {item.version}{item.note ? ` · ${item.note}` : ''}</button>)}{e.hasMore && <button disabled={e.busy} onClick={e.more}>More text versions</button>}</div>
      <fieldset disabled={e.busy} className="text-fields">
        <div className="draft-heading"><h2>{e.viewed ? `Editing from version ${e.viewed.version}` : 'First text version'}</h2><span>{e.dirty ? 'Unsaved text changes' : e.viewed ? 'Saved text' : 'Not saved yet'}</span></div>
        <label htmlFor="style-text">Style prompt<textarea id="style-text" rows={6} maxLength={20000} value={e.content.style_prompt} onChange={event => e.setContent({ ...e.content, style_prompt: event.target.value })}/></label>
        <p className="quiet">{e.content.style_prompt.length} characters · English prompting</p>
        <label htmlFor="lyrics-text">Lyrics and section instructions<textarea id="lyrics-text" rows={12} maxLength={100000} value={e.content.lyrics} onChange={event => e.setContent({ ...e.content, lyrics: event.target.value })}/></label>
        <label htmlFor="text-note">Version note<input id="text-note" maxLength={2000} value={e.note} onChange={event => e.setNote(event.target.value)}/></label>
        <div className="draft-controls"><button disabled={!e.dirty || e.contextOutdated} onClick={e.save}>Save new text version</button><button onClick={e.refreshContext}>Refresh saved draft context</button></div>
        <div className="draft-controls"><button disabled={!e.viewed || e.dirty} onClick={() => e.download('style')}>Export saved style</button><button disabled={!e.viewed || e.dirty} onClick={() => e.download('lyrics')}>Export saved lyrics</button><button disabled={!e.viewed || e.dirty} onClick={() => e.download('json')}>Export text version JSON</button></div>
      </fieldset>
      {e.viewed && <details className="text-fingerprints"><summary>Saved context and text fingerprints</summary>
        <p>Saved with draft revision {e.viewed.draft_snapshot.revision}, {e.viewed.draft_snapshot.selection?.library?.items.length ?? 0} kept library references and {e.viewed.draft_snapshot.selection?.selected_ids?.length ?? 0} checked concept records.</p>
        <p>Style: <code>{e.viewed.style_sha256}</code></p><p>Lyrics: <code>{e.viewed.lyrics_sha256}</code></p>
      </details>}
    </>}
    <div aria-live="polite">{e.error && <p className="error" role="alert">{e.error}</p>}{e.notice && <p className="notice" role="status">{e.notice}</p>}</div>
  </details>;
}
