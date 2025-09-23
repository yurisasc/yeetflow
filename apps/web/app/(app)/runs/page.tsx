'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  Search,
  Clock,
  Play,
  Eye,
  Calendar,
  RefreshCw,
  MoreHorizontal,
  Copy,
  ExternalLink,
  Download,
  FileText,
  FileSpreadsheet,
  Archive,
  ImageIcon,
  Grid3X3,
  List,
} from 'lucide-react';

interface RunArtifact {
  id: string;
  filename: string;
  type: 'json' | 'csv' | 'zip' | 'image' | 'pdf';
  size: string;
  generatedAt: string;
}

interface Run {
  id: string;
  flowName: string;
  flowId: string;
  status:
    | 'idle'
    | 'running'
    | 'paused'
    | 'awaiting_input'
    | 'error'
    | 'completed'
    | 'canceled';
  progress: number;
  startedAt: string;
  duration: string;
  currentStep?: string;
  artifacts: RunArtifact[];
}

const mockRuns: Run[] = [
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

const flowOptions = [
  { value: 'all', label: 'All Flows' },
  { value: 'flow-accounts-payable', label: 'Accounts Payable Reconciliation' },
  { value: 'flow-data-migration', label: 'Customer Data Migration' },
  { value: 'flow-report-generation', label: 'Monthly Report Generation' },
  { value: 'flow-user-onboarding', label: 'Employee Onboarding' },
  { value: 'flow-invoice-processing', label: 'Invoice Processing' },
];

const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'running', label: 'Running' },
  { value: 'awaiting_input', label: 'Awaiting Input' },
  { value: 'paused', label: 'Paused' },
  { value: 'completed', label: 'Completed' },
  { value: 'error', label: 'Error' },
  { value: 'canceled', label: 'Canceled' },
];

