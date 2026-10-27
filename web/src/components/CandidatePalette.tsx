import type { Packet } from '../types';
import { sourceNames, recordTitle, recordField } from '../presentation';

type Props = {
  packet: Pick<Packet, 'items' | 'sources'> | null;
  included: ReadonlySet<string>;
  inspected: string | null;
  dirty: boolean;
  onToggleCandidate: (id: string) => void;
  onInspect: (id: string) => void;
};

export default function CandidatePalette({ packet, included, inspected, dirty, onToggleCandidate, onInspect }: Props) {
  if (!packet) return <section className="empty-workbench"><div className="phrase-lines" aria-hidden="true"><span/><span/><span/></div><h2>Start with a musical job.</h2><p>Select a concept on the left, then assemble its source-backed wording here.</p><p className="quiet">You choose between alternatives. A source claim stays a source claim.</p></section>;
  return <>
          <div className="results-heading"><div><h2>Your wording palette</h2><p>{included.size} of {packet.items.length} candidates included. Select the parts that fit.</p></div><span className="count-mark">{packet.items.length}</span></div>
          {!packet.items.length && <p className="notice">No candidates fit this model and source selection. Try another concept or review the omitted candidates below.</p>}
          <div className={`candidates ${dirty ? 'outdated' : ''}`} aria-label="Wording candidates">
            {packet.items.map(item => <article key={item.record.id} className={`candidate ${included.has(item.record.id) ? 'included' : ''} ${inspected === item.record.id ? 'inspected' : ''}`}>
              <div className="candidate-top"><label className="candidate-toggle"><input type="checkbox" aria-label={`Include ${recordTitle(item.record)}`} checked={included.has(item.record.id)} onChange={() => onToggleCandidate(item.record.id)}/><span>{recordField(item.record)}</span></label><span className={`source-tag ${item.v6_core ? '' : 'supplement'}`}>{sourceNames[packet.sources[item.snapshot_id].id] || packet.sources[item.snapshot_id].id}{!item.v6_core && ' · supplementary'}</span></div>
              <h3>{recordTitle(item.record)}</h3>
              {'meaning' in item.record ? <p>{item.record.meaning}</p> : <p className="recipe-text">{item.record.style_prompt}</p>}
              <div className="candidate-bottom"><span>{[...new Set(item.uses.map(use => use.relation))].join(' / ')}</span><button className="text-button" onClick={() => onInspect(item.record.id)}>Inspect source<span aria-hidden="true"> ↗</span></button></div>
            </article>)}
          </div>
  </>;
}
