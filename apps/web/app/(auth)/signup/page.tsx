import type { Metadata } from 'next';
import SignupWithApi from './with-api';

export const metadata: Metadata = {
  title: 'Sign up',
};

export default async function SignupPage({
  searchParams,
}: {
  searchParams: Promise<{ redirect?: string }>;
}) {
  const sp = await searchParams;
  const redirectTo = sp?.redirect ?? '/flows';
  return <SignupWithApi redirectTo={redirectTo} />;
}
