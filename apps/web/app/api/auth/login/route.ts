import { NextRequest, NextResponse } from 'next/server';
import { createUnauthenticatedClient } from '@/lib/api';
import { parseSetCookieHeader } from '@/lib/cookies';
import { loginApiV1AuthLoginPost } from '@yeetflow/api-client';

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

    const nextResponse = NextResponse.json(response.data);
    const setCookieHeaders = response.response.headers.getSetCookie();

    const proto = request.headers.get('x-forwarded-proto');
    const isSecureRequest =
      proto === 'https' || request.nextUrl.protocol === 'https:';

    if (isSecureRequest) {
      setCookieHeaders.forEach((cookieHeader) => {
        nextResponse.headers.append('Set-Cookie', cookieHeader);
      });
    } else {
      setCookieHeaders.forEach((cookieHeader) => {
        const parsed = parseSetCookieHeader(cookieHeader, isSecureRequest);
        if (parsed) {
          nextResponse.cookies.set(parsed.name, parsed.value, parsed.options);
        }
      });
    }

    return nextResponse;
  } catch (err: any) {
    const detail = err.response?.data?.detail || 'Authentication failed';
    return NextResponse.json(
      { detail },
      { status: err.response?.status || 401 },
    );
  }
}
