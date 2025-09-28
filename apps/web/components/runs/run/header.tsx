import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Clock } from 'lucide-react';
import type { RunStatusSummary } from '../types';
import { statusBadgeClass } from './utils';

export type RunHeaderProps = {
  status: RunStatusSummary;
};

export function RunHeader({ status }: RunHeaderProps) {
  return (
    <div className='border-b border-border bg-card/50'>
      <div className='container mx-auto px-6 py-4'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center space-x-4'>
            <h1 className='text-2xl font-bold text-foreground'>
              {status.name}
            </h1>
            <Badge
              className={statusBadgeClass(status.status)}
              data-testid='run-status'
            >
              {status.status.split('_').join(' ')}
            </Badge>
          </div>
          <div className='flex items-center space-x-2 text-sm text-muted-foreground'>
            <Clock className='w-4 h-4' />
            <span>{status.timeElapsed}</span>
            {status.estimatedTimeRemaining && (
              <>
                <span>•</span>
                <span>{status.estimatedTimeRemaining} remaining</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
