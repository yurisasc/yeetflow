import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Shield, LogIn, Zap } from 'lucide-react';

export default function UnauthorizedPage() {
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

        {/* Unauthorized Card */}
        <Card className='border-border bg-card'>
          <CardHeader className='text-center space-y-2'>
            <div className='w-16 h-16 bg-yellow-500/10 rounded-full flex items-center justify-center mx-auto mb-4'>
              <Shield className='w-8 h-8 text-yellow-400' />
            </div>
            <CardTitle className='text-2xl'>Access Required</CardTitle>
            <CardDescription>
              You need to sign in to access this page. Please log in with your
              YeetFlow account.
            </CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <Link href='/login'>
              <Button className='w-full bg-primary hover:bg-primary/90'>
                <LogIn className='w-4 h-4 mr-2' />
                Sign In
              </Button>
            </Link>

            <div className='mt-4 text-center text-sm text-muted-foreground'>
              Don't have an account? Contact your administrator.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
