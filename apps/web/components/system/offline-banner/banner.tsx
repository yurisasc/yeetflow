import React from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { WifiOff, Wifi, X } from 'lucide-react';

export function OfflineBanner({
  isOnline,
  onDismiss,
}: {
  isOnline: boolean;
  onDismiss: () => void;
}) {
  return (
    <div
      className='fixed top-0 left-0 right-0 z-50'
      aria-live='polite'
      aria-atomic='true'
    >
      <Alert className='rounded-none border-x-0 border-t-0 bg-yellow-500/10 border-yellow-500/20'>
        <WifiOff className='h-4 w-4 text-yellow-400' />
        <AlertDescription className='flex items-center justify-between'>
          <span className='text-yellow-400' aria-live='polite'>
            You're currently offline. Some features may not work properly.
          </span>
          <div className='flex items-center space-x-2'>
            {isOnline && (
              <div className='flex items-center text-green-400 text-sm'>
                <Wifi className='w-4 h-4 mr-1' />
                Reconnected
              </div>
            )}
            <Button
              variant='ghost'
              size='sm'
              onClick={onDismiss}
              aria-label='Dismiss offline banner'
              className='h-6 w-6 p-0 text-yellow-400 hover:text-yellow-300'
            >
              <X className='h-4 w-4' />
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    </div>
  );
}
