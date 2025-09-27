import React from 'react';
import Link from 'next/link';
import { LoginHeader } from '../login/header';
import { SignupForm } from './form';

export type SignupLayoutProps = {
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

export default function SignupLayout(props: SignupLayoutProps) {
  return (
    <div className='min-h-screen flex items-center justify-center bg-background p-4'>
      <div className='w-full max-w-md space-y-8'>
        <LoginHeader />

        <SignupForm
          name={props.name}
          email={props.email}
          password={props.password}
          confirmPassword={props.confirmPassword}
          isLoading={props.isLoading}
          error={props.error}
          onNameChange={props.onNameChange}
          onEmailChange={props.onEmailChange}
          onPasswordChange={props.onPasswordChange}
          onConfirmPasswordChange={props.onConfirmPasswordChange}
          onSubmit={props.onSubmit}
        />

        <div className='mt-4 text-center'>
          <Link href='/login' className='text-sm text-primary hover:underline'>
            Already have an account? Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
