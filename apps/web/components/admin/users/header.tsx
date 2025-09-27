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
        <div className='flex items-center justify-between'>
          <div>
            <h1 className='text-3xl font-bold text-foreground'>
              User Management
            </h1>
            <p className='text-muted-foreground mt-1'>
              Manage users and their roles
            </p>
          </div>
          <div className='flex items-center space-x-4'>
            <div className='relative'>
              <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
              <Input
                placeholder='Search users...'
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className='pl-10 w-80 bg-input border-border'
              />
            </div>

            <Button disabled className='bg-primary hover:bg-primary/90'>
              <UserPlus className='w-4 h-4 mr-2' />
              Invite User
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
