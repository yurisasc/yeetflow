'use client';

import React, { useState } from 'react';
import RunDetailLayout from '@/components/runs/run/layout';
import type { RunStatusSummary, RunEvent, RunStatus } from '@/components/runs/types';
import { continueWithAIFormAction } from './actions';
import type { RunRead, FlowRead } from '@yeetflow/api-client';

type RunPageWithUIProps = {
  run: RunRead | null;
  flow: FlowRead | null;
  sessionUrl: string | null;
  errorMessage: string | null;
};

export default function RunPageWithUI({
  run,
  flow,
  sessionUrl,
  errorMessage,
}: RunPageWithUIProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [iframeError, setIframeError] = useState(false);
  const [showHandoffDialog, setShowHandoffDialog] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [handoffNotes, setHandoffNotes] = useState('');
  const [inputJson, setInputJson] = useState('');

  // Calculate time elapsed from started_at
  const timeElapsed = run?.started_at
    ? (() => {
        const startTime = new Date(run.started_at);
        const now = new Date();
        const diffMs = now.getTime() - startTime.getTime();
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);

        if (diffHour > 0) return `${diffHour}h ${diffMin % 60}m`;
        if (diffMin > 0) return `${diffMin}m ${diffSec % 60}s`;
        return `${diffSec}s`;
      })()
    : '0s';

  const status: RunStatusSummary = {
    id: run?.id || '',
    name: flow?.name || 'Run Details',
    status: run?.status || 'pending',
    progress: 0, // TODO: calculate from run data if available
    currentStep: 'Unknown', // TODO: get from run data if available
    timeElapsed,
    estimatedTimeRemaining: undefined,
  };

  const events: RunEvent[] = [];

  const handleToggleFullscreen = () => {
    setIsFullscreen((prev) => !prev);
  };

  const handleOpenInNewTab = () => {
    if (sessionUrl) {
      window.open(sessionUrl, '_blank');
    }
  };

  const handleIframeError = () => {
    setIframeError(true);
  };

  const handleIframeLoad = () => {
    setIframeError(false);
  };

  const handleHandoffDialogChange = (open: boolean) => {
    setShowHandoffDialog(open);
  };

  const handleHandoffNotesChange = (value: string) => {
    setHandoffNotes(value);
  };

  const handleInputJsonChange = (value: string) => {
    setInputJson(value);
  };

  const handleToggleAdvanced = () => {
    setShowAdvanced((prev) => !prev);
  };

  const handleSubmitHandoff = async () => {
    // Use the continueWithAIFormAction with the collected data
    const formData = new FormData();
    formData.append('runId', status.id);
    formData.append('notes', handoffNotes);
    formData.append('inputJson', inputJson);

    try {
      await continueWithAIFormAction(formData);
      setShowHandoffDialog(false);
      setHandoffNotes('');
      setInputJson('');
    } catch (error) {
      // Error handling is done in the action
      console.error('Failed to continue with AI:', error);
    }
  };

  if (errorMessage) {
    return (
      <div className='min-h-screen bg-background'>
        <div className='container mx-auto px-6 py-6'>
          <div
            className='rounded-md border border-destructive/20 bg-destructive/10 p-4 text-destructive'
            data-testid='error-message'
          >
            {errorMessage}
          </div>
        </div>
      </div>
    );
  }

  return (
    <RunDetailLayout
      status={status}
      events={events}
      embeddedUrl={sessionUrl || ''}
      isFullscreen={isFullscreen}
      iframeError={iframeError}
      showHandoffDialog={showHandoffDialog}
      showAdvanced={showAdvanced}
      handoffNotes={handoffNotes}
      inputJson={inputJson}
      onToggleFullscreen={handleToggleFullscreen}
      onOpenInNewTab={handleOpenInNewTab}
      onIframeError={handleIframeError}
      onIframeLoad={handleIframeLoad}
      onHandoffDialogChange={handleHandoffDialogChange}
      onHandoffNotesChange={handleHandoffNotesChange}
      onInputJsonChange={handleInputJsonChange}
      onToggleAdvanced={handleToggleAdvanced}
      onSubmitHandoff={handleSubmitHandoff}
    />
  );
}
