'use client';

import React, { useMemo, useState } from 'react';
import FlowsLayout from '@/components/flows/layout';
import type { FlowListItem } from '@/components/flows/types';
import type { FlowRead } from '@yeetflow/api-client';
import type { StartFlowFormState } from './actions';

type Props = {
  flows: FlowRead[];
  startFlow: (
    _prevState: StartFlowFormState,
    formData: FormData,
  ) => Promise<StartFlowFormState>;
};

export default function FlowsWithUI({ flows, startFlow }: Props) {
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  const normalizedFlows = useMemo<FlowListItem[]>(
    () =>
      flows.map((flow) => ({
        id: flow.id,
        name: flow.name,
        description: flow.description ?? null,
      })),
    [flows],
  );

  const filtered = useMemo(() => {
    if (!query) return normalizedFlows;
    const q = query.toLowerCase();
    return normalizedFlows.filter(
      (f) =>
        f.name.toLowerCase().includes(q) ||
        (f.description ? f.description.toLowerCase().includes(q) : false),
    );
  }, [normalizedFlows, query]);

  return (
    <FlowsLayout
      flows={filtered}
      searchQuery={query}
      onSearchChange={setQuery}
      startFlow={startFlow}
      error={error}
      onError={setError}
    />
  );
}
