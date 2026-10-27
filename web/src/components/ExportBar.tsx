type Props = {
  includedCount: number;
  canExport: boolean;
  onExport: (format: 'json' | 'markdown', copy?: boolean) => void;
};

export default function ExportBar({ includedCount, canExport, onExport }: Props) {
  return (
          <footer className="export-bar"><div><strong>{includedCount} candidates ready</strong><small>Context with sources, not a finished prompt</small></div><button disabled={!canExport} onClick={() => onExport('markdown', true)}>Copy context</button><button disabled={!canExport} onClick={() => onExport('markdown')}>Markdown</button><button disabled={!canExport} onClick={() => onExport('json')}>JSON</button></footer>
  );
}
