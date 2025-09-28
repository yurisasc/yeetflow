import React from 'react';
import type { FilterOption, RunListItem } from './types';
import { RunsHeader } from './header';
import { RunsFilters } from './filters';
import { RunsLoadingSkeleton } from './loading-skeleton';
import { RunsEmptyState } from './empty-state';
import { RunsCardsList } from './cards-list';
import { RunsTableList } from './table-list';

type RunsLayoutProps = {
  isLoading: boolean;
  visibleRuns: RunListItem[];
  searchQuery: string;
  statusFilter: string;
  flowFilter: string;
  dateRangeFilter: string;
  statusOptions: FilterOption[];
  flowOptions: FilterOption[];
  dateRangeOptions: FilterOption[];
  viewMode: 'table' | 'cards';
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onFlowChange: (value: string) => void;
  onDateRangeChange: (value: string) => void;
  onClearFilters: () => void;
  onViewModeChange: (mode: 'table' | 'cards') => void;
  onRefresh: () => void;
  onCopyToClipboard: (text: string) => void;
  onCopyLink: (runId: string) => void;
};

export default function RunsLayout({
  isLoading,
  visibleRuns,
  searchQuery,
  statusFilter,
  flowFilter,
  dateRangeFilter,
  statusOptions,
  flowOptions,
  dateRangeOptions,
  viewMode,
  onSearchChange,
  onStatusChange,
  onFlowChange,
  onDateRangeChange,
  onClearFilters,
  onViewModeChange,
  onRefresh,
  onCopyToClipboard,
  onCopyLink,
}: RunsLayoutProps) {
  const hasActiveFilters =
    Boolean(searchQuery) ||
    statusFilter !== 'all' ||
    flowFilter !== 'all' ||
    dateRangeFilter !== 'all';

  return (
    <div className='min-h-screen bg-background'>
      <RunsHeader
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        onRefresh={onRefresh}
      />

      <RunsFilters
        statusFilter={statusFilter}
        flowFilter={flowFilter}
        dateRangeFilter={dateRangeFilter}
        statusOptions={statusOptions}
        flowOptions={flowOptions}
        dateRangeOptions={dateRangeOptions}
        hasActiveFilters={hasActiveFilters}
        viewMode={viewMode}
        onStatusChange={onStatusChange}
        onFlowChange={onFlowChange}
        onDateRangeChange={onDateRangeChange}
        onClearFilters={onClearFilters}
        onViewModeChange={onViewModeChange}
      />

      <div className='container mx-auto px-6 py-8'>
        {isLoading ? (
          <RunsLoadingSkeleton />
        ) : visibleRuns.length === 0 ? (
          <RunsEmptyState
            hasActiveFilters={hasActiveFilters}
            onClearFilters={onClearFilters}
          />
        ) : viewMode === 'cards' ? (
          <RunsCardsList runs={visibleRuns} />
        ) : (
          <RunsTableList
            runs={visibleRuns}
            onCopyId={onCopyToClipboard}
            onCopyLink={onCopyLink}
          />
        )}
      </div>
    </div>
  );
}
