'use client';

import type React from 'react';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import { Loader2 } from 'lucide-react';

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const checkAuth = () => {
      if (!isAuthenticated()) {
        // Store the attempted URL for redirect after login
        if (pathname && pathname !== '/login') {
          sessionStorage.setItem('yeetflow_redirect', pathname);
        }
        router.push('/unauthorized');
      } else {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router, pathname]);

  if (isLoading) {
    return (
      <div className='min-h-screen flex items-center justify-center bg-background'>
        <div className='flex items-center space-x-2'>
          <Loader2 className='h-6 w-6 animate-spin text-primary' />
          <span className='text-muted-foreground'>Loading...</span>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
