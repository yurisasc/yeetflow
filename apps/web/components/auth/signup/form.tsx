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
import { Loader2, UserPlus } from 'lucide-react';

export type SignupFormProps = {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  isLoading: boolean;
  error?: string | null;
  onNameChange: (v: string) => void;
  onEmailChange: (v: string) => void;
  onPasswordChange: (v: string) => void;
  onConfirmPasswordChange: (v: string) => void;
  onSubmit: () => void;
};

export function SignupForm({
  name,
  email,
  password,
  confirmPassword,
  isLoading,
  error,
  onNameChange,
  onEmailChange,
  onPasswordChange,
  onConfirmPasswordChange,
  onSubmit,
}: SignupFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <Card className='border-border bg-card'>
      <CardHeader className='space-y-1'>
        <CardTitle className='text-xl text-center'>
          Create your account
        </CardTitle>
        <CardDescription className='text-center'>
          Join YeetFlow and start building automation workflows
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={handleSubmit}
          className='space-y-4'
          data-testid='signup-form'
        >
          <div className='space-y-2'>
            <Label htmlFor='name'>Full Name</Label>
            <Input
              id='name'
              type='text'
              placeholder='Enter your full name'
              value={name}
              onChange={(e) => onNameChange(e.target.value)}
              required
              className='bg-input border-border'
              data-testid='name-input'
            />
          </div>

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
            />
          </div>

          <div className='space-y-2'>
            <Label htmlFor='password'>Password</Label>
            <Input
              id='password'
              type='password'
              placeholder='Create a password'
              value={password}
              onChange={(e) => onPasswordChange(e.target.value)}
              required
              className='bg-input border-border'
              data-testid='password-input'
            />
          </div>

          <div className='space-y-2'>
            <Label htmlFor='confirmPassword'>Confirm Password</Label>
            <Input
              id='confirmPassword'
              type='password'
              placeholder='Confirm your password'
              value={confirmPassword}
              onChange={(e) => onConfirmPasswordChange(e.target.value)}
              required
              className='bg-input border-border'
              data-testid='confirm-password-input'
            />
          </div>

          {error && (
            <Alert variant='destructive' data-testid='signup-error'>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <Button
            type='submit'
            className='w-full'
            disabled={isLoading}
            data-testid='signup-submit'
          >
            {isLoading ? (
              <>
                <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                Creating account...
              </>
            ) : (
              <>
                <UserPlus className='mr-2 h-4 w-4' />
                Create account
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
