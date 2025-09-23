'use client';

import type React from 'react';

import { useState } from 'react';
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
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Zap } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Simulate JWT authentication
      await new Promise((resolve) => setTimeout(resolve, 1000));

      if (email === 'demo@yeetflow.com' && password === 'demo123') {
        // Store JWT token (in real app, this would come from API)
        localStorage.setItem('yeetflow_token', 'mock-jwt-token');
        router.push('/flows');
      } else {
        setError('Invalid credentials. Try demo@yeetflow.com / demo123');
      }
    } catch (err) {
      setError('Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='min-h-screen flex items-center justify-center bg-background p-4'>
      <div className='w-full max-w-md space-y-8'>
        {/* Brand Area */}
        <div className='text-center space-y-2'>
          <div className='flex items-center justify-center space-x-2'>
            <div className='w-8 h-8 bg-primary rounded-lg flex items-center justify-center'>
              <Zap className='w-5 h-5 text-primary-foreground' />
            </div>
            <h1 className='text-2xl font-bold text-foreground'>YeetFlow</h1>
          </div>
          <p className='text-muted-foreground'>
            Automation platform with human-in-the-loop
          </p>
        </div>

        {/* Login Card */}
        <Card className='border-border bg-card'>
          <CardHeader className='space-y-1'>
            <CardTitle className='text-xl text-center'>
              Sign in to your account
            </CardTitle>
            <CardDescription className='text-center'>
              Enter your credentials to access your flows
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className='space-y-4'>
              <div className='space-y-2'>
                <Label htmlFor='email'>Email</Label>
                <Input
                  id='email'
                  type='email'
                  placeholder='Enter your email'
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className='bg-input border-border'
                />
              </div>

              <div className='space-y-2'>
                <Label htmlFor='password'>Password</Label>
                <Input
                  id='password'
                  type='password'
                  placeholder='Enter your password'
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className='bg-input border-border'
                />
              </div>

              {error && (
                <Alert variant='destructive'>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button type='submit' className='w-full' disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                    Signing in...
                  </>
                ) : (
                  'Sign in'
                )}
              </Button>
            </form>

            <div className='mt-4 text-center'>
              <button className='text-sm text-primary hover:underline'>
                Forgot your password?
              </button>
            </div>

            <div className='mt-6 p-3 bg-muted rounded-lg'>
              <p className='text-xs text-muted-foreground text-center'>
                Demo credentials: demo@yeetflow.com / demo123
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
