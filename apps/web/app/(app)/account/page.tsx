import { createAPIClient } from '@/lib/api';
import {
  getCurrentUserInfoApiV1AuthMeGet,
  type UserRead,
} from '@yeetflow/api-client';
import AccountWithAuth from './with-auth';

export default async function AccountPage() {
  const client = createAPIClient();
  const response = await getCurrentUserInfoApiV1AuthMeGet({
    client,
    throwOnError: true,
  });
  const user = response.data as UserRead;

  return <AccountWithAuth user={user} />;
}
