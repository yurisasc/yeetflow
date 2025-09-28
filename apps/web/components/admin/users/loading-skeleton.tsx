import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';

export function UsersLoadingSkeleton() {
  return (
    <div className='border border-border rounded-lg bg-card'>
      <Table aria-busy={true} aria-label='Loading users'>
        <TableHeader>
          <TableRow className='border-border'>
            <TableHead>User</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Last Login</TableHead>
            <TableHead>Runs</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 6 }).map((_, i) => (
            <TableRow key={i} className='border-border'>
              <TableCell>
                <div className='flex items-center space-x-3'>
                  <Skeleton className='h-8 w-8 rounded-full' />
                  <div>
                    <Skeleton className='h-4 w-32 mb-1' />
                    <Skeleton className='h-3 w-48' />
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <Skeleton className='h-5 w-16' />
              </TableCell>
              <TableCell>
                <Skeleton className='h-5 w-20' />
              </TableCell>
              <TableCell>
                <Skeleton className='h-4 w-24' />
              </TableCell>
              <TableCell>
                <Skeleton className='h-4 w-12' />
              </TableCell>
              <TableCell>
                <Skeleton className='h-8 w-8' />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
