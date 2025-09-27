import React from 'react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import type { AccountUser } from './types';

type AccountHeaderProps = {
  user: AccountUser;
};

export function AccountHeader({ user }: AccountHeaderProps) {
  return (
    <div className='border-b border-border bg-card/50'>
      <div className='container mx-auto px-6 py-6'>
        <div className='flex items-center justify-between'>
          <div>
            <h1 className='text-3xl font-bold text-foreground'>
              Account Settings
            </h1>
            <p className='text-muted-foreground mt-1'>
              Manage your profile and account preferences
            </p>
          </div>
          <div className='flex items-center space-x-3'>
            <Avatar className='h-12 w-12'>
              <AvatarFallback className='bg-primary text-primary-foreground text-lg'>
                {user?.name?.charAt(0) || 'U'}
              </AvatarFallback>
            </Avatar>
            <div>
              <div className='flex items-center space-x-2'>
                <p className='font-medium text-foreground'>
                  {user?.name || 'User'}
                </p>
                <Badge
                  variant={user?.role === 'admin' ? 'default' : 'secondary'}
                >
                  {user?.role === 'admin' ? 'Admin' : 'User'}
                </Badge>
              </div>
              <p className='text-sm text-muted-foreground'>{user?.email}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
