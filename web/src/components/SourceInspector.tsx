import type { Item, Source } from '../types';
import { sourceNames, recordTitle } from '../presentation';

type Props = { item?: Item; source?: Source; open: boolean; onClose: () => void };

export default function SourceInspector({ item, source, open, onClose }: Props) {
  const pinnedSource = source?.repository.startsWith('https://github.com/')
    ? `${source.repository.replace(/\.git$/, '').replace(/\/$/, '')}/tree/${source.revision}` : source?.repository;
  const licenseFile = source && Object.keys(source.files).find(path => /(^|\/)LICENSE(\.(md|txt))?$/i.test(path));
  const licenseLink = source?.license_url || (licenseFile && source?.repository.startsWith('https://github.com/')
    ? `${source.repository.replace(/\.git$/, '').replace(/\/$/, '')}/blob/${source.revision}/${licenseFile}` : source?.repository);
  return (
      <aside className={`source-panel ${open ? 'open' : ''}`} aria-label="Source inspection"><div className="source-panel-header"><h2>Source notes</h2><span className="note-dot" aria-hidden="true"/><button className="close-notes" onClick={() => onClose()}>Close source notes</button></div>
        {item && source ? <>
          <p className="source-name">{sourceNames[source.id] || source.id}</p><h3>{recordTitle(item.record)}</h3>
          <dl><dt>Application</dt><dd>{item.v6_core ? 'V6-targeted core candidate' : 'Supplementary reference'}</dd><dt>Source grade</dt><dd>{item.record.evidence?.source_label || 'Publisher recommendation'}</dd><dt>Effect evidence</dt><dd>Not independently verified</dd></dl>
          {item.record.evidence && <p className="evidence-context">{item.record.evidence.context}</p>}
          <h4>Why it is here</h4>{item.uses.length ? item.uses.map(use => <p key={use.concept_id} className="use-note"><strong>{use.relation}</strong>{use.note}</p>) : <p className="quiet">Found by direct search of the active reference collection.</p>}
          {'style_prompt' in item.record && <>
            <h4>Source style prompt</h4><p className="source-style">{item.record.style_prompt}</p>
            <h4>Source arrangement</h4><p>{item.record.structure}</p>
            <h4>Publisher settings</h4><p className="quiet">Suggestions for this recipe, not independently tested settings or personal defaults. Model: {item.record.settings.model_version || 'unspecified'}.</p>
            <dl><dt>BPM</dt><dd>{item.record.settings.bpm ?? 'Unspecified'}</dd><dt>Weirdness</dt><dd>{item.record.settings.weirdness ?? 'Unspecified'}</dd><dt>Style Influence</dt><dd>{item.record.settings.style_influence ?? 'Unspecified'}</dd></dl>
            <a href={item.record.source_record_url} target="_blank" rel="noreferrer">Publisher record page</a>
          </>}
          {'exclude_styles' in item.record && item.record.exclude_styles && <><h4>Source exclusions</h4><p>{item.record.exclude_styles}</p><p className="quiet">Kept separate from style wording.</p></>}
          <h4>Original passages</h4>{item.record.citations.map((citation, i) => <details className="citation" key={i}><summary>Passage {i + 1}, line {citation.line_start}</summary><blockquote>{citation.excerpt}</blockquote><a href={citation.url} target="_blank" rel="noreferrer">Open original source</a></details>)}
          {!item.record.citations.length && <p className="quiet">The full original record is retained in the JSON export.</p>}
          <h4>Source snapshot</h4><a href={pinnedSource} target="_blank" rel="noreferrer">Open repository snapshot</a><p className="quiet" title={source.revision}>Revision {source.revision.slice(0, 12)}</p>
          <div className="license-note"><h4>Reuse</h4><p>{source.attribution}</p><a href={licenseLink} target="_blank" rel="noreferrer">{source.license}</a>{(source.changes || source.license_text) && <details><summary>License and changes</summary><p>{source.changes}</p><pre>{source.license_text}</pre></details>}</div>
        </> : <div className="source-empty"><p>Every phrase has a paper trail.</p><small>Search the reference library or assemble a selection, then inspect a record to see its original passage, evidence limits and reuse terms.</small></div>}
      </aside>
  );
}
