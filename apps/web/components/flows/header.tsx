import React from 'react';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';

type FlowsHeaderProps = {
  searchQuery: string;
  onSearchChange: (query: string) => void;
};

export function FlowsHeader({ searchQuery, onSearchChange }: FlowsHeaderProps) {
  return (
    <div className='border-b border-border bg-card/50'>
      <div className='container mx-auto px-6 py-6'>
        <div className='flex items-center justify-between'>
          <div>
            <h1 className='text-3xl font-bold text-foreground'>Flows</h1>
            <p className='text-muted-foreground mt-1'>
              Discover and start automation workflows
            </p>
          </div>
          <div className='relative'>
            <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
            <Input
              placeholder='Search flows...'
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className='pl-10 w-80 bg-input border-border'
            />
          </div>
        </div>
      </div>
    </div>
  );
}
