'use client';

import type React from 'react';
import { AuthGuard } from '@/components/auth-guard';
import { ErrorBoundary } from '@/components/error-boundary';
import { OfflineBanner } from '@/components/offline-banner';
import { Sidebar } from '@/components/ui/sidebar';
import { MobileNav } from '@/components/ui/mobile-nav';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bell } from 'lucide-react';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <ErrorBoundary>
        <div className='min-h-screen bg-background'>
          <OfflineBanner />

          <div className='flex h-screen'>
            {/* Desktop Sidebar */}
            <div className='hidden md:flex'>
              <Sidebar />
            </div>

            {/* Main Content Area */}
            <div className='flex-1 flex flex-col overflow-hidden'>
              {/* Mobile Header */}
              <header className='md:hidden sticky top-0 z-40 border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60'>
                <div className='flex h-16 items-center justify-between px-4'>
                  <MobileNav />

                  {/* Mobile Notifications */}
                  <Button variant='ghost' size='sm' className='relative'>
                    <Bell className='w-4 h-4' />
                    <Badge className='absolute -top-1 -right-1 w-2 h-2 p-0 bg-red-500 text-white'>
                      <span className='sr-only'>New notifications</span>
                    </Badge>
                  </Button>
                </div>
              </header>

              {/* Page Content */}
              <main className='flex-1 overflow-auto'>{children}</main>
            </div>
          </div>
        </div>
      </ErrorBoundary>
    </AuthGuard>
  );
}
