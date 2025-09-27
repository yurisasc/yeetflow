import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import type { RunEvent } from '../types';
import { eventIcon, formatTime } from './utils';

export type RunTimelineCardProps = {
  events: RunEvent[];
  heightClass?: string;
};

export function RunTimelineCard({
  events,
  heightClass = 'h-[400px]',
}: RunTimelineCardProps) {
  return (
    <Card className='border-border bg-card flex-1'>
      <CardHeader className='pb-3'>
        <CardTitle className='text-lg'>Timeline</CardTitle>
      </CardHeader>
      <CardContent className='p-0'>
        <ScrollArea className={`${heightClass} px-6`}>
          <div className='space-y-4'>
            {events.map((event) => (
              <div key={event.id} className='flex items-start space-x-3'>
                <div className='flex-shrink-0 mt-1'>
                  {eventIcon(event.type)}
                </div>
                <div className='flex-1 min-w-0'>
                  <div className='flex items-center justify-between'>
                    <p className='text-sm font-medium text-foreground'>
                      {event.step}
                    </p>
                    <span className='text-xs text-muted-foreground'>
                      {formatTime(event.timestamp)}
                    </span>
                  </div>
                  <p className='text-sm text-muted-foreground'>
                    {event.message}
                  </p>
                  {event.progress !== undefined && (
                    <div className='mt-1'>
                      <Progress value={event.progress} className='h-1' />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
