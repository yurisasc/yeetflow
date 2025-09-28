'use server';

import { z } from 'zod';
import { createAPIClient } from '@/lib/api';
import { updateUserRoleApiV1AuthUsersUserIdRolePatch } from '@yeetflow/api-client';

const UpdateUserRoleSchema = z.object({
  userId: z.string().min(1, 'User ID is required'),
  role: z.enum(['admin', 'user']),
});

export type UpdateUserRoleResult =
  | { success: true }
  | { success: false; error: string };

export async function updateUserRoleAction(
  input: z.infer<typeof UpdateUserRoleSchema>,
): Promise<UpdateUserRoleResult> {
  const parsed = UpdateUserRoleSchema.safeParse(input);
  if (!parsed.success) {
    return {
      success: false,
      error: parsed.error.errors[0]?.message ?? 'Invalid role update payload.',
    };
  }

  try {
    const client = createAPIClient();
    await updateUserRoleApiV1AuthUsersUserIdRolePatch({
      client,
      path: { user_id: parsed.data.userId },
      body: { new_role: parsed.data.role },
      throwOnError: true,
    });

    return { success: true };
  } catch (error: any) {
    const detailMessage =
      error?.response?.data?.detail ??
      error?.response?.data?.error ??
      error?.message ??
      'Failed to update user role.';
    return { success: false, error: detailMessage };
  }
}
