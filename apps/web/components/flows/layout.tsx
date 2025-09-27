import React from 'react';
import { FlowsHeader } from './header';
import { FlowsGrid } from './grid';
import type { FlowListItem } from './types';

type StartFlowFormAction = (
  prevState: { error: string | null },
  formData: FormData,
) => Promise<{ error: string | null }>;

type Props = {
  flows: FlowListItem[];
  searchQuery: string;
  onSearchChange: (v: string) => void;
  startFlow: StartFlowFormAction;
  error?: string | null;
  onError?: (error: string | null) => void;
};

export default function FlowsLayout({
  flows,
  searchQuery,
  onSearchChange,
  startFlow,
  error,
  onError,
}: Props) {
  return (
    <div className='min-h-screen bg-background' data-testid='flows-list'>
      <FlowsHeader searchQuery={searchQuery} onSearchChange={onSearchChange} />

      {error && (
        <div className='mb-6 p-4 bg-red-500/10 border border-red-500/20 mx-6 mt-6 rounded-lg'>
          <p className='text-red-400 text-sm'>{error}</p>
        </div>
      )}

      <div className={`container mx-auto px-6 ${error ? 'pb-8' : 'py-8'}`}>
        <FlowsGrid
          flows={flows}
          startFlow={startFlow}
          onClearSearch={() => onSearchChange('')}
          onError={onError}
        />
      </div>
    </div>
  );
}
