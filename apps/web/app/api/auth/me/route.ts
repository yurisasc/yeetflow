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
    return NextResponse.json(user);
  } catch (err: any) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }
}
