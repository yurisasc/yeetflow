import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function UsersStatsCards({
  total,
  active,
  admins,
  pending,
}: {
  total: number;
  active: number;
  admins: number;
  pending: number;
}) {
  return (
    <div className='grid grid-cols-1 md:grid-cols-4 gap-6 mt-8'>
      <Card className='border-border bg-card'>
        <CardHeader className='pb-2'>
          <CardTitle className='text-sm font-medium text-muted-foreground'>
            Total Users
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-2xl font-bold text-foreground'>{total}</div>
        </CardContent>
      </Card>

      <Card className='border-border bg-card'>
        <CardHeader className='pb-2'>
          <CardTitle className='text-sm font-medium text-muted-foreground'>
            Active Users
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-2xl font-bold text-foreground'>{active}</div>
        </CardContent>
      </Card>

      <Card className='border-border bg-card'>
        <CardHeader className='pb-2'>
          <CardTitle className='text-sm font-medium text-muted-foreground'>
            Admins
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-2xl font-bold text-foreground'>{admins}</div>
        </CardContent>
      </Card>

      <Card className='border-border bg-card'>
        <CardHeader className='pb-2'>
          <CardTitle className='text-sm font-medium text-muted-foreground'>
            Pending
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-2xl font-bold text-foreground'>{pending}</div>
        </CardContent>
      </Card>
    </div>
  );
}
