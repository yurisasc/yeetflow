'use client';

import React, { useState, useTransition } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import LoginLayout from '@/components/auth/login/page';

export default function LoginWithApi({ redirectTo }: { redirectTo: string }) {
  const router = useRouter();
  const search = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const onSubmit = () => {
    setError(null);
    startTransition(async () => {
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          let detail = 'Authentication failed';
          try {
            const data = await res.json();
            if (data?.detail) detail = data.detail;
          } catch {}
          setError(detail);
          return;
        }
        const next = redirectTo || search.get('redirect') || '/flows';
        router.push(next);
      } catch (err) {
        console.error('Login failed:', err);
        setError('Authentication failed');
      }
    });
  };

  return (
    <LoginLayout
      email={email}
      password={password}
      isLoading={isPending}
      error={error}
      onEmailChange={setEmail}
      onPasswordChange={setPassword}
      onSubmit={onSubmit}
    />
  );
}
