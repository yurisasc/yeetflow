import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Play } from 'lucide-react';

export type RunsEmptyStateProps = {
  hasActiveFilters: boolean;
  onClearFilters: () => void;
};

export function RunsEmptyState({
  hasActiveFilters,
  onClearFilters,
}: RunsEmptyStateProps) {
  return (
    <div className='text-center py-16'>
      <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
        <Play className='w-8 h-8 text-muted-foreground' />
      </div>
      <h3 className='text-lg font-semibold text-foreground mb-2'>
        No runs found
      </h3>
      <p className='text-muted-foreground mb-4'>
        {hasActiveFilters
          ? 'Try adjusting your filters or search criteria'
          : 'Start your first automation flow to see runs here'}
      </p>
      {hasActiveFilters ? (
        <Button
          variant='outline'
          onClick={onClearFilters}
          className='border-border bg-transparent'
        >
          Clear filters
        </Button>
      ) : (
        <Link href='/flows'>
          <Button className='bg-primary hover:bg-primary/90'>
            Browse Flows
          </Button>
        </Link>
      )}
    </div>
  );
}
