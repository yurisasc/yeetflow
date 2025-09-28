'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { UsersLayout } from '@/components/admin/users/layout';
import type { FilterOption, UserData } from '@/components/admin/users/types';
import { useAuth } from '@/providers/auth-provider';

type AdminUsersWithUIProps = {
  usersList: UserData[];
  roleOptions: FilterOption[];
  statusOptions: FilterOption[];
};

export default function AdminUsersWithUI({
  usersList,
  roleOptions,
  statusOptions,
}: AdminUsersWithUIProps) {
  const { isAdmin, isLoading } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<UserData[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
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
      const t = setTimeout(() => {
        setUsers(usersList);
        setIsPageLoading(false);
      }, 600);
      return () => clearTimeout(t);
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

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // TODO: consider toast feedback on success
    } catch {
      // TODO: surface failure feedback for the user
    }
  };

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

  if (isLoading) return null;
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
