import React from 'react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Copy, Eye, ExternalLink, MoreHorizontal } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { RunListItem } from './types';
import { formatDate, getArtifactIcon, getStatusColor } from './utils';

export type RunsTableListProps = {
  runs: RunListItem[];
  onCopyId: (text: string) => void;
  onCopyLink: (runId: string) => void;
};

export function RunsTableList({
  runs,
  onCopyId,
  onCopyLink,
}: RunsTableListProps) {
  return (
    <div className='border border-border rounded-lg bg-card'>
      <Table>
        <TableHeader>
          <TableRow className='border-border'>
            <TableHead className='text-foreground'>Status</TableHead>
            <TableHead className='text-foreground'>Flow</TableHead>
            <TableHead className='text-foreground'>Run ID</TableHead>
            <TableHead className='text-foreground'>Started</TableHead>
            <TableHead className='text-foreground'>Duration</TableHead>
            <TableHead className='text-foreground'>Artifacts</TableHead>
            <TableHead className='text-foreground'>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {runs.map((run) => (
            <TableRow key={run.id} className='border-border hover:bg-muted/50'>
              <TableCell>
                <Badge className={getStatusColor(run.status)}>
                  {run.status.replaceAll('_', ' ')}
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
                    onClick={() => onCopyId(run.id)}
                    aria-label='Copy run ID'
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
                  <span className='text-muted-foreground text-sm'>None</span>
                )}
              </TableCell>
              <TableCell>
                <div className='flex items-center space-x-2'>
                  <Button
                    asChild
                    variant='ghost'
                    size='sm'
                    aria-label='View run'
                  >
                    <Link href={`/runs/${run.id}`}>
                      <Eye className='w-4 h-4' />
                    </Link>
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant='ghost'
                        size='sm'
                        aria-label='More actions'
                      >
                        <MoreHorizontal className='w-4 h-4' />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent
                      align='end'
                      className='bg-popover border-border'
                    >
                      <DropdownMenuItem asChild>
                        <Link
                          href={`/runs/${run.id}`}
                          target='_blank'
                          rel='noopener noreferrer'
                        >
                          <ExternalLink className='w-4 h-4 mr-2' />
                          Open in new tab
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem onSelect={() => onCopyId(run.id)}>
                        <Copy className='w-4 h-4 mr-2' />
                        Copy ID
                      </DropdownMenuItem>
                      <DropdownMenuItem onSelect={() => onCopyLink(run.id)}>
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
  );
}
