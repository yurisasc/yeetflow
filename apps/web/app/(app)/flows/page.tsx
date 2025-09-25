'use client';

import type React from 'react';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Search, Play, FileText } from 'lucide-react';
import { getAuthHeader } from '@/lib/auth';

interface Flow {
  id: string;
  name: string;
  description: string;
  key: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  config: Record<string, any>;
}

export default function FlowsPage() {
  const [flows, setFlows] = useState<Flow[]>([]);
  const [filteredFlows, setFilteredFlows] = useState<Flow[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [startingFlowIds, setStartingFlowIds] = useState<Set<string>>(
    new Set(),
  );
  const [startFlowError, setStartFlowError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchFlows();
  }, []);

  const fetchFlows = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/worker/api/v1/flows', {
        headers: {
          ...getAuthHeader(),
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch flows');
      }

      const data = await response.json();
      const flowsData = data.flows || [];

      const mappedFlows = flowsData.map((flow: any) => ({
        id: flow.id,
        name: flow.name,
        description: flow.description || 'No description provided',
        key: flow.key,
        created_by: flow.created_by,
        created_at: flow.created_at,
        updated_at: flow.updated_at,
        config: flow.config || {},
      }));

      setFlows(mappedFlows);
      setFilteredFlows(mappedFlows);
    } catch (error) {
      console.error('Error fetching flows:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let filtered = flows;

    if (searchQuery) {
      filtered = filtered.filter(
        (flow) =>
          flow.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          flow.description.toLowerCase().includes(searchQuery.toLowerCase()),
      );
    }

    setFilteredFlows(filtered);
  }, [flows, searchQuery]);

  const handleStartFlow = async (flowId: string) => {
    if (startingFlowIds.has(flowId)) {
      return;
    }

    setStartFlowError(null);
    setStartingFlowIds((prev) => new Set(prev).add(flowId));
    try {
      const response = await fetch('/api/worker/api/v1/runs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
        body: JSON.stringify({ flow_id: flowId }),
      });

      if (!response.ok) {
        let message = 'Failed to create run';
        try {
          const errorBody = await response.json();
          message = errorBody?.detail ?? message;
        } catch {
          // no-op: fallback to default message
        }

        throw new Error(message);
      }

      const data = await response.json();
      setStartFlowError(null);
      router.push(`/runs/${data.id}`);
    } catch (error) {
      console.error('Error starting flow:', error);
      const message =
        error instanceof Error ? error.message : 'Failed to create run';
      setStartFlowError(message);
    } finally {
      setStartingFlowIds((prev) => {
        const next = new Set(prev);
        next.delete(flowId);
        return next;
      });
    }
  };

  return (
    <div className='min-h-screen bg-background' data-testid='flows-list'>
      {/* Header */}
      <div className='border-b border-border bg-card/50'>
        <div className='container mx-auto px-6 py-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold text-foreground'>Flows</h1>
              <p className='text-muted-foreground mt-1'>
                Discover and start automation workflows
              </p>
            </div>
            <div className='relative'>
              <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
              <Input
                placeholder='Search flows...'
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className='pl-10 w-80 bg-input border-border'
              />
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className='container mx-auto px-6 py-8'>
        {startFlowError && (
          <div
            data-testid='start-flow-error'
            className='mb-6 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive'
            role='alert'
          >
            {startFlowError}
          </div>
        )}

        {isLoading ? (
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className='border-border bg-card'>
                <CardHeader>
                  <Skeleton className='h-6 w-3/4' />
                  <Skeleton className='h-4 w-full' />
                </CardHeader>
                <CardContent>
                  <Skeleton className='h-9 w-full' />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredFlows.length === 0 ? (
          <div className='text-center py-16'>
            <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
              <Search className='w-8 h-8 text-muted-foreground' />
            </div>
            <h3 className='text-lg font-semibold text-foreground mb-2'>
              No flows found
            </h3>
            <p className='text-muted-foreground mb-4'>
              Try adjusting your search
            </p>
            <Button
              variant='outline'
              onClick={() => setSearchQuery('')}
              className='border-border'
            >
              Clear search
            </Button>
          </div>
        ) : (
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {filteredFlows.map((flow) => (
              <Card
                key={flow.id}
                className='border-border bg-card hover:bg-card/80 transition-colors group'
                data-testid='flow-card'
              >
                <CardHeader className='pb-3'>
                  <div className='flex items-start justify-between'>
                    <div className='flex items-center space-x-3'>
                      <div className='w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center text-primary'>
                        <FileText className='w-5 h-5' />
                      </div>
                      <div>
                        <CardTitle
                          className='text-lg text-foreground group-hover:text-primary transition-colors'
                          data-testid='flow-name'
                        >
                          {flow.name}
                        </CardTitle>
                      </div>
                    </div>
                  </div>
                  <CardDescription
                    className='text-muted-foreground leading-relaxed'
                    data-testid='flow-description'
                  >
                    {flow.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className='pt-0'>
                  <div className='flex items-center justify-end'>
                    <Button
                      onClick={() => handleStartFlow(flow.id)}
                      className='bg-primary hover:bg-primary/90 text-primary-foreground hover:cursor-pointer'
                      data-testid='start-flow-button'
                      disabled={startingFlowIds.has(flow.id)}
                    >
                      {startingFlowIds.has(flow.id) ? (
                        <>
                          <span className='mr-2 inline-flex h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent align-[-0.125em]' />
                          Starting...
                        </>
                      ) : (
                        <>
                          <Play className='w-4 h-4 mr-2' />
                          Start Flow
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
