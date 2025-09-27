export type UserData = {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  status: 'active' | 'inactive' | 'pending';
  lastLogin: string; // ISO or 'Never'
  createdAt: string; // ISO
  runsCount: number;
};

export type FilterOption = {
  value: string;
  label: string;
};
