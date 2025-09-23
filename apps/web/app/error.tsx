'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  AlertTriangle,
  RefreshCw,
  Home,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useState } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className='min-h-screen bg-background flex items-center justify-center p-4'>
      <div className='w-full max-w-lg space-y-6'>
        <Card className='border-border bg-card'>
          <CardHeader className='text-center space-y-2'>
            <div className='w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mx-auto mb-4'>
              <AlertTriangle className='w-8 h-8 text-destructive' />
            </div>
            <CardTitle className='text-2xl'>Something went wrong</CardTitle>
            <CardDescription>
              An unexpected error occurred. Please try again or contact support
              if the problem persists.
            </CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='grid grid-cols-1 sm:grid-cols-2 gap-3'>
              <Button
                onClick={reset}
                className='bg-primary hover:bg-primary/90'
              >
                <RefreshCw className='w-4 h-4 mr-2' />
                Try Again
              </Button>
              <Button
                variant='outline'
                onClick={() => (window.location.href = '/flows')}
                className='border-border'
              >
                <Home className='w-4 h-4 mr-2' />
                Go Home
              </Button>
            </div>

            {/* Error Details Toggle */}
            <div className='border-t border-border pt-4'>
              <Button
                variant='ghost'
                onClick={() => setShowDetails(!showDetails)}
                className='w-full justify-between p-0 h-auto text-sm text-muted-foreground hover:text-foreground'
              >
                Technical Details
                {showDetails ? (
                  <ChevronUp className='w-4 h-4' />
                ) : (
                  <ChevronDown className='w-4 h-4' />
                )}
              </Button>

              {showDetails && (
                <div className='mt-3 p-3 bg-muted rounded-lg'>
                  <div className='space-y-2 text-sm'>
                    <div>
                      <span className='font-medium text-foreground'>
                        Error:
                      </span>
                      <p className='text-muted-foreground font-mono text-xs mt-1 break-all'>
                        {error.message}
                      </p>
                    </div>
                    {error.digest && (
                      <div>
                        <span className='font-medium text-foreground'>
                          Error ID:
                        </span>
                        <p className='text-muted-foreground font-mono text-xs mt-1'>
                          {error.digest}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
