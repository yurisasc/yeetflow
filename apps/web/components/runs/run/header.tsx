import React from 'react';
import type { RunStatusSummary } from '../types';

export type RunHeaderProps = {
  status: RunStatusSummary;
};

export function RunHeader({ status }: RunHeaderProps) {
  return (
    <div className='border-b border-border bg-card/50 h-16'>
      <div className='container mx-auto px-6 h-full flex items-center'>
        <h1 className='text-2xl font-bold text-foreground'>
          {status.name}
        </h1>
      </div>
    </div>
  );
}
