'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to flows page - authentication is handled by middleware
    router.push('/flows');
  }, [router]);

  return (
    <div className='min-h-screen flex items-center justify-center bg-background'>
      <div className='text-center'>
        <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto'></div>
        <p className='mt-2 text-muted-foreground'>Redirecting...</p>
      </div>
    </div>
  );
}
