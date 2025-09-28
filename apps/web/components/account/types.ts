export type AccountUser = {
  id: string;
  email: string;
  name?: string | null;
  role: 'admin' | 'user';
};
