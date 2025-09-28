import React from 'react';
import { Button } from '@/components/ui/button';
import { Users } from 'lucide-react';

export function UsersEmptyState({
  onClearFilters,
}: {
  onClearFilters: () => void;
}) {
  return (
    <div className='text-center py-16'>
      <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
        <Users className='w-8 h-8 text-muted-foreground' />
      </div>
      <h3 className='text-lg font-semibold text-foreground mb-2'>
        No users found
      </h3>
      <p className='text-muted-foreground mb-4'>Try adjusting your filters</p>
      <Button
        variant='outline'
        onClick={onClearFilters}
        className='border-border bg-transparent'
      >
        Clear filters
      </Button>
    </div>
  );
}
