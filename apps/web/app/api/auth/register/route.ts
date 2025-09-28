import { NextResponse } from 'next/server';
import {
  registerUserApiV1AuthRegisterPost,
  type UserRead,
} from '@yeetflow/api-client';
import { createUnauthenticatedClient } from '@/lib/api';

export async function POST(req: Request) {
  try {
    const { email, password, name } = await req.json();
    if (!email || !password) {
      return NextResponse.json(
        { detail: 'Email and password are required' },
        { status: 400 },
      );
    }

    const client = createUnauthenticatedClient();

    const response = await registerUserApiV1AuthRegisterPost({
      client,
      body: { email, password, name },
      throwOnError: true,
    });

    const user: UserRead = response.data!;
    return NextResponse.json(user, { status: 201 });
  } catch (err: any) {
    const detail =
      err?.response?.data?.detail ??
      err?.response?.body?.detail ??
      (typeof err === 'string' ? err : err?.message) ??
      'Registration failed';
    const status = err?.response?.status ?? err?.status ?? 500;
    return NextResponse.json({ detail }, { status });
  }
}
