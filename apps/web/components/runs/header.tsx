import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { RefreshCw, Search } from 'lucide-react';

export type RunsHeaderProps = {
  title?: string;
  subtitle?: string;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onRefresh: () => void;
};

export function RunsHeader({
  title = 'Runs',
  subtitle = 'View run history and monitor progress',
  searchQuery,
  onSearchChange,
  onRefresh,
}: RunsHeaderProps) {
  return (
    <div className='border-b border-border bg-card/50'>
      <div className='container mx-auto px-6 py-6'>
        <div className='flex items-center justify-between'>
          <div>
            <h1 className='text-3xl font-bold text-foreground'>{title}</h1>
            <p className='text-muted-foreground mt-1'>{subtitle}</p>
          </div>
          <div className='flex items-center space-x-4'>
            <div className='relative'>
              <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
              <Input
                placeholder='Search runs or IDs...'
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className='pl-10 w-80 bg-input border-border'
              />
            </div>
            <Button
              variant='outline'
              size='sm'
              className='border-border bg-transparent'
              onClick={onRefresh}
            >
              <RefreshCw className='w-4 h-4' />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
