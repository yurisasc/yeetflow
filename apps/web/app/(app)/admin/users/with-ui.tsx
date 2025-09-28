'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { UsersLayout } from '@/components/admin/users/layout';
import type { UserData } from '@/components/admin/users/types';
import type { FilterOption } from '@/components/runs/types';
import { useAuth } from '@/providers/auth-provider';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { updateUserRoleAction } from './actions';

type AdminUsersWithUIProps = {
  usersList: UserData[];
  roleOptions: FilterOption[];
  statusOptions: FilterOption[];
};

const ROLE_VALUES = ['all', 'admin', 'user'] as const;
const STATUS_VALUES = ['all', 'active', 'inactive', 'pending'] as const;

export default function AdminUsersWithUI({
  usersList,
  roleOptions,
  statusOptions,
}: AdminUsersWithUIProps) {
  const { isAdmin, isLoading } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<UserData[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<'all' | 'admin' | 'user'>('all');
  const [statusFilter, setStatusFilter] = useState<
    'all' | 'active' | 'inactive' | 'pending'
  >('all');
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [isRoleChangeDialogOpen, setIsRoleChangeDialogOpen] = useState(false);
  const [newRole, setNewRole] = useState<'admin' | 'user'>('user');

  useEffect(() => {
    if (!isLoading && !isAdmin) {
      router.replace('/flows');
      return;
    }
    if (!isLoading) {
      setUsers(usersList);
      setIsPageLoading(false);
    }
  }, [isAdmin, isLoading, router, usersList]);

  const filteredUsers = useMemo(() => {
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
    return filtered;
  }, [users, searchQuery, roleFilter, statusFilter]);

  const clearFilters = () => {
    setSearchQuery('');
    setRoleFilter('all');
    setStatusFilter('all');
  };

  const handleRoleFilterChange = useCallback((value: string) => {
    if (ROLE_VALUES.includes(value as any)) {
      setRoleFilter(value as typeof ROLE_VALUES[number]);
    }
  }, []);

  const handleStatusFilterChange = useCallback((value: string) => {
    if (STATUS_VALUES.includes(value as any)) {
      setStatusFilter(value as typeof STATUS_VALUES[number]);
    }
  }, []);

  const handleCopy = useCallback(async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast('Copied to clipboard', {
        description: 'User identifier copied successfully.',
      });
    } catch {
      toast.error('Copy failed', {
        description: 'Unable to copy to clipboard. Please try again.',
      });
    }
  }, []);

  const handleRoleChange = useCallback((user: UserData) => {
    setSelectedUser(user);
    setNewRole(user.role === 'admin' ? 'user' : 'admin');
    setIsRoleChangeDialogOpen(true);
  }, []);

  const confirmRoleChange = useCallback(async () => {
    if (!selectedUser) return;

    const previousRole = selectedUser.role;

    setUsers((prev) =>
      prev.map((user) =>
        user.id === selectedUser.id ? { ...user, role: newRole } : user,
      ),
    );

    try {
      const result = await updateUserRoleAction({
        userId: selectedUser.id,
        role: newRole,
      });

      if (!result.success) {
        setUsers((prev) =>
          prev.map((user) =>
            user.id === selectedUser.id
              ? { ...user, role: previousRole }
              : user,
          ),
        );
        toast.error('Unable to update role', {
          description: result.error,
        });
        setIsRoleChangeDialogOpen(true);
        return;
      }

      toast.success('Role updated', {
        description: `${selectedUser.name}'s role is now ${newRole}.`,
      });

      setIsRoleChangeDialogOpen(false);
      setSelectedUser(null);
    } catch (error: unknown) {
      setUsers((prev) =>
        prev.map((user) =>
          user.id === selectedUser.id
            ? { ...user, role: previousRole }
            : user,
        ),
      );
      toast.error('Network error', {
        description: 'We could not update the user role. Please try again.',
      });
      setIsRoleChangeDialogOpen(true);
    }
  }, [newRole, selectedUser, updateUserRoleAction]);

  if (isLoading)
    return (
      <div className='flex h-full w-full flex-col items-center justify-center gap-3 py-16 text-center'>
        <Loader2
          className='h-6 w-6 animate-spin text-muted-foreground'
          aria-hidden='true'
        />
        <p className='text-sm text-muted-foreground'>Checking permissions…</p>
      </div>
    );
  if (!isAdmin) {
    return (
      <div className='flex h-full w-full flex-col items-center justify-center gap-3 py-16 text-center'>
        <p className='text-sm text-muted-foreground'>
          You don't have permission to access this page
        </p>
      </div>
    );
  }

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
      dialog={{ open: isRoleChangeDialogOpen, user: selectedUser, newRole }}
      onSearchChange={setSearchQuery}
      onRoleChange={handleRoleFilterChange}
      onStatusChange={handleStatusFilterChange}
      onClearFilters={clearFilters}
      onCopy={handleCopy}
      onChangeRole={handleRoleChange}
      onDialogOpenChange={setIsRoleChangeDialogOpen}
      onConfirmRoleChange={confirmRoleChange}
    />
  );
}
