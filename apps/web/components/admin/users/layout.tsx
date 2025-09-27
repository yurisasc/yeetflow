import React from 'react';
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
  stats: { total: number; active: number; admins: number; pending: number };
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
  stats,
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
          total={users.length}
          active={users.filter((u) => u.status === 'active').length}
          admins={users.filter((u) => u.role === 'admin').length}
          pending={users.filter((u) => u.status === 'pending').length}
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
