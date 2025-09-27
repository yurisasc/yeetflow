import React from 'react';
import {
  AlertTriangle,
  CheckCircle,
  Shield,
  User as UserIcon,
  XCircle,
} from 'lucide-react';

export const getRoleColor = (role: string) =>
  role === 'admin'
    ? 'bg-primary/10 text-primary border-primary/20'
    : 'bg-muted text-muted-foreground';

export const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-500/10 text-green-400 border-green-500/20';
    case 'inactive':
      return 'bg-red-500/10 text-red-400 border-red-500/20';
    case 'pending':
      return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
    default:
      return 'bg-muted text-muted-foreground';
  }
};

export const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active':
      return <CheckCircle className='w-4 h-4' />;
    case 'inactive':
      return <XCircle className='w-4 h-4' />;
    case 'pending':
      return <AlertTriangle className='w-4 h-4' />;
    default:
      return null;
  }
};

export const formatDate = (dateString: string) => {
  if (dateString === 'Never') return 'Never';
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

export const formatLastLogin = (dateString: string) => {
  if (dateString === 'Never') return 'Never';
  const date = new Date(dateString);
  const now = new Date();
  const diffInHours = Math.floor(
    (now.getTime() - date.getTime()) / (1000 * 60 * 60),
  );
  if (diffInHours < 1) return 'Just now';
  if (diffInHours < 24) return `${diffInHours}h ago`;
  if (diffInHours < 48) return 'Yesterday';
  return formatDate(dateString);
};

export const RoleIcon = ({ role }: { role: 'admin' | 'user' }) =>
  role === 'admin' ? (
    <Shield className='w-3 h-3 mr-1' />
  ) : (
    <UserIcon className='w-3 h-3 mr-1' />
  );
