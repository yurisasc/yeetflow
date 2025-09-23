'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Search,
  ArrowLeft,
  Download,
  Eye,
  MoreHorizontal,
  FileText,
  FileSpreadsheet,
  Archive,
  ImageIcon,
  Copy,
  ExternalLink,
  Grid3X3,
  List,
  Calendar,
  HardDrive,
} from 'lucide-react';

interface Artifact {
  id: string;
  filename: string;
  type: 'json' | 'csv' | 'zip' | 'image' | 'pdf' | 'txt' | 'xml';
  size: string;
  sizeBytes: number;
  generatedAt: string;
  stepName: string;
  description?: string;
  downloadUrl: string;
  previewUrl?: string;
}

const mockArtifacts: Artifact[] = [
  {
    id: '1',
    filename: 'reconciliation_report.json',
    type: 'json',
    size: '2.4 KB',
    sizeBytes: 2400,
    generatedAt: '2025-01-23T10:18:00Z',
    stepName: 'Generate Report',
    description:
      'Complete reconciliation report with all matched and unmatched transactions',
    downloadUrl: '/api/artifacts/1/download',
    previewUrl: '/api/artifacts/1/preview',
  },
  {
    id: '2',
    filename: 'discrepancies.csv',
    type: 'csv',
    size: '15.2 KB',
    sizeBytes: 15200,
    generatedAt: '2025-01-23T10:18:00Z',
    stepName: 'Identify Discrepancies',
    description: 'List of all identified discrepancies requiring manual review',
    downloadUrl: '/api/artifacts/2/download',
    previewUrl: '/api/artifacts/2/preview',
  },
  {
    id: '3',
    filename: 'transaction_summary.pdf',
    type: 'pdf',
    size: '1.8 MB',
    sizeBytes: 1800000,
    generatedAt: '2025-01-23T10:17:00Z',
    stepName: 'Create Summary',
    description: 'Executive summary of the reconciliation process',
    downloadUrl: '/api/artifacts/3/download',
  },
  {
    id: '4',
    filename: 'backup_data.zip',
    type: 'zip',
    size: '5.4 MB',
    sizeBytes: 5400000,
    generatedAt: '2025-01-23T10:16:00Z',
    stepName: 'Backup Data',
    description: 'Complete backup of processed data and intermediate results',
    downloadUrl: '/api/artifacts/4/download',
  },
  {
    id: '5',
    filename: 'process_log.txt',
    type: 'txt',
    size: '892 B',
    sizeBytes: 892,
    generatedAt: '2025-01-23T10:15:00Z',
    stepName: 'Initialize Process',
    description: 'Detailed log of the reconciliation process execution',
    downloadUrl: '/api/artifacts/5/download',
    previewUrl: '/api/artifacts/5/preview',
  },
  {
    id: '6',
    filename: 'chart_visualization.png',
    type: 'image',
    size: '245 KB',
    sizeBytes: 245000,
    generatedAt: '2025-01-23T10:17:30Z',
    stepName: 'Generate Charts',
    description: 'Visual representation of reconciliation results',
    downloadUrl: '/api/artifacts/6/download',
    previewUrl: '/api/artifacts/6/preview',
  },
];

const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'json', label: 'JSON' },
  { value: 'csv', label: 'CSV' },
  { value: 'pdf', label: 'PDF' },
  { value: 'zip', label: 'ZIP' },
  { value: 'image', label: 'Images' },
  { value: 'txt', label: 'Text' },
];

const sortOptions = [
  { value: 'newest', label: 'Newest First' },
  { value: 'oldest', label: 'Oldest First' },
  { value: 'largest', label: 'Largest First' },
  { value: 'smallest', label: 'Smallest First' },
  { value: 'name', label: 'Name A-Z' },
];

