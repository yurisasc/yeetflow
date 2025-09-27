'use client';

import React, { useState, useTransition } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import SignupLayout from '@/components/auth/signup/page';

export default function SignupWithApi({ redirectTo }: { redirectTo?: string }) {
  const router = useRouter();
  const search = useSearchParams();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const onSubmit = () => {
    setError(null);
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    startTransition(async () => {
      try {
        const regRes = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ name, email, password }),
        });
        if (!regRes.ok) {
          let detail = 'Registration failed';
          try {
            const data = await regRes.json();
            if (data?.detail) detail = data.detail;
          } catch {}
          setError(detail);
          return;
        }
        const loginRes = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email, password }),
        });
        if (!loginRes.ok) {
          let detail = 'Login failed after registration';
          try {
            const data = await loginRes.json();
            if (data?.detail) detail = data.detail;
          } catch {}
          setError(detail);
          return;
        }
        const next = redirectTo || search.get('redirect') || '/flows';
        router.push(next);
      } catch (err) {
        console.error('Signup failed:', err);
        setError('Registration failed');
      }
    });
  };

  return (
    <SignupLayout
      name={name}
      email={email}
      password={password}
      confirmPassword={confirmPassword}
      isLoading={isPending}
      error={error}
      onNameChange={setName}
      onEmailChange={setEmail}
      onPasswordChange={setPassword}
      onConfirmPasswordChange={setConfirmPassword}
      onSubmit={onSubmit}
    />
  );
}
