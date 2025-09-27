import { NextRequest, NextResponse } from 'next/server';
import { createUnauthenticatedClient } from '@/lib/api';
import { loginApiV1AuthLoginPost, type Token } from '@yeetflow/api-client';

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return NextResponse.json(
        { detail: 'Email and password are required' },
        { status: 400 },
      );
    }

    const client = createUnauthenticatedClient();

    const response = await loginApiV1AuthLoginPost({
      client,
      body: {
        grant_type: 'password',
        username: email,
        password,
      },
      throwOnError: true,
    });

    // Forward cookies from worker to browser
    const nextResponse = NextResponse.json(response.data);
    const setCookieHeaders = response.response.headers.getSetCookie();
    setCookieHeaders.forEach((cookie) => {
      const [name, value] = cookie.split(';')[0].split('=');
      nextResponse.cookies.set(name, value);
    });

    return nextResponse;
  } catch (err: any) {
    const detail = err.response?.data?.detail || 'Authentication failed';
    return NextResponse.json(
      { detail },
      { status: err.response?.status || 401 },
    );
  }
}
