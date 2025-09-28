import AdminUsersWithUI from './with-ui';
import type { FilterOption, UserData } from '@/components/admin/users/types';

const mockUsers: UserData[] = [
  {
    id: '1',
    name: 'Demo User',
    email: 'demo@yeetflow.com',
    role: 'admin',
    status: 'active',
    lastLogin: '2025-01-23T14:30:00Z',
    createdAt: '2025-01-01T00:00:00Z',
    runsCount: 45,
  },
  {
    id: '2',
    name: 'Sarah Johnson',
    email: 'sarah.johnson@company.com',
    role: 'user',
    status: 'active',
    lastLogin: '2025-01-23T10:15:00Z',
    createdAt: '2025-01-15T00:00:00Z',
    runsCount: 23,
  },
  {
    id: '3',
    name: 'Michael Chen',
    email: 'michael.chen@company.com',
    role: 'user',
    status: 'active',
    lastLogin: '2025-01-22T16:45:00Z',
    createdAt: '2025-01-10T00:00:00Z',
    runsCount: 67,
  },
  {
    id: '4',
    name: 'Emily Rodriguez',
    email: 'emily.rodriguez@company.com',
    role: 'admin',
    status: 'active',
    lastLogin: '2025-01-23T09:20:00Z',
    createdAt: '2025-01-05T00:00:00Z',
    runsCount: 89,
  },
  {
    id: '5',
    name: 'David Kim',
    email: 'david.kim@company.com',
    role: 'user',
    status: 'inactive',
    lastLogin: '2025-01-20T14:30:00Z',
    createdAt: '2025-01-12T00:00:00Z',
    runsCount: 12,
  },
  {
    id: '6',
    name: 'Lisa Thompson',
    email: 'lisa.thompson@company.com',
    role: 'user',
    status: 'pending',
    lastLogin: 'Never',
    createdAt: '2025-01-22T00:00:00Z',
    runsCount: 0,
  },
];

const roleOptions: FilterOption[] = [
  { value: 'all', label: 'All Roles' },
  { value: 'admin', label: 'Admin' },
  { value: 'user', label: 'User' },
];

const statusOptions: FilterOption[] = [
  { value: 'all', label: 'All Status' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'pending', label: 'Pending' },
];

export default function UserManagementPage() {
  return (
    <AdminUsersWithUI
      usersList={mockUsers}
      roleOptions={roleOptions}
      statusOptions={statusOptions}
    />
  );
}