const dateRangeOptions = [
  { value: 'all', label: 'All Time' },
  { value: '24h', label: 'Last 24 Hours' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
];

export default function RunsPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [filteredRuns, setFilteredRuns] = useState<Run[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [flowFilter, setFlowFilter] = useState('all');
  const [dateRangeFilter, setDateRangeFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('cards');
  const [selectedRunArtifacts, setSelectedRunArtifacts] = useState<Run | null>(
    null,
  );

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setRuns(mockRuns);
      setFilteredRuns(mockRuns);
      setIsLoading(false);
    }, 800);
  }, []);

  useEffect(() => {
    let filtered = runs;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (run) =>
          run.flowName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          run.id.toLowerCase().includes(searchQuery.toLowerCase()),
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((run) => run.status === statusFilter);
    }

    // Flow filter
    if (flowFilter !== 'all') {
      filtered = filtered.filter((run) => run.flowId === flowFilter);
    }

    // Date range filter (simplified for demo)
    if (dateRangeFilter !== 'all') {
      const now = new Date();
      const filterDate = new Date();

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

    setFilteredRuns(filtered);
  }, [runs, searchQuery, statusFilter, flowFilter, dateRangeFilter]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
      case 'running':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'paused':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'awaiting_input':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      case 'error':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'completed':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'canceled':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const getArtifactIcon = (type: string) => {
    switch (type) {
      case 'json':
        return <FileText className='w-4 h-4' />;
      case 'csv':
        return <FileSpreadsheet className='w-4 h-4' />;
      case 'zip':
        return <Archive className='w-4 h-4' />;
      case 'image':
        return <ImageIcon className='w-4 h-4' />;
      default:
        return <FileText className='w-4 h-4' />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setStatusFilter('all');
    setFlowFilter('all');
    setDateRangeFilter('all');
  };

  const hasActiveFilters =
    searchQuery ||
    statusFilter !== 'all' ||
    flowFilter !== 'all' ||
    dateRangeFilter !== 'all';

  return (
    <div className='min-h-screen bg-background'>
      {/* Header */}
      <div className='border-b border-border bg-card/50'>
        <div className='container mx-auto px-6 py-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold text-foreground'>Runs</h1>
              <p className='text-muted-foreground mt-1'>
                View run history and monitor progress
              </p>
            </div>
            <div className='flex items-center space-x-4'>
              {/* Search */}
              <div className='relative'>
                <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
                <Input
                  placeholder='Search runs or IDs...'
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className='pl-10 w-80 bg-input border-border'
                />
              </div>

              {/* Refresh */}
              <Button
                variant='outline'
                size='sm'
                className='border-border bg-transparent'
              >
                <RefreshCw className='w-4 h-4' />
              </Button>
            </div>
          </div>

          {/* Filters */}
          <div className='flex items-center justify-between mt-6'>
            <div className='flex items-center space-x-4'>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
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

              <Select value={flowFilter} onValueChange={setFlowFilter}>
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

              <Select
                value={dateRangeFilter}
                onValueChange={setDateRangeFilter}
              >
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
                  onClick={clearFilters}
                  className='text-muted-foreground'
                >
                  Clear filters
                </Button>
              )}
            </div>

            {/* View Mode Toggle */}
            <Tabs
              value={viewMode}
              onValueChange={(value) => setViewMode(value as 'table' | 'cards')}
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
      </div>

      {/* Content */}
      <div className='container mx-auto px-6 py-8'>
        {isLoading ? (
          <div className='space-y-4'>
            {Array.from({ length: 5 }).map((_, i) => (
              <Card key={i} className='border-border bg-card'>
                <CardHeader>
                  <div className='flex items-center justify-between'>
                    <Skeleton className='h-6 w-1/3' />
                    <Skeleton className='h-5 w-20' />
                  </div>
                  <Skeleton className='h-4 w-1/4' />
                </CardHeader>
                <CardContent>
                  <div className='flex items-center justify-between'>
                    <Skeleton className='h-4 w-1/2' />
                    <Skeleton className='h-9 w-24' />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredRuns.length === 0 ? (
          <div className='text-center py-16'>
            <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
              <Play className='w-8 h-8 text-muted-foreground' />
            </div>
            <h3 className='text-lg font-semibold text-foreground mb-2'>
              No runs found
            </h3>
            <p className='text-muted-foreground mb-4'>
              {hasActiveFilters
                ? 'Try adjusting your filters or search criteria'
                : 'Start your first automation flow to see runs here'}
            </p>
            {hasActiveFilters ? (
              <Button
                variant='outline'
                onClick={clearFilters}
                className='border-border bg-transparent'
              >
                Clear filters
              </Button>
            ) : (
              <Link href='/flows'>
                <Button className='bg-primary hover:bg-primary/90'>
                  Browse Flows
                </Button>
              </Link>
            )}
          </div>
        ) : (
          <>
            {viewMode === 'cards' ? (
              <div className='space-y-4'>
                {filteredRuns.map((run) => (
                  <Card
                    key={run.id}
                    className='border-border bg-card hover:bg-card/80 transition-colors'
                  >
                    <CardHeader className='pb-3'>
                      <div className='flex items-center justify-between'>
                        <CardTitle className='text-lg text-foreground'>
                          {run.flowName}
                        </CardTitle>
                        <div className='flex items-center space-x-2'>
                          {run.artifacts.length > 0 && (
                            <div className='flex items-center space-x-1'>
                              {run.artifacts.slice(0, 3).map((artifact) => (
                                <Badge
                                  key={artifact.id}
                                  variant='outline'
                                  className='text-xs'
                                >
                                  {getArtifactIcon(artifact.type)}
                                  <span className='ml-1'>
                                    {artifact.type.toUpperCase()}
                                  </span>
                                </Badge>
                              ))}
                              {run.artifacts.length > 3 && (
                                <Badge variant='outline' className='text-xs'>
                                  +{run.artifacts.length - 3}
                                </Badge>
                              )}
                            </div>
                          )}
                          <Badge className={getStatusColor(run.status)}>
                            {run.status.replace('_', ' ')}
                          </Badge>
                        </div>
                      </div>
                      <CardDescription className='flex items-center space-x-4 text-muted-foreground'>
                        <div className='flex items-center'>
                          <Calendar className='w-4 h-4 mr-1' />
                          {formatDate(run.startedAt)}
                        </div>
                        <div className='flex items-center'>
                          <Clock className='w-4 h-4 mr-1' />
                          {run.duration}
                        </div>
                        {run.currentStep && (
                          <div className='text-sm'>
                            Current: {run.currentStep}
                          </div>
                        )}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className='pt-0'>
                      <div className='flex items-center justify-between'>
                        <div className='flex-1 mr-4'>
                          <div className='flex justify-between text-sm mb-1'>
                            <span className='text-muted-foreground'>
                              Progress
                            </span>
                            <span className='text-foreground'>
                              {run.progress}%
                            </span>
                          </div>
                          <div className='w-full bg-secondary rounded-full h-2'>
                            <div
                              className='bg-primary h-2 rounded-full transition-all'
                              style={{ width: `${run.progress}%` }}
                            />
                          </div>
                        </div>
                        <div className='flex items-center space-x-2'>
                          {run.artifacts.length > 0 && (
                            <Sheet>
                              <SheetTrigger asChild>
                                <Button
                                  variant='outline'
                                  size='sm'
                                  className='border-border bg-transparent'
                                >
                                  <Archive className='w-4 h-4 mr-2' />
                                  Artifacts ({run.artifacts.length})
                                </Button>
                              </SheetTrigger>
                              <SheetContent className='w-96 bg-card border-border'>
                                <SheetHeader>
                                  <SheetTitle>
                                    Artifacts - {run.flowName}
                                  </SheetTitle>
                                </SheetHeader>
                                <div className='mt-6 space-y-3'>
                                  {run.artifacts.map((artifact) => (
                                    <div
                                      key={artifact.id}
                                      className='flex items-center justify-between p-3 border border-border rounded-lg'
                                    >
                                      <div className='flex items-center space-x-3'>
                                        {getArtifactIcon(artifact.type)}
                                        <div>
                                          <p className='text-sm font-medium text-foreground'>
                                            {artifact.filename}
                                          </p>
                                          <p className='text-xs text-muted-foreground'>
                                            {artifact.size} •{' '}
                                            {formatDate(artifact.generatedAt)}
                                          </p>
                                        </div>
                                      </div>
                                      <div className='flex items-center space-x-1'>
                                        <Button variant='ghost' size='sm'>
                                          <Eye className='w-4 h-4' />
                                        </Button>
                                        <Button variant='ghost' size='sm'>
                                          <Download className='w-4 h-4' />
                                        </Button>
                                      </div>
                                    </div>
                                  ))}
                                  {run.artifacts.length > 1 && (
                                    <Button
                                      variant='outline'
                                      className='w-full border-border bg-transparent'
                                    >
                                      <Download className='w-4 h-4 mr-2' />
                                      Download All
                                    </Button>
                                  )}
                                </div>
                              </SheetContent>
                            </Sheet>
                          )}
                          <Link href={`/runs/${run.id}`}>
                            <Button
                              variant='outline'
                              className='border-border bg-transparent'
                            >
                              <Eye className='w-4 h-4 mr-2' />
                              View Details
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className='border border-border rounded-lg bg-card'>
                <Table>
                  <TableHeader>
                    <TableRow className='border-border'>
                      <TableHead className='text-foreground'>Status</TableHead>
                      <TableHead className='text-foreground'>Flow</TableHead>
                      <TableHead className='text-foreground'>Run ID</TableHead>
                      <TableHead className='text-foreground'>Started</TableHead>
                      <TableHead className='text-foreground'>
                        Duration
                      </TableHead>
                      <TableHead className='text-foreground'>
                        Artifacts
                      </TableHead>
                      <TableHead className='text-foreground'>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRuns.map((run) => (
                      <TableRow
                        key={run.id}
                        className='border-border hover:bg-muted/50'
                      >
                        <TableCell>
                          <Badge className={getStatusColor(run.status)}>
                            {run.status.replace('_', ' ')}
                          </Badge>
                        </TableCell>
                        <TableCell className='font-medium text-foreground'>
                          {run.flowName}
                        </TableCell>
                        <TableCell>
                          <div className='flex items-center space-x-2'>
                            <code className='text-xs bg-muted px-2 py-1 rounded'>
                              {run.id.slice(-8)}
                            </code>
                            <Button
                              variant='ghost'
                              size='sm'
                              onClick={() => copyToClipboard(run.id)}
                            >
                              <Copy className='w-3 h-3' />
                            </Button>
                          </div>
                        </TableCell>
                        <TableCell className='text-muted-foreground'>
                          {formatDate(run.startedAt)}
                        </TableCell>
                        <TableCell className='text-muted-foreground'>
                          {run.duration}
                        </TableCell>
                        <TableCell>
                          {run.artifacts.length > 0 ? (
                            <div className='flex items-center space-x-1'>
                              {run.artifacts.slice(0, 2).map((artifact) => (
                                <Badge
                                  key={artifact.id}
                                  variant='outline'
                                  className='text-xs'
                                >
                                  {getArtifactIcon(artifact.type)}
                                  <span className='ml-1'>
                                    {artifact.type.toUpperCase()}
                                  </span>
                                </Badge>
                              ))}
                              {run.artifacts.length > 2 && (
                                <Badge variant='outline' className='text-xs'>
                                  +{run.artifacts.length - 2}
                                </Badge>
                              )}
                            </div>
                          ) : (
                            <span className='text-muted-foreground text-sm'>
                              None
                            </span>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className='flex items-center space-x-2'>
                            <Link href={`/runs/${run.id}`}>
                              <Button variant='ghost' size='sm'>
                                <Eye className='w-4 h-4' />
                              </Button>
                            </Link>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant='ghost' size='sm'>
                                  <MoreHorizontal className='w-4 h-4' />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent
                                align='end'
                                className='bg-popover border-border'
                              >
                                <DropdownMenuItem>
                                  <ExternalLink className='w-4 h-4 mr-2' />
                                  Open in new tab
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={() => copyToClipboard(run.id)}
                                >
                                  <Copy className='w-4 h-4 mr-2' />
                                  Copy ID
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={() =>
                                    copyToClipboard(
                                      `${window.location.origin}/runs/${run.id}`,
                                    )
                                  }
                                >
                                  <Copy className='w-4 h-4 mr-2' />
                                  Copy link
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
