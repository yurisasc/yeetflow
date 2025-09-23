'use client';

import { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { WifiOff, Wifi, X } from 'lucide-react';

export function OfflineBanner() {
  const [isOnline, setIsOnline] = useState(true);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowBanner(false);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowBanner(true);
    };

    // Set initial state
    setIsOnline(navigator.onLine);
    if (!navigator.onLine) {
      setShowBanner(true);
    }

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!showBanner) return null;

  return (
    <div className='fixed top-0 left-0 right-0 z-50'>
      <Alert className='rounded-none border-x-0 border-t-0 bg-yellow-500/10 border-yellow-500/20'>
        <WifiOff className='h-4 w-4 text-yellow-400' />
        <AlertDescription className='flex items-center justify-between'>
          <span className='text-yellow-400'>
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
              onClick={() => setShowBanner(false)}
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
