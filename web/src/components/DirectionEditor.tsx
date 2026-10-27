import type { Concept } from '../types';

type Props = {
  concepts: Concept[];
  selected: string[];
  intent: string;
  model: string;
  supplementary: boolean;
  busy: boolean;
  ready: boolean;
  hasAssembly: boolean;
  onIntentChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onSupplementaryChange: (value: boolean) => void;
  onToggleConcept: (id: string) => void;
  onAssemble: () => void;
};

export default function DirectionEditor({ concepts, selected, intent, model, supplementary, busy, ready, hasAssembly,
  onIntentChange, onModelChange, onSupplementaryChange, onToggleConcept, onAssemble }: Props) {
  return (
        <section className="direction" aria-labelledby="direction-heading">
          <div className="heading-row"><h1 id="direction-heading">Give the music a direction.</h1><span className="core-label">{supplementary ? 'V6 first + supplements' : 'V6 core'}</span></div>
          <label htmlFor="intent">Your musical direction</label>
          <textarea id="intent" maxLength={4000} placeholder="Intimate verses opening into a wider chorus, with natural drum character…" value={intent} onChange={e => onIntentChange(e.target.value)}/>
          <div className="controls">
            <label className="model-label" htmlFor="model">Target model<select id="model" value={model} onChange={e => onModelChange(e.target.value)}><option value="v6">v6</option><option value="v6-wild">v6-wild</option><option value="v6-mini">v6-mini</option></select></label>
            <label className="check-label"><input type="checkbox" checked={supplementary} onChange={e => onSupplementaryChange(e.target.checked)}/><span>Include supplementary sources<small>Keep mixed-model guidance visibly separate</small></span></label>
            <button className="primary" disabled={!selected.length || busy || !ready} onClick={onAssemble}>{busy ? 'Assembling…' : hasAssembly ? 'Rebuild selection' : 'Assemble selection'}</button>
          </div>
          {selected.length > 0 && <div className="selected-concepts" aria-label="Selected concepts">{selected.map(id => <button key={id} onClick={() => onToggleConcept(id)} title="Remove concept">{concepts.find(c => c.id === id)?.label || id}<span aria-hidden="true">×</span></button>)}</div>}
        </section>
  );
}
