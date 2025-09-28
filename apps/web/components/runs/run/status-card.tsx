import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import type { RunStatusSummary } from '../types';
import { statusBadgeClass } from './utils';

export type RunStatusCardProps = {
  status: RunStatusSummary;
};

export function RunStatusCard({ status }: RunStatusCardProps) {
  return (
    <Card className='border-border bg-card'>
      <CardHeader>
        <CardTitle className='text-lg'>Run Status</CardTitle>
      </CardHeader>
      <CardContent className='space-y-4'>
        <div className='flex items-center justify-between'>
          <Label className='text-sm text-muted-foreground'>Status</Label>
          <Badge
            className={statusBadgeClass(status.status)}
            data-testid='run-status'
          >
            {status.status.split('_').join(' ')}
          </Badge>
        </div>
        <div>
          <div className='flex justify-between text-sm mb-2'>
            <span className='text-muted-foreground'>Progress</span>
            <span className='text-foreground'>{status.progress}%</span>
          </div>
          <Progress value={status.progress} className='h-2' />
        </div>
        <div>
          <Label className='text-sm text-muted-foreground'>Current Step</Label>
          <p className='text-sm font-medium text-foreground'>
            {status.currentStep}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
