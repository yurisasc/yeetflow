import React from 'react';
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
import { Loader2 } from 'lucide-react';

export type LoginFormProps = {
  email: string;
  password: string;
  isLoading: boolean;
  error?: string | null;
  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onSubmit: () => void;
};

export function LoginForm({
  email,
  password,
  isLoading,
  error,
  onEmailChange,
  onPasswordChange,
  onSubmit,
}: LoginFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) {
      return;
    }
    onSubmit();
  };

  return (
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
              onChange={(e) => onEmailChange(e.target.value)}
              required
              className='bg-input border-border'
              data-testid='email-input'
              name='email'
              autoComplete='username'
              autoCapitalize='none'
              autoCorrect='off'
              inputMode='email'
              spellCheck={false}
            />
          </div>

          <div className='space-y-2'>
            <Label htmlFor='password'>Password</Label>
            <Input
              id='password'
              type='password'
              placeholder='Enter your password'
              value={password}
              onChange={(e) => onPasswordChange(e.target.value)}
              required
              className='bg-input border-border'
              data-testid='password-input'
              name='password'
              autoComplete='current-password'
              spellCheck={false}
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
      </CardContent>
    </Card>
  );
}
