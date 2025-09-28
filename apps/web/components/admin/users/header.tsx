import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, UserPlus } from 'lucide-react';

export type UsersHeaderProps = {
  searchQuery: string;
  onSearchChange: (v: string) => void;
};

export function UsersHeader({ searchQuery, onSearchChange }: UsersHeaderProps) {
  return (
    <div className='border-b border-border bg-card/50'>
      <div className='container mx-auto px-6 py-6'>
        <div className='flex flex-col gap-6 md:flex-row md:items-center md:justify-between'>
          <div>
            <h1 className='text-3xl font-bold text-foreground'>
              User Management
            </h1>
            <p className='text-muted-foreground mt-1'>
              Manage users and their roles
            </p>
          </div>
          <div className='flex flex-col gap-4 md:flex-row md:items-center md:space-x-4 md:gap-0'>
            <div className='relative w-full md:w-auto'>
              <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
              <Input
                placeholder='Search users...'
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className='pl-10 w-full md:w-80 bg-input border-border'
              />
            </div>
            <Button
              disabled
              className='w-full md:w-auto bg-primary hover:bg-primary/90'
            >
              <UserPlus className='w-4 h-4 mr-2' />
              Invite User
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
