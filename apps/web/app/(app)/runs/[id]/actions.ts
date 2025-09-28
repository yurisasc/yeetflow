'use server';

import { revalidatePath } from 'next/cache';
import { z } from 'zod';
import {
  continueRunApiV1RunsRunIdContinuePost,
  createClient,
} from '@yeetflow/api-client';
import { createAPIClient } from '@/lib/api';

const ContinueSchema = z.object({
  runId: z.string().min(1, 'Run ID is required'),
  notes: z.string().trim().max(2000).optional().or(z.literal('')),
  inputJson: z.string().trim().optional().or(z.literal('')),
});

export type ContinueRunResult =
  | { success: true }
  | { success: false; error: string };

export async function continueWithAIAction(
  input: z.infer<typeof ContinueSchema>,
): Promise<ContinueRunResult> {
  const parsed = ContinueSchema.safeParse(input);
  if (!parsed.success) {
    return {
      success: false,
      error: parsed.error.errors[0]?.message ?? 'Invalid continue payload.',
    };
  }

  const { runId, notes, inputJson } = parsed.data;

  let input_payload: Record<string, unknown> | undefined = undefined;
  if (inputJson && inputJson.length > 0) {
    try {
      const parsedJson = JSON.parse(inputJson);
      if (typeof parsedJson !== 'object' || parsedJson === null) {
        return { success: false, error: 'Input JSON must be an object.' };
      }
      input_payload = parsedJson as Record<string, unknown>;
    } catch (e) {
      return { success: false, error: 'Invalid JSON in advanced input.' };
    }
  }

  // Ensure action is set to "continue" when input_payload is present
  if (input_payload) {
    input_payload = { ...input_payload, action: 'continue' };
  }

  try {
    const client = createAPIClient();

    await continueRunApiV1RunsRunIdContinuePost({
      client,
      path: { run_id: runId },
      body: {
        ...(input_payload ? { input_payload } : {}),
        ...(notes && notes.length > 0 ? { notes } : {}),
      },
      throwOnError: true,
    });

    revalidatePath(`/runs/${runId}`);
    return { success: true };
  } catch (error: any) {
    const detailMessage =
      error?.response?.data?.detail ??
      error?.response?.data?.error ??
      error?.message ??
      'Failed to continue run.';
    return { success: false, error: detailMessage };
  }
}

export async function continueWithAIFormAction(
  formData: FormData,
): Promise<void> {
  const runId = String(formData.get('runId') || '');
  const notes = String(formData.get('notes') || '');
  const inputJson = String(formData.get('inputJson') || '');

  await continueWithAIAction({ runId, notes, inputJson });
}
