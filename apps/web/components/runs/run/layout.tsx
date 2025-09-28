import React from 'react';
import type { RunEvent, RunStatusSummary } from '../types';
import { RunHeader } from './header';
import { RunStatusCard } from './status-card';
import { RunControlsCard } from './controls-card';
import { RunTimelineCard } from './timeline-card';
import { RunBrowserCard } from './browser-card';
import { RunHandoffDialog } from './handoff-dialog';

export type RunDetailLayoutProps = {
  status: RunStatusSummary;
  events: RunEvent[];
  embeddedUrl: string;
  isFullscreen: boolean;
  iframeError: boolean;
  showHandoffDialog: boolean;
  showAdvanced: boolean;
  handoffNotes: string;
  inputJson: string;
  onControlAction: (action: 'resume' | 'pause' | 'stop' | 'handoff') => void;
  onToggleFullscreen: () => void;
  onOpenInNewTab: () => void;
  onIframeError: () => void;
  onIframeLoad: () => void;
  onHandoffDialogChange: (open: boolean) => void;
  onHandoffNotesChange: (value: string) => void;
  onInputJsonChange: (value: string) => void;
  onToggleAdvanced: () => void;
  onSubmitHandoff: () => void;
};

export default function RunDetailLayout({
  status,
  events,
  embeddedUrl,
  isFullscreen,
  iframeError,
  showHandoffDialog,
  showAdvanced,
  handoffNotes,
  inputJson,
  onControlAction,
  onToggleFullscreen,
  onOpenInNewTab,
  onIframeError,
  onIframeLoad,
  onHandoffDialogChange,
  onHandoffNotesChange,
  onInputJsonChange,
  onToggleAdvanced,
  onSubmitHandoff,
}: RunDetailLayoutProps) {
  const timelineHeight = isFullscreen ? 'h-[calc(50vh_-_120px)]' : 'h-[400px]';
  const iframeHeight = isFullscreen ? 'h-[calc(100vh_-_220px)]' : 'h-[600px]';

  return (
    <div className='min-h-screen bg-background'>
      <RunHeader status={status} />

      <div className='container mx-auto px-6 py-6'>
        <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
          <div className='lg:col-span-1 space-y-6'>
            <RunStatusCard status={status} />
            <RunControlsCard
              status={status}
              onControlAction={onControlAction}
            />
            <RunTimelineCard events={events} heightClass={timelineHeight} />
          </div>

          <div className='lg:col-span-2'>
            <RunBrowserCard
              embeddedUrl={embeddedUrl}
              iframeError={iframeError}
              heightClass={iframeHeight}
              onOpenInNewTab={onOpenInNewTab}
              onToggleFullscreen={onToggleFullscreen}
              onIframeError={onIframeError}
              onIframeLoad={onIframeLoad}
            />
          </div>
        </div>
      </div>

      <RunHandoffDialog
        open={showHandoffDialog}
        showAdvanced={showAdvanced}
        handoffNotes={handoffNotes}
        inputJson={inputJson}
        onOpenChange={onHandoffDialogChange}
        onToggleAdvanced={onToggleAdvanced}
        onHandoffNotesChange={onHandoffNotesChange}
        onInputJsonChange={onInputJsonChange}
        onSubmit={onSubmitHandoff}
      />
    </div>
  );
}
