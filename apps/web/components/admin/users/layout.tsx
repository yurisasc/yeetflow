import React, { useMemo } from 'react';
import type { FilterOption, UserData } from './types';
import { UsersHeader } from './header';
import { UsersFilters } from './filters';
import { UsersLoadingSkeleton } from './loading-skeleton';
import { UsersEmptyState } from './empty-state';
import { UsersTable } from './table';
import { UsersStatsCards } from './stats-cards';
import { RoleDialog } from './role-dialog';

export type UsersLayoutProps = {
  isLoading: boolean;
  users: UserData[];
  filteredUsers: UserData[];
  searchQuery: string;
  roleFilter: string;
  statusFilter: string;
  roleOptions: FilterOption[];
  statusOptions: FilterOption[];
  hasActiveFilters: boolean;
  dialog: { open: boolean; user: UserData | null; newRole: 'admin' | 'user' };
  onSearchChange: (v: string) => void;
  onRoleChange: (v: string) => void;
  onStatusChange: (v: string) => void;
  onClearFilters: () => void;
  onCopy: (text: string) => void;
  onChangeRole: (user: UserData) => void;
  onDialogOpenChange: (open: boolean) => void;
  onConfirmRoleChange: () => void;
};

export function UsersLayout({
  isLoading,
  users,
  filteredUsers,
  searchQuery,
  roleFilter,
  statusFilter,
  roleOptions,
  statusOptions,
  hasActiveFilters,
  dialog,
  onSearchChange,
  onRoleChange,
  onStatusChange,
  onClearFilters,
  onCopy,
  onChangeRole,
  onDialogOpenChange,
  onConfirmRoleChange,
}: UsersLayoutProps) {
  const stats = useMemo(
    () =>
      users.reduce(
        (acc, user) => {
          acc.total += 1;
          if (user.status === 'active') acc.active += 1;
          if (user.role === 'admin') acc.admins += 1;
          if (user.status === 'pending') acc.pending += 1;
          return acc;
        },
        { total: 0, active: 0, admins: 0, pending: 0 },
      ),
    [users],
  );

  return (
    <div className='min-h-screen bg-background'>
      <UsersHeader searchQuery={searchQuery} onSearchChange={onSearchChange} />

      <UsersFilters
        roleFilter={roleFilter}
        statusFilter={statusFilter}
        roleOptions={roleOptions}
        statusOptions={statusOptions}
        hasActiveFilters={hasActiveFilters}
        totalCount={filteredUsers.length}
        onRoleChange={onRoleChange}
        onStatusChange={onStatusChange}
        onClearFilters={onClearFilters}
      />

      <div className='container mx-auto px-6 py-8'>
        {isLoading ? (
          <UsersLoadingSkeleton />
        ) : filteredUsers.length === 0 ? (
          <UsersEmptyState onClearFilters={onClearFilters} />
        ) : (
          <UsersTable
            users={filteredUsers}
            onCopy={onCopy}
            onChangeRole={onChangeRole}
          />
        )}

        <UsersStatsCards
          total={stats.total}
          active={stats.active}
          admins={stats.admins}
          pending={stats.pending}
        />
      </div>

      <RoleDialog
        open={dialog.open}
        user={dialog.user}
        newRole={dialog.newRole}
        onOpenChange={onDialogOpenChange}
        onConfirm={onConfirmRoleChange}
      />
    </div>
  );
}
