'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { UsersLayout } from '@/components/admin/users/layout';
import type { FilterOption, UserData } from '@/components/admin/users/types';
import { useAuth } from '@/providers/auth-provider';

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

export default function AdminUsersWithUI() {
  const { isAdmin, isLoading } = useAuth();
  const [users, setUsers] = useState<UserData[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<UserData[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [isRoleChangeDialogOpen, setIsRoleChangeDialogOpen] = useState(false);
  const [newRole, setNewRole] = useState<'admin' | 'user'>('user');

  useEffect(() => {
    if (!isLoading && !isAdmin) {
      window.location.href = '/flows';
      return;
    }
    if (!isLoading) {
      const t = setTimeout(() => {
        setUsers(mockUsers);
        setFilteredUsers(mockUsers);
        setIsPageLoading(false);
      }, 600);
      return () => clearTimeout(t);
    }
  }, [isAdmin, isLoading]);

  useEffect(() => {
    let filtered = users;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (u) =>
          u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q),
      );
    }
    if (roleFilter !== 'all') {
      filtered = filtered.filter((u) => u.role === roleFilter);
    }
    if (statusFilter !== 'all') {
      filtered = filtered.filter((u) => u.status === statusFilter);
    }
    setFilteredUsers(filtered);
  }, [users, searchQuery, roleFilter, statusFilter]);

  const clearFilters = () => {
    setSearchQuery('');
    setRoleFilter('all');
    setStatusFilter('all');
  };

  const stats = useMemo(
    () => ({
      total: users.length,
      active: users.filter((u) => u.status === 'active').length,
      admins: users.filter((u) => u.role === 'admin').length,
      pending: users.filter((u) => u.status === 'pending').length,
    }),
    [users],
  );

  const handleCopy = (text: string) => navigator.clipboard.writeText(text);

  const handleRoleChange = (user: UserData) => {
    setSelectedUser(user);
    setNewRole(user.role === 'admin' ? 'user' : 'admin');
    setIsRoleChangeDialogOpen(true);
  };

  const confirmRoleChange = () => {
    if (selectedUser) {
      setUsers((prev) =>
        prev.map((u) =>
          u.id === selectedUser.id ? { ...u, role: newRole } : u,
        ),
      );
      setIsRoleChangeDialogOpen(false);
      setSelectedUser(null);
    }
  };

  if (!isAdmin) return null;

  return (
    <UsersLayout
      isLoading={isPageLoading}
      users={users}
      filteredUsers={filteredUsers}
      searchQuery={searchQuery}
      roleFilter={roleFilter}
      statusFilter={statusFilter}
      roleOptions={roleOptions}
      statusOptions={statusOptions}
      hasActiveFilters={
        Boolean(searchQuery) || roleFilter !== 'all' || statusFilter !== 'all'
      }
      stats={stats}
      dialog={{ open: isRoleChangeDialogOpen, user: selectedUser, newRole }}
      onSearchChange={setSearchQuery}
      onRoleChange={setRoleFilter}
      onStatusChange={setStatusFilter}
      onClearFilters={clearFilters}
      onCopy={handleCopy}
      onChangeRole={handleRoleChange}
      onDialogOpenChange={setIsRoleChangeDialogOpen}
      onConfirmRoleChange={confirmRoleChange}
    />
  );
}
