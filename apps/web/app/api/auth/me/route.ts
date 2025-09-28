import { NextResponse } from 'next/server';
import { getCurrentUserInfoApiV1AuthMeGet } from '@yeetflow/api-client';
import { createAPIClient } from '@/lib/api';

export async function GET() {
  try {
    const client = createAPIClient();
    const response = await getCurrentUserInfoApiV1AuthMeGet({
      client,
      throwOnError: true,
    });

    const user = response.data;
    return NextResponse.json(user, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        Vary: 'Cookie',
      },
    });
  } catch (err: unknown) {
    const status =
      (typeof err === 'object' &&
        err &&
        // @ts-expect-error best-effort extraction from client error
        (err.status || err.response?.status)) ||
      401;
    const message = status === 401 ? 'Unauthorized' : 'Failed to load user';
    return NextResponse.json({ detail: message }, { status });
  }
}
