'use client';

import React, { useEffect, useState } from 'react';
import RunsLayout from '@/components/runs/layout';
import type { FilterOption, RunListItem } from '@/components/runs/types';

type RunsWithUIProps = {
  runsList: RunListItem[];
  flowOptions: FilterOption[];
  statusOptions: FilterOption[];
  dateRangeOptions: FilterOption[];
};

export default function RunsWithUI({
  runsList,
  flowOptions,
  statusOptions,
  dateRangeOptions,
}: RunsWithUIProps) {
  const [runs, setRuns] = useState<RunListItem[]>([]);
  const [visibleRuns, setVisibleRuns] = useState<RunListItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [flowFilter, setFlowFilter] = useState('all');
  const [dateRangeFilter, setDateRangeFilter] = useState('all');
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('cards');
  const [isLoading, setIsLoading] = useState(true);
  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setRuns(runsList);
      setIsLoading(false);
    }, 500);
  };

  useEffect(() => {
    const timeout = setTimeout(() => {
      setRuns(runsList);
      setIsLoading(false);
    }, 800);
    return () => clearTimeout(timeout);
  }, [runsList]);

  useEffect(() => {
    let filtered = runs;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (run) =>
          run.flowName.toLowerCase().includes(query) ||
          run.id.toLowerCase().includes(query),
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((run) => run.status === statusFilter);
    }

    if (flowFilter !== 'all') {
      filtered = filtered.filter((run) => run.flowId === flowFilter);
    }

    if (dateRangeFilter !== 'all') {
      const now = new Date();
      const filterDate = new Date(now);
      switch (dateRangeFilter) {
        case '24h':
          filterDate.setHours(now.getHours() - 24);
          break;
        case '7d':
          filterDate.setDate(now.getDate() - 7);
          break;
        case '30d':
          filterDate.setDate(now.getDate() - 30);
          break;
      }
      filtered = filtered.filter(
        (run) => new Date(run.startedAt) >= filterDate,
      );
    }

    setVisibleRuns(filtered);
  }, [runs, searchQuery, statusFilter, flowFilter, dateRangeFilter]);

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const handleCopyLink = (runId: string) => {
    const url = `${window.location.origin}/runs/${runId}`;
    handleCopy(url);
  };

  const resetFilters = () => {
    setSearchQuery('');
    setStatusFilter('all');
    setFlowFilter('all');
    setDateRangeFilter('all');
  };

  return (
    <RunsLayout
      isLoading={isLoading}
      visibleRuns={visibleRuns}
      searchQuery={searchQuery}
      statusFilter={statusFilter}
      flowFilter={flowFilter}
      dateRangeFilter={dateRangeFilter}
      statusOptions={statusOptions}
      flowOptions={flowOptions}
      dateRangeOptions={dateRangeOptions}
      viewMode={viewMode}
      onSearchChange={setSearchQuery}
      onStatusChange={setStatusFilter}
      onFlowChange={setFlowFilter}
      onDateRangeChange={setDateRangeFilter}
      onClearFilters={resetFilters}
      onViewModeChange={setViewMode}
      onRefresh={handleRefresh}
      onCopyToClipboard={handleCopy}
      onCopyLink={handleCopyLink}
    />
  );
}
