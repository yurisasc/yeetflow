import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export function RunsLoadingSkeleton() {
  return (
    <div className='space-y-4'>
      {Array.from({ length: 5 }).map((_, i) => (
        <Card key={i} className='border-border bg-card'>
          <CardHeader>
            <div className='flex items-center justify-between'>
              <Skeleton className='h-6 w-1/3' />
              <Skeleton className='h-5 w-20' />
            </div>
            <Skeleton className='h-4 w-1/4' />
          </CardHeader>
          <CardContent>
            <div className='flex items-center justify-between'>
              <Skeleton className='h-4 w-1/2' />
              <Skeleton className='h-9 w-24' />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
