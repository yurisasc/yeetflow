import React from 'react';
import Link from 'next/link';
import { LoginHeader } from './header';
import { LoginForm, type LoginFormProps } from './form';

export type LoginLayoutProps = LoginFormProps;

export default function LoginLayout(props: LoginLayoutProps) {
  return (
    <div className='min-h-screen flex items-center justify-center bg-background p-4'>
      <div className='w-full max-w-md space-y-8'>
        <LoginHeader />

        <LoginForm {...props} />

        <div className='mt-4 text-center space-y-2'>
          <Link href='/signup' className='text-sm text-primary hover:underline'>
            Don't have an account? Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
