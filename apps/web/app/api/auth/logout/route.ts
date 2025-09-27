import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST() {
  const cookieStore = await cookies();
  cookieStore.set('access_token', '', { httpOnly: true, path: '/', maxAge: 0 });
  cookieStore.set('refresh_token', '', {
    httpOnly: true,
    path: '/',
    maxAge: 0,
  });
  return NextResponse.json({ ok: true });
}