export default function RunArtifactsPage() {
  const params = useParams();
  const runId = params.id as string;

  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [filteredArtifacts, setFilteredArtifacts] = useState<Artifact[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedArtifacts, setSelectedArtifacts] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [previewArtifact, setPreviewArtifact] = useState<Artifact | null>(null);
  const [previewContent, setPreviewContent] = useState<string>('');

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setArtifacts(mockArtifacts);
      setFilteredArtifacts(mockArtifacts);
      setIsLoading(false);
    }, 800);
  }, []);

  useEffect(() => {
    let filtered = artifacts;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (artifact) =>
          artifact.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
          artifact.stepName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          artifact.description
            ?.toLowerCase()
            .includes(searchQuery.toLowerCase()),
      );
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter((artifact) => artifact.type === typeFilter);
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return (
            new Date(b.generatedAt).getTime() -
            new Date(a.generatedAt).getTime()
          );
        case 'oldest':
          return (
            new Date(a.generatedAt).getTime() -
            new Date(b.generatedAt).getTime()
          );
        case 'largest':
          return b.sizeBytes - a.sizeBytes;
        case 'smallest':
          return a.sizeBytes - b.sizeBytes;
        case 'name':
          return a.filename.localeCompare(b.filename);
        default:
          return 0;
      }
    });

    setFilteredArtifacts(filtered);
  }, [artifacts, searchQuery, typeFilter, sortBy]);

  const getArtifactIcon = (type: string) => {
    switch (type) {
      case 'json':
      case 'txt':
      case 'xml':
        return <FileText className='w-5 h-5' />;
      case 'csv':
        return <FileSpreadsheet className='w-5 h-5' />;
      case 'zip':
        return <Archive className='w-5 h-5' />;
      case 'image':
        return <ImageIcon className='w-5 h-5' />;
      default:
        return <FileText className='w-5 h-5' />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'json':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'csv':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'pdf':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'zip':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      case 'image':
        return 'bg-pink-500/10 text-pink-400 border-pink-500/20';
      case 'txt':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
      default:
        return 'bg-muted text-muted-foreground';
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

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (
      Number.parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    );
  };

  const handleSelectArtifact = (artifactId: string) => {
    setSelectedArtifacts((prev) =>
      prev.includes(artifactId)
        ? prev.filter((id) => id !== artifactId)
        : [...prev, artifactId],
    );
  };

  const handleSelectAll = () => {
    if (selectedArtifacts.length === filteredArtifacts.length) {
      setSelectedArtifacts([]);
    } else {
      setSelectedArtifacts(filteredArtifacts.map((a) => a.id));
    }
  };

  const handlePreview = (artifact: Artifact) => {
    setPreviewArtifact(artifact);
    // Simulate loading preview content
    if (artifact.type === 'json') {
      setPreviewContent(`{
  "reconciliation_summary": {
    "total_transactions": 1247,
    "matched_transactions": 1198,
    "unmatched_transactions": 49,
    "discrepancies_found": 12,
    "total_amount_processed": "$2,847,392.18"
  },
  "status": "completed",
  "processing_time": "18m 32s"
}`);
    } else if (artifact.type === 'csv') {
      setPreviewContent(`Transaction ID,Amount,Status,Notes
TXN-001,$1,250.00,Matched,
TXN-002,$875.50,Unmatched,Missing reference
TXN-003,$2,100.00,Matched,
TXN-004,$450.75,Discrepancy,Amount mismatch`);
    } else if (artifact.type === 'txt') {
      setPreviewContent(`[2025-01-23 10:15:00] Process initialized
[2025-01-23 10:15:02] Loading transaction data...
[2025-01-23 10:15:05] 1247 transactions loaded
[2025-01-23 10:15:06] Starting reconciliation process
[2025-01-23 10:17:30] Reconciliation completed
[2025-01-23 10:18:00] Report generated successfully`);
    }
  };

  const handleBulkDownload = () => {
    console.log('Downloading selected artifacts:', selectedArtifacts);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setTypeFilter('all');
    setSortBy('newest');
  };

  const hasActiveFilters =
    searchQuery || typeFilter !== 'all' || sortBy !== 'newest';
  const totalSize = filteredArtifacts.reduce(
    (sum, artifact) => sum + artifact.sizeBytes,
    0,
  );

  return (
    <div className='min-h-screen bg-background'>
      {/* Header */}
      <div className='border-b border-border bg-card/50'>
        <div className='container mx-auto px-6 py-6'>
          <div className='flex items-center justify-between'>
            <div className='flex items-center space-x-4'>
              <Link href={`/runs/${runId}`}>
                <Button
                  variant='ghost'
                  size='sm'
                  className='text-muted-foreground'
                >
                  <ArrowLeft className='w-4 h-4 mr-2' />
                  Back to Run
                </Button>
              </Link>
              <div>
                <h1 className='text-3xl font-bold text-foreground'>
                  Run Artifacts
                </h1>
                <p className='text-muted-foreground mt-1'>
                  {filteredArtifacts.length} artifacts •{' '}
                  {formatFileSize(totalSize)}
                </p>
              </div>
            </div>
            <div className='flex items-center space-x-4'>
              {/* Search */}
              <div className='relative'>
                <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
                <Input
                  placeholder='Search artifacts...'
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className='pl-10 w-80 bg-input border-border'
                />
              </div>

              {/* Bulk Actions */}
              {selectedArtifacts.length > 0 && (
                <Button
                  onClick={handleBulkDownload}
                  className='bg-primary hover:bg-primary/90'
                >
                  <Download className='w-4 h-4 mr-2' />
                  Download Selected ({selectedArtifacts.length})
                </Button>
              )}
            </div>
          </div>

          {/* Filters and Controls */}
          <div className='flex items-center justify-between mt-6'>
            <div className='flex items-center space-x-4'>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className='w-40 bg-input border-border'>
                  <SelectValue placeholder='Type' />
                </SelectTrigger>
                <SelectContent>
                  {typeOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className='w-40 bg-input border-border'>
                  <SelectValue placeholder='Sort by' />
                </SelectTrigger>
                <SelectContent>
                  {sortOptions.map((option) => (
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

            <div className='flex items-center space-x-4'>
              {/* Select All */}
              <div className='flex items-center space-x-2'>
                <Checkbox
                  checked={
                    selectedArtifacts.length === filteredArtifacts.length &&
                    filteredArtifacts.length > 0
                  }
                  onCheckedChange={handleSelectAll}
                />
                <span className='text-sm text-muted-foreground'>
                  Select all
                </span>
              </div>

              {/* View Mode Toggle */}
              <Tabs
                value={viewMode}
                onValueChange={(value) => setViewMode(value as 'grid' | 'list')}
              >
                <TabsList className='bg-muted'>
                  <TabsTrigger
                    value='grid'
                    className='data-[state=active]:bg-background'
                  >
                    <Grid3X3 className='w-4 h-4' />
                  </TabsTrigger>
                  <TabsTrigger
                    value='list'
                    className='data-[state=active]:bg-background'
                  >
                    <List className='w-4 h-4' />
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className='container mx-auto px-6 py-8'>
        {isLoading ? (
          <div
            className={
              viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                : 'space-y-4'
            }
          >
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className='border-border bg-card'>
                <CardHeader>
                  <div className='flex items-center justify-between'>
                    <Skeleton className='h-6 w-1/2' />
                    <Skeleton className='h-5 w-16' />
                  </div>
                  <Skeleton className='h-4 w-3/4' />
                </CardHeader>
                <CardContent>
                  <div className='flex items-center justify-between'>
                    <Skeleton className='h-4 w-1/3' />
                    <Skeleton className='h-8 w-20' />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredArtifacts.length === 0 ? (
          <div className='text-center py-16'>
            <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
              <Archive className='w-8 h-8 text-muted-foreground' />
            </div>
            <h3 className='text-lg font-semibold text-foreground mb-2'>
              No artifacts found
            </h3>
            <p className='text-muted-foreground mb-4'>
              {hasActiveFilters
                ? 'Try adjusting your filters'
                : "This run hasn't generated any artifacts yet"}
            </p>
            {hasActiveFilters && (
              <Button
                variant='outline'
                onClick={clearFilters}
                className='border-border bg-transparent'
              >
                Clear filters
              </Button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {filteredArtifacts.map((artifact) => (
              <Card
                key={artifact.id}
                className='border-border bg-card hover:bg-card/80 transition-colors'
              >
                <CardHeader className='pb-3'>
                  <div className='flex items-center justify-between'>
                    <div className='flex items-center space-x-2'>
                      <Checkbox
                        checked={selectedArtifacts.includes(artifact.id)}
                        onCheckedChange={() =>
                          handleSelectArtifact(artifact.id)
                        }
                      />
                      <div className='flex items-center space-x-2'>
                        {getArtifactIcon(artifact.type)}
                        <CardTitle className='text-sm text-foreground truncate'>
                          {artifact.filename}
                        </CardTitle>
                      </div>
                    </div>
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
                        {artifact.previewUrl && (
                          <DropdownMenuItem
                            onClick={() => handlePreview(artifact)}
                          >
                            <Eye className='w-4 h-4 mr-2' />
                            Preview
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuItem>
                          <Download className='w-4 h-4 mr-2' />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() =>
                            navigator.clipboard.writeText(artifact.filename)
                          }
                        >
                          <Copy className='w-4 h-4 mr-2' />
                          Copy name
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <ExternalLink className='w-4 h-4 mr-2' />
                          Open in new tab
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                  <div className='flex items-center space-x-2'>
                    <Badge className={getTypeColor(artifact.type)}>
                      {artifact.type.toUpperCase()}
                    </Badge>
                    <span className='text-xs text-muted-foreground'>
                      {artifact.size}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className='pt-0'>
                  <div className='space-y-2'>
                    <p className='text-sm text-muted-foreground'>
                      {artifact.stepName}
                    </p>
                    {artifact.description && (
                      <p className='text-xs text-muted-foreground line-clamp-2'>
                        {artifact.description}
                      </p>
                    )}
                    <div className='flex items-center justify-between text-xs text-muted-foreground'>
                      <div className='flex items-center'>
                        <Calendar className='w-3 h-3 mr-1' />
                        {formatDate(artifact.generatedAt)}
                      </div>
                      <div className='flex items-center'>
                        <HardDrive className='w-3 h-3 mr-1' />
                        {artifact.size}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className='space-y-2'>
            {filteredArtifacts.map((artifact) => (
              <Card
                key={artifact.id}
                className='border-border bg-card hover:bg-card/80 transition-colors'
              >
                <CardContent className='py-4'>
                  <div className='flex items-center justify-between'>
                    <div className='flex items-center space-x-4'>
                      <Checkbox
                        checked={selectedArtifacts.includes(artifact.id)}
                        onCheckedChange={() =>
                          handleSelectArtifact(artifact.id)
                        }
                      />
                      <div className='flex items-center space-x-3'>
                        {getArtifactIcon(artifact.type)}
                        <div>
                          <p className='font-medium text-foreground'>
                            {artifact.filename}
                          </p>
                          <p className='text-sm text-muted-foreground'>
                            {artifact.stepName}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className='flex items-center space-x-4'>
                      <Badge className={getTypeColor(artifact.type)}>
                        {artifact.type.toUpperCase()}
                      </Badge>
                      <span className='text-sm text-muted-foreground'>
                        {artifact.size}
                      </span>
                      <span className='text-sm text-muted-foreground'>
                        {formatDate(artifact.generatedAt)}
                      </span>
                      <div className='flex items-center space-x-2'>
                        {artifact.previewUrl && (
                          <Button
                            variant='ghost'
                            size='sm'
                            onClick={() => handlePreview(artifact)}
                          >
                            <Eye className='w-4 h-4' />
                          </Button>
                        )}
                        <Button variant='ghost' size='sm'>
                          <Download className='w-4 h-4' />
                        </Button>
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
                            <DropdownMenuItem
                              onClick={() =>
                                navigator.clipboard.writeText(artifact.filename)
                              }
                            >
                              <Copy className='w-4 h-4 mr-2' />
                              Copy name
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <ExternalLink className='w-4 h-4 mr-2' />
                              Open in new tab
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Preview Dialog */}
      <Dialog
        open={!!previewArtifact}
        onOpenChange={() => setPreviewArtifact(null)}
      >
        <DialogContent className='max-w-4xl max-h-[80vh] bg-card border-border'>
          <DialogHeader>
            <DialogTitle className='text-foreground flex items-center space-x-2'>
              {previewArtifact && getArtifactIcon(previewArtifact.type)}
              <span>{previewArtifact?.filename}</span>
              <Badge
                className={
                  previewArtifact ? getTypeColor(previewArtifact.type) : ''
                }
              >
                {previewArtifact?.type.toUpperCase()}
              </Badge>
            </DialogTitle>
          </DialogHeader>
          <div className='mt-4'>
            {previewArtifact?.type === 'image' ? (
              <div className='flex items-center justify-center bg-muted rounded-lg p-8'>
                <div className='text-center'>
                  <ImageIcon className='w-16 h-16 text-muted-foreground mx-auto mb-4' />
                  <p className='text-muted-foreground'>
                    Image preview would appear here
                  </p>
                </div>
              </div>
            ) : (
              <div className='bg-muted rounded-lg p-4 max-h-96 overflow-auto'>
                <pre className='text-sm text-foreground whitespace-pre-wrap font-mono'>
                  {previewContent}
                </pre>
              </div>
            )}
            <div className='flex items-center justify-between mt-4 pt-4 border-t border-border'>
              <div className='text-sm text-muted-foreground'>
                Generated by {previewArtifact?.stepName} •{' '}
                {previewArtifact?.size} •{' '}
                {previewArtifact && formatDate(previewArtifact.generatedAt)}
              </div>
              <Button>
                <Download className='w-4 h-4 mr-2' />
                Download
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
