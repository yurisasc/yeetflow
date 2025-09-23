'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Home, ArrowLeft, Zap } from 'lucide-react';

export default function NotFound() {
  return (
    <div className='min-h-screen bg-background flex items-center justify-center p-4'>
      <div className='w-full max-w-md space-y-8'>
        {/* Brand Area */}
        <div className='text-center space-y-2'>
          <div className='flex items-center justify-center space-x-2'>
            <div className='w-8 h-8 bg-primary rounded-lg flex items-center justify-center'>
              <Zap className='w-5 h-5 text-primary-foreground' />
            </div>
            <h1 className='text-2xl font-bold text-foreground'>YeetFlow</h1>
          </div>
        </div>

        {/* 404 Card */}
        <Card className='border-border bg-card'>
          <CardHeader className='text-center space-y-2'>
            <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
              <span className='text-2xl font-bold text-muted-foreground'>
                404
              </span>
            </div>
            <CardTitle className='text-2xl'>Page not found</CardTitle>
            <CardDescription>
              The page you're looking for doesn't exist or has been moved.
            </CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='grid grid-cols-1 gap-3'>
              <Link href='/flows'>
                <Button className='w-full bg-primary hover:bg-primary/90'>
                  <Home className='w-4 h-4 mr-2' />
                  Go to Flows
                </Button>
              </Link>
              <Button
                variant='outline'
                onClick={() => window.history.back()}
                className='w-full border-border'
              >
                <ArrowLeft className='w-4 h-4 mr-2' />
                Go Back
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
