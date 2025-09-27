import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Bot, Pause, Play, Square } from 'lucide-react';
import type { RunStatusSummary } from '../types';

export type RunControlsCardProps = {
  status: RunStatusSummary;
  onControlAction: (action: 'resume' | 'pause' | 'stop' | 'handoff') => void;
};

export function RunControlsCard({
  status,
  onControlAction,
}: RunControlsCardProps) {
  return (
    <Card className='border-border bg-card'>
      <CardHeader className='pb-3'>
        <CardTitle className='text-lg'>Controls</CardTitle>
      </CardHeader>
      <CardContent className='space-y-3'>
        <div className='grid grid-cols-2 gap-2'>
          {status.status === 'running' ? (
            <Button
              variant='outline'
              onClick={() => onControlAction('pause')}
              className='border-border'
            >
              <Pause className='w-4 h-4 mr-2' />
              Pause
            </Button>
          ) : (
            <Button
              onClick={() => onControlAction('resume')}
              className='bg-primary hover:bg-primary/90'
            >
              <Play className='w-4 h-4 mr-2' />
              Resume
            </Button>
          )}
          <Button
            variant='outline'
            onClick={() => onControlAction('stop')}
            className='border-border'
          >
            <Square className='w-4 h-4 mr-2' />
            Stop
          </Button>
        </div>
        <Button
          onClick={() => onControlAction('handoff')}
          className='w-full bg-purple-600 hover:bg-purple-700 text-white'
        >
          <Bot className='w-4 h-4 mr-2' />
          Complete Manual Steps
        </Button>
      </CardContent>
    </Card>
  );
}
