import React from 'react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Grid3X3, List } from 'lucide-react';
import type { FilterOption } from './types';

export type RunsFiltersProps = {
  statusFilter: string;
  flowFilter: string;
  dateRangeFilter: string;
  statusOptions: FilterOption[];
  flowOptions: FilterOption[];
  dateRangeOptions: FilterOption[];
  hasActiveFilters: boolean;
  viewMode: 'table' | 'cards';
  onStatusChange: (value: string) => void;
  onFlowChange: (value: string) => void;
  onDateRangeChange: (value: string) => void;
  onClearFilters: () => void;
  onViewModeChange: (mode: 'table' | 'cards') => void;
};

export function RunsFilters({
  statusFilter,
  flowFilter,
  dateRangeFilter,
  statusOptions,
  flowOptions,
  dateRangeOptions,
  hasActiveFilters,
  viewMode,
  onStatusChange,
  onFlowChange,
  onDateRangeChange,
  onClearFilters,
  onViewModeChange,
}: RunsFiltersProps) {
  return (
    <div className='container mx-auto px-6 mt-6'>
      <div className='flex items-center justify-between'>
        <div className='flex items-center space-x-4'>
          <Select value={statusFilter} onValueChange={onStatusChange}>
            <SelectTrigger className='w-40 bg-input border-border'>
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

          <Select value={flowFilter} onValueChange={onFlowChange}>
            <SelectTrigger className='w-60 bg-input border-border'>
              <SelectValue placeholder='Flow' />
            </SelectTrigger>
            <SelectContent>
              {flowOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={dateRangeFilter} onValueChange={onDateRangeChange}>
            <SelectTrigger className='w-40 bg-input border-border'>
              <SelectValue placeholder='Date Range' />
            </SelectTrigger>
            <SelectContent>
              {dateRangeOptions.map((option) => (
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

        <Tabs
          value={viewMode}
          onValueChange={(value) =>
            onViewModeChange(value as 'table' | 'cards')
          }
        >
          <TabsList className='bg-muted'>
            <TabsTrigger
              value='cards'
              className='data-[state=active]:bg-background'
            >
              <List className='w-4 h-4 mr-2' />
              Cards
            </TabsTrigger>
            <TabsTrigger
              value='table'
              className='data-[state=active]:bg-background'
            >
              <Grid3X3 className='w-4 h-4 mr-2' />
              Table
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
    </div>
  );
}
