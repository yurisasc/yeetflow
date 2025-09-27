'use server';

import { z } from 'zod';
import { redirect } from 'next/navigation';
import { createAPIClient } from '@/lib/api';
import { createRunApiV1RunsPost } from '@yeetflow/api-client';

export type StartFlowResult = { success: false; error: string };

const StartFlowSchema = z.object({
  flow_id: z.string().min(1, 'flow_id is required'),
});

// Server action compatible with useFormState. It ignores prevState and either
// redirects on success or returns an error object for client display.
export type StartFlowFormState = { error: string | null };

export async function startFlowFormAction(
  _prevState: StartFlowFormState,
  formData: FormData,
): Promise<StartFlowFormState> {
  try {
    const parsed = StartFlowSchema.safeParse({
      flow_id: formData.get('flow_id'),
    });

    if (!parsed.success) {
      return { error: 'Invalid flow selection. Please try again.' };
    }

    const client = createAPIClient();
    const res = await createRunApiV1RunsPost({
      client,
      body: { flow_id: parsed.data.flow_id },
      throwOnError: true,
    });

    redirect(`/runs/${res.data!.id}`);
  } catch (error) {
    // Allow Next.js to handle redirect errors
    if (
      typeof error === 'object' &&
      error !== null &&
      'digest' in (error as any) &&
      typeof (error as any).digest === 'string' &&
      (error as any).digest.startsWith('NEXT_REDIRECT')
    ) {
      throw error as Error;
    }
    console.error('Failed to start flow (form action):', error);
    return { error: 'Failed to start the flow. Please try again.' };
  }
}
