'use client';

import type React from 'react';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
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
import { setToken, setRefreshToken } from '@/lib/auth';
import { useCSRF } from '@/lib/csrf';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const { token: csrfToken } = useCSRF();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('grant_type', 'password');
      formData.append('username', email);
      formData.append('password', password);
      // Include CSRF token for future server-side validation
      if (csrfToken) {
        formData.append('csrf_token', csrfToken);
      }

      const response = await fetch('/api/worker/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Authentication failed');
      }

      const data = await response.json();
      setToken(data.access_token);
      if (data.refresh_token) {
        setRefreshToken(data.refresh_token);
      }
      router.push('/flows');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
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
            <form
              onSubmit={handleSubmit}
              className='space-y-4'
              data-testid='login-form'
            >
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
                  data-testid='email-input'
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
                  data-testid='password-input'
                />
              </div>

              {error && (
                <Alert variant='destructive' data-testid='login-error'>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button
                type='submit'
                className='w-full'
                disabled={isLoading}
                data-testid='login-submit'
              >
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

            <div className='mt-4 text-center space-y-2'>
              <Link
                href='/signup'
                className='text-sm text-primary hover:underline'
              >
                Don't have an account? Sign up
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
