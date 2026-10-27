import { useWorkbench } from './hooks/useWorkbench';
import ConceptLibrary from './components/ConceptLibrary';
import DirectionEditor from './components/DirectionEditor';
import CandidatePalette from './components/CandidatePalette';
import ReviewNotes from './components/ReviewNotes';
import ExportBar from './components/ExportBar';
import SourceInspector from './components/SourceInspector';
import { useWorkspace } from './hooks/useWorkspace';
import WorkspaceBar from './components/WorkspaceBar';
import ListeningPanel from './components/ListeningPanel';
import { useListening } from './hooks/useListening';
import { useState } from 'react';
import { useLibrary } from './hooks/useLibrary';
import ReferenceLibrary from './components/ReferenceLibrary';
import DraftReferences from './components/DraftReferences';
import PromptEditor from './components/PromptEditor';
import { usePromptVersions } from './hooks/usePromptVersions';

export default function App() {
  const workbench = useWorkbench();
  const workspace = useWorkspace(workbench);
  const listening = useListening();
  const library = useLibrary();
  const promptVersions = usePromptVersions();
  const [inspectionOwner, setInspectionOwner] = useState<'context' | 'library'>('context');

  return <div className="app">
    <header className="topbar">
      <a className="brand" href="/" aria-label="Cowabunga AI home"><img className="brand-mark" src="/brand/shaka-icon.svg" width="36" height="36" alt=""/>Cowabunga AI</a>
      <span className="workspace-label">Music workbench</span>
      <span className="local-status"><span aria-hidden="true"/>Local workspace</span>
    </header>
    <div className="workspace">
      <ConceptLibrary
        concepts={workbench.concepts} filtered={workbench.filtered} meta={workbench.meta}
        query={workbench.query} selected={workbench.selected}
        onQueryChange={workbench.setQuery} onToggleConcept={workbench.toggleConcept}
        onClear={workbench.clearSelection}
      />
      <main>
        <WorkspaceBar workspace={workspace}/>
        <PromptEditor editor={promptVersions} currentDraft={workspace.active} workbenchUnsaved={workspace.unsaved}/>
        <ReferenceLibrary library={library} selected={workspace.references} onToggleReference={workspace.toggleReference} onInspect={hit => { setInspectionOwner('library'); library.inspect(hit); }}/>
        <DraftReferences references={workspace.references} inactive={workspace.inactiveReferences}
          onRemove={workspace.toggleReference} onInspect={hit => { setInspectionOwner('library'); library.inspect(hit); }}/>
        <ListeningPanel notebook={listening} drafts={workspace.drafts}/>
        <DirectionEditor
          concepts={workbench.concepts} selected={workbench.selected}
          intent={workbench.intent} model={workbench.model} supplementary={workbench.supplementary}
          busy={workbench.busy} ready={!!workbench.meta} hasAssembly={!!workbench.packet}
          onIntentChange={workbench.setIntent} onModelChange={workbench.setModel}
          onSupplementaryChange={workbench.setSupplementary}
          onToggleConcept={workbench.toggleConcept} onAssemble={() => { setInspectionOwner('context'); workbench.assemble(); }}
        />
        <div className="messages" aria-live="polite">
          {workbench.error && <p className="error" role="alert">{workbench.error}</p>}
          {workbench.notice && <p className="notice" role="status">{workbench.notice}</p>}
          {workbench.dirty && <p className="changed" role="status">Your direction changed. Rebuild the selection before exporting.</p>}
        </div>
        <CandidatePalette
          packet={workbench.packet} included={workbench.included}
          inspected={workbench.inspected} dirty={workbench.dirty}
          onToggleCandidate={workbench.toggleCandidate} onInspect={id => { setInspectionOwner('context'); workbench.inspectCandidate(id); }}
        />
        {workbench.packet && <>
          <ReviewNotes packet={workbench.packet}/>
          <ExportBar includedCount={workbench.included.size} canExport={workbench.canExport}
            onExport={workbench.exportPacket}/>
        </>}
      </main>
      <SourceInspector item={inspectionOwner === 'library' ? library.inspectedItem : workbench.inspectedItem}
        source={inspectionOwner === 'library' ? library.inspectedSource : workbench.inspectedSource}
        open={inspectionOwner === 'library' ? library.inspectorOpen : workbench.inspectorOpen}
        onClose={inspectionOwner === 'library' ? library.closeInspector : workbench.closeInspector}/>
    </div>
  </div>;
}
