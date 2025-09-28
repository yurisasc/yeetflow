import React from 'react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Archive, Download, Eye } from 'lucide-react';
import type { RunListItem } from './types';
import { formatDate, getArtifactIcon, getStatusColor } from './utils';

export type RunsCardsListProps = {
  runs: RunListItem[];
};

export function RunsCardsList({ runs }: RunsCardsListProps) {
  return (
    <div className='space-y-4'>
      {runs.map((run) => (
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
                  {run.status.replaceAll('_', ' ')}
                </Badge>
              </div>
            </div>
            <CardDescription className='flex items-center space-x-4 text-muted-foreground'>
              <div className='flex items-center'>
                <span className='mr-1'>📅</span>
                {formatDate(run.startedAt)}
              </div>
              <div className='flex items-center'>
                <span className='mr-1'>⏱️</span>
                {run.duration}
              </div>
              {run.currentStep && (
                <div className='text-sm'>Current: {run.currentStep}</div>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent className='pt-0'>
            <div className='flex items-center justify-between'>
              <div className='flex-1 mr-4'>
                <div className='flex justify-between text-sm mb-1'>
                  <span className='text-muted-foreground'>Progress</span>
                  <span className='text-foreground'>{run.progress}%</span>
                </div>
                <div className='w-full bg-secondary rounded-full h-2'>
                  <div
                    className='bg-primary h-2 rounded-full transition-all'
                    style={{
                      width: `${Math.max(0, Math.min(100, run.progress))}%`,
                    }}
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
                        <SheetTitle>Artifacts - {run.flowName}</SheetTitle>
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
                              <Button
                                variant='ghost'
                                size='sm'
                                disabled
                                aria-disabled='true'
                                title='Not available'
                              >
                                <Eye className='w-4 h-4' />
                              </Button>
                              <Button
                                variant='ghost'
                                size='sm'
                                disabled
                                aria-disabled='true'
                                title='Not available'
                              >
                                <Download className='w-4 h-4' />
                              </Button>
                            </div>
                          </div>
                        ))}
                        {run.artifacts.length > 1 && (
                          <Button
                            variant='outline'
                            className='w-full border-border bg-transparent'
                            disabled
                            aria-disabled='true'
                            title='Not available'
                          >
                            <Download className='w-4 h-4 mr-2' />
                            Download All
                          </Button>
                        )}
                      </div>
                    </SheetContent>
                  </Sheet>
                )}
                <Button
                  asChild
                  variant='outline'
                  className='border-border bg-transparent'
                >
                  <Link href={`/runs/${run.id}`}>
                    <Eye className='w-4 h-4 mr-2' />
                    View Details
                  </Link>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
