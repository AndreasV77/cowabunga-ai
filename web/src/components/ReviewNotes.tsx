import type { Packet } from '../types';

export default function ReviewNotes({ packet }: { packet: Pick<Packet, 'crosschecks' | 'omitted'> }) {
  return <>
          {packet.crosschecks.length > 0 && <section className="counterchecks"><h2>Before you combine these</h2>{packet.crosschecks.map(check => <details key={check.id}><summary>{check.topic}<span>{check.assessment}</span></summary><p>{check.conclusion}</p><p className="quiet">{check.evidence_limit}</p></details>)}</section>}
          {packet.omitted.length > 0 && <details className="omissions"><summary>{packet.omitted.length} candidates left out by the source, model or size filter</summary><ul>{packet.omitted.map(item => <li key={item.record_id}>{item.record_id.replace(/^[^:]+:/, '').replaceAll('-', ' ')}<small>{item.reason.replaceAll('_', ' ')}</small></li>)}</ul></details>}
  </>;
}
