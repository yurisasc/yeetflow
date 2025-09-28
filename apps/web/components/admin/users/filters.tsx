import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { FilterOption } from './types';
import { Users } from 'lucide-react';

export type UsersFiltersProps = {
  roleFilter: string;
  statusFilter: string;
  roleOptions: FilterOption[];
  statusOptions: FilterOption[];
  hasActiveFilters: boolean;
  totalCount: number;
  onRoleChange: (v: string) => void;
  onStatusChange: (v: string) => void;
  onClearFilters: () => void;
};

export function UsersFilters({
  roleFilter,
  statusFilter,
  roleOptions,
  statusOptions,
  hasActiveFilters,
  totalCount,
  onRoleChange,
  onStatusChange,
  onClearFilters,
}: UsersFiltersProps) {
  return (
    <div className='container mx-auto px-6 mt-6'>
      <div className='flex items-center justify-between'>
        <div className='flex items-center space-x-4'>
          <Select value={roleFilter} onValueChange={onRoleChange}>
            <SelectTrigger
              className='w-40 bg-input border-border'
              aria-label='Role filter'
            >
              <SelectValue placeholder='Role' />
            </SelectTrigger>
            <SelectContent>
              {roleOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={statusFilter} onValueChange={onStatusChange}>
            <SelectTrigger
              className='w-40 bg-input border-border'
              aria-label='Status filter'
            >
              <SelectValue placeholder='Status' />
            </SelectTrigger>
            <SelectContent>
              {statusOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {hasActiveFilters && (
            <Button
              variant='ghost'
              size='sm'
              onClick={onClearFilters}
              className='text-muted-foreground'
            >
              Clear filters
            </Button>
          )}
        </div>

        <div className='flex items-center space-x-2 text-sm text-muted-foreground'>
          <Users className='w-4 h-4' />
          <span>{totalCount} users</span>
        </div>
      </div>
    </div>
  );
}
