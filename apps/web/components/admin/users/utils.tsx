import React from 'react';
import {
  Shield,
  User as UserIcon,
} from 'lucide-react';
import {
  getBadgeToneClass,
  getBadgeToneIcon,
  type BadgeTone,
} from '../../system/status-badge';

export type UserRole = 'admin' | 'user';
export type UserStatus = 'active' | 'inactive' | 'pending';

export const getRoleColor = (role: UserRole) =>
  role === 'admin'
    ? 'bg-primary/10 text-primary border-primary/20'
    : 'bg-muted text-muted-foreground';

const USER_STATUS_TONE: Record<UserStatus, BadgeTone> = {
  active: 'success',
  inactive: 'danger',
  pending: 'warning',
};

export const getStatusColor = (status: UserStatus) => {
  const tone = USER_STATUS_TONE[status] ?? 'muted';
  return getBadgeToneClass(tone);
};

export const getStatusIcon = (status: UserStatus) => {
  const tone = USER_STATUS_TONE[status] ?? 'muted';
  return getBadgeToneIcon(tone);
};

export const formatDate = (dateString: string) => {
  if (dateString === 'Never') return 'Never';
  const d = new Date(dateString);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

export const formatLastLogin = (dateString: string) => {
  if (dateString === 'Never') return 'Never';
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return '—';
  const now = new Date();
  const diffInHours = Math.floor(
    (now.getTime() - date.getTime()) / (1000 * 60 * 60),
  );
  if (diffInHours < 1) return 'Just now';
  if (diffInHours < 24) return `${diffInHours}h ago`;
  if (diffInHours < 48) return 'Yesterday';
  return formatDate(dateString);
};

export const RoleIcon = ({ role }: { role: UserRole }) =>
  role === 'admin' ? (
    <Shield className='w-3 h-3 mr-1' />
  ) : (
    <UserIcon className='w-3 h-3 mr-1' />
  );
