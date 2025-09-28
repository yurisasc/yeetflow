import React from 'react';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';

type EmptyFlowsStateProps = {
  onClearSearch: () => void;
};

export function EmptyFlowsState({ onClearSearch }: EmptyFlowsStateProps) {
  return (
    <div className='text-center py-16'>
      <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
        <Search aria-hidden='true' className='w-8 h-8 text-muted-foreground' />
      </div>
      <h3 className='text-lg font-semibold text-foreground mb-2'>
        No flows found
      </h3>
      <p className='text-muted-foreground mb-4'>Try adjusting your search</p>
      <Button
        variant='outline'
        onClick={onClearSearch}
        className='border-border'
        type='button'
      >
        Clear search
      </Button>
    </div>
  );
}
