import type { Metadata } from 'next';
import LoginWithApi from './with-api';

export const metadata: Metadata = {
  title: 'Login',
};

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ redirect?: string }>;
}) {
  const sp = await searchParams;
  const redirectTo = sp?.redirect ?? '/flows';
  return <LoginWithApi redirectTo={redirectTo} />;
}
