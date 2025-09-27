import RunsWithUI from './with-ui';
import type { FilterOption, RunListItem } from '@/components/runs/types';

const mockRuns: RunListItem[] = [
  {
    id: 'accounts-payable-1737632400000',
    flowName: 'Accounts Payable Reconciliation',
    flowId: 'flow-accounts-payable',
    status: 'completed',
    progress: 100,
    startedAt: '2025-01-23T10:00:00Z',
    duration: '18m 32s',
    artifacts: [
      {
        id: '1',
        filename: 'reconciliation_report.json',
        type: 'json',
        size: '2.4 KB',
        generatedAt: '2025-01-23T10:18:00Z',
      },
      {
        id: '2',
        filename: 'discrepancies.csv',
        type: 'csv',
        size: '15.2 KB',
        generatedAt: '2025-01-23T10:18:00Z',
      },
    ],
  },
  {
    id: 'data-migration-1737628800000',
    flowName: 'Customer Data Migration',
    flowId: 'flow-data-migration',
    status: 'running',
    progress: 65,
    startedAt: '2025-01-23T09:00:00Z',
    duration: '42m 15s',
    currentStep: 'Validating customer records',
    artifacts: [
      {
        id: '3',
        filename: 'migration_log.json',
        type: 'json',
        size: '8.7 KB',
        generatedAt: '2025-01-23T09:30:00Z',
      },
    ],
  },
  {
    id: 'report-generation-1737625200000',
    flowName: 'Monthly Report Generation',
    flowId: 'flow-report-generation',
    status: 'awaiting_input',
    progress: 80,
    startedAt: '2025-01-23T08:00:00Z',
    duration: '12m 45s',
    currentStep: 'Manual review required',
    artifacts: [
      {
        id: '4',
        filename: 'draft_report.zip',
        type: 'zip',
        size: '1.2 MB',
        generatedAt: '2025-01-23T08:12:00Z',
      },
      {
        id: '5',
        filename: 'charts.zip',
        type: 'zip',
        size: '856 KB',
        generatedAt: '2025-01-23T08:12:00Z',
      },
    ],
  },
  {
    id: 'user-onboarding-1737621600000',
    flowName: 'Employee Onboarding',
    flowId: 'flow-user-onboarding',
    status: 'error',
    progress: 35,
    startedAt: '2025-01-23T07:00:00Z',
    duration: '8m 22s',
    currentStep: 'Failed to create user account',
    artifacts: [],
  },
  {
    id: 'invoice-processing-1737618000000',
    flowName: 'Invoice Processing',
    flowId: 'flow-invoice-processing',
    status: 'completed',
    progress: 100,
    startedAt: '2025-01-23T06:00:00Z',
    duration: '6m 18s',
    artifacts: [
      {
        id: '6',
        filename: 'processed_invoices.csv',
        type: 'csv',
        size: '45.3 KB',
        generatedAt: '2025-01-23T06:06:00Z',
      },
      {
        id: '7',
        filename: 'summary.json',
        type: 'json',
        size: '1.8 KB',
        generatedAt: '2025-01-23T06:06:00Z',
      },
    ],
  },
];

const flowOptions: FilterOption[] = [
  { value: 'all', label: 'All Flows' },
  { value: 'flow-accounts-payable', label: 'Accounts Payable Reconciliation' },
  { value: 'flow-data-migration', label: 'Customer Data Migration' },
  { value: 'flow-report-generation', label: 'Monthly Report Generation' },
  { value: 'flow-user-onboarding', label: 'Employee Onboarding' },
  { value: 'flow-invoice-processing', label: 'Invoice Processing' },
];

const statusOptions: FilterOption[] = [
  { value: 'all', label: 'All Status' },
  { value: 'running', label: 'Running' },
  { value: 'awaiting_input', label: 'Awaiting Input' },
  { value: 'paused', label: 'Paused' },
  { value: 'completed', label: 'Completed' },
  { value: 'error', label: 'Error' },
  { value: 'canceled', label: 'Canceled' },
];

const dateRangeOptions: FilterOption[] = [
  { value: 'all', label: 'All Time' },
  { value: '24h', label: 'Last 24 Hours' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
];

export default function RunsPage() {
  return (
    <RunsWithUI
      runsList={mockRuns}
      flowOptions={flowOptions}
      statusOptions={statusOptions}
      dateRangeOptions={dateRangeOptions}
    />
  );
}
