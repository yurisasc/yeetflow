'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; reset: () => void }>;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return (
        <FallbackComponent
          error={this.state.error}
          reset={() => this.setState({ hasError: false, error: undefined })}
        />
      );
    }

    return this.props.children;
  }
}

function DefaultErrorFallback({
  error,
  reset,
}: {
  error?: Error;
  reset: () => void;
}) {
  return (
    <div className='min-h-[400px] flex items-center justify-center p-4'>
      <Card className='border-border bg-card max-w-md w-full'>
        <CardHeader className='text-center space-y-2'>
          <div className='w-12 h-12 bg-destructive/10 rounded-full flex items-center justify-center mx-auto mb-2'>
            <AlertTriangle className='w-6 h-6 text-destructive' />
          </div>
          <CardTitle className='text-lg'>Something went wrong</CardTitle>
          <CardDescription>
            This component encountered an error. Please try refreshing or
            contact support.
          </CardDescription>
        </CardHeader>
        <CardContent className='text-center'>
          <Button onClick={reset} className='bg-primary hover:bg-primary/90'>
            <RefreshCw className='w-4 h-4 mr-2' />
            Try Again
          </Button>
          {error && (
            <details className='mt-4 text-left'>
              <summary className='text-sm text-muted-foreground cursor-pointer hover:text-foreground'>
                Error Details
              </summary>
              <pre className='mt-2 text-xs bg-muted p-2 rounded overflow-auto'>
                {error.message}
              </pre>
            </details>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
