import React from 'react';
import { FlowCard } from './card';
import { EmptyFlowsState } from './empty-state';
import type { FlowListItem } from './types';

type StartFlowFormAction = (
  prevState: { error: string | null },
  formData: FormData,
) => Promise<{ error: string | null }>;

type FlowsGridProps = {
  flows: FlowListItem[];
  startFlow: StartFlowFormAction;
  onClearSearch: () => void;
  onError?: (error: string | null) => void;
};

export function FlowsGrid({
  flows,
  startFlow,
  onClearSearch,
  onError,
}: FlowsGridProps) {
  if (flows.length === 0) {
    return <EmptyFlowsState onClearSearch={onClearSearch} />;
  }

  return (
    <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
      {flows.map((flow) => (
        <FlowCard
          key={flow.id}
          flow={flow}
          startFlow={startFlow}
          onError={onError}
        />
      ))}
    </div>
  );
}
