'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { isAdmin } from '@/lib/auth';
import {
  Search,
  Users,
  UserPlus,
  MoreHorizontal,
  Copy,
  Mail,
  Shield,
  User,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from 'lucide-react';

interface UserData {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  status: 'active' | 'inactive' | 'pending';
  lastLogin: string;
  createdAt: string;
  runsCount: number;
}

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

const roleOptions = [
  { value: 'all', label: 'All Roles' },
  { value: 'admin', label: 'Admin' },
  { value: 'user', label: 'User' },
];

const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'pending', label: 'Pending' },
];

export default function UserManagementPage() {
  const [users, setUsers] = useState<UserData[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<UserData[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [isRoleChangeDialogOpen, setIsRoleChangeDialogOpen] = useState(false);
  const [newRole, setNewRole] = useState<'admin' | 'user'>('user');

  const userIsAdmin = isAdmin();

  useEffect(() => {
    // Redirect non-admin users
    if (!userIsAdmin) {
      window.location.href = '/flows';
      return;
    }

    // Simulate loading
    setTimeout(() => {
      setUsers(mockUsers);
      setFilteredUsers(mockUsers);
      setIsLoading(false);
    }, 800);
  }, [userIsAdmin]);

  useEffect(() => {
    let filtered = users;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (user) =>
          user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          user.email.toLowerCase().includes(searchQuery.toLowerCase()),
      );
    }

    // Role filter
    if (roleFilter !== 'all') {
      filtered = filtered.filter((user) => user.role === roleFilter);
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((user) => user.status === statusFilter);
    }

    setFilteredUsers(filtered);
  }, [users, searchQuery, roleFilter, statusFilter]);

  const getRoleColor = (role: string) => {
    return role === 'admin'
      ? 'bg-primary/10 text-primary border-primary/20'
      : 'bg-muted text-muted-foreground';
  };

  const getStatusColor = (status: string) => {
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

  const getStatusIcon = (status: string) => {
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

  const formatDate = (dateString: string) => {
    if (dateString === 'Never') return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatLastLogin = (dateString: string) => {
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

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const handleRoleChange = (user: UserData) => {
    setSelectedUser(user);
    setNewRole(user.role === 'admin' ? 'user' : 'admin');
    setIsRoleChangeDialogOpen(true);
  };

  const confirmRoleChange = () => {
    if (selectedUser) {
      setUsers(
        users.map((user) =>
          user.id === selectedUser.id ? { ...user, role: newRole } : user,
        ),
      );
      setIsRoleChangeDialogOpen(false);
      setSelectedUser(null);
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setRoleFilter('all');
    setStatusFilter('all');
  };

  const hasActiveFilters =
    searchQuery || roleFilter !== 'all' || statusFilter !== 'all';

  if (!userIsAdmin) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className='min-h-screen bg-background'>
      {/* Header */}
      <div className='border-b border-border bg-card/50'>
        <div className='container mx-auto px-6 py-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold text-foreground'>
                User Management
              </h1>
              <p className='text-muted-foreground mt-1'>
                Manage users and their roles
              </p>
            </div>
            <div className='flex items-center space-x-4'>
              {/* Search */}
              <div className='relative'>
                <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
                <Input
                  placeholder='Search users...'
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className='pl-10 w-80 bg-input border-border'
                />
              </div>

              {/* Invite User Button */}
              <Button disabled className='bg-primary hover:bg-primary/90'>
                <UserPlus className='w-4 h-4 mr-2' />
                Invite User
              </Button>
            </div>
          </div>

          {/* Filters */}
          <div className='flex items-center justify-between mt-6'>
            <div className='flex items-center space-x-4'>
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger className='w-40 bg-input border-border'>
                  <SelectValue placeholder='Role' />
                </SelectTrigger>
                <SelectContent>
                  {roleOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className='w-40 bg-input border-border'>
                  <SelectValue placeholder='Status' />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {hasActiveFilters && (
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={clearFilters}
                  className='text-muted-foreground'
                >
                  Clear filters
                </Button>
              )}
            </div>

            <div className='flex items-center space-x-4 text-sm text-muted-foreground'>
              <div className='flex items-center space-x-2'>
                <Users className='w-4 h-4' />
                <span>{filteredUsers.length} users</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className='container mx-auto px-6 py-8'>
        {isLoading ? (
          <div className='border border-border rounded-lg bg-card'>
            <Table>
              <TableHeader>
                <TableRow className='border-border'>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead>Runs</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.from({ length: 6 }).map((_, i) => (
                  <TableRow key={i} className='border-border'>
                    <TableCell>
                      <div className='flex items-center space-x-3'>
                        <Skeleton className='h-8 w-8 rounded-full' />
                        <div>
                          <Skeleton className='h-4 w-32 mb-1' />
                          <Skeleton className='h-3 w-48' />
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Skeleton className='h-5 w-16' />
                    </TableCell>
                    <TableCell>
                      <Skeleton className='h-5 w-20' />
                    </TableCell>
                    <TableCell>
                      <Skeleton className='h-4 w-24' />
                    </TableCell>
                    <TableCell>
                      <Skeleton className='h-4 w-12' />
                    </TableCell>
                    <TableCell>
                      <Skeleton className='h-8 w-8' />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className='text-center py-16'>
            <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
              <Users className='w-8 h-8 text-muted-foreground' />
            </div>
            <h3 className='text-lg font-semibold text-foreground mb-2'>
              No users found
            </h3>
            <p className='text-muted-foreground mb-4'>
              {hasActiveFilters
                ? 'Try adjusting your filters'
                : 'No users match your criteria'}
            </p>
            {hasActiveFilters && (
              <Button
                variant='outline'
                onClick={clearFilters}
                className='border-border bg-transparent'
              >
                Clear filters
              </Button>
            )}
          </div>
        ) : (
          <div className='border border-border rounded-lg bg-card'>
            <Table>
              <TableHeader>
                <TableRow className='border-border'>
                  <TableHead className='text-foreground'>User</TableHead>
                  <TableHead className='text-foreground'>Role</TableHead>
                  <TableHead className='text-foreground'>Status</TableHead>
                  <TableHead className='text-foreground'>Last Login</TableHead>
                  <TableHead className='text-foreground'>Runs</TableHead>
                  <TableHead className='text-foreground'>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow
                    key={user.id}
                    className='border-border hover:bg-muted/50'
                  >
                    <TableCell>
                      <div className='flex items-center space-x-3'>
                        <Avatar className='h-8 w-8'>
                          <AvatarFallback className='bg-primary text-primary-foreground text-sm'>
                            {user.name.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className='font-medium text-foreground'>
                            {user.name}
                          </p>
                          <p className='text-sm text-muted-foreground'>
                            {user.email}
                          </p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getRoleColor(user.role)}>
                        {user.role === 'admin' ? (
                          <>
                            <Shield className='w-3 h-3 mr-1' />
                            Admin
                          </>
                        ) : (
                          <>
                            <User className='w-3 h-3 mr-1' />
                            User
                          </>
                        )}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(user.status)}>
                        {getStatusIcon(user.status)}
                        <span className='ml-1 capitalize'>{user.status}</span>
                      </Badge>
                    </TableCell>
                    <TableCell className='text-muted-foreground'>
                      {formatLastLogin(user.lastLogin)}
                    </TableCell>
                    <TableCell className='text-muted-foreground'>
                      {user.runsCount}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant='ghost' size='sm'>
                            <MoreHorizontal className='w-4 h-4' />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                          align='end'
                          className='bg-popover border-border'
                        >
                          <DropdownMenuItem
                            onClick={() => handleRoleChange(user)}
                          >
                            <Shield className='w-4 h-4 mr-2' />
                            Change Role
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => copyToClipboard(user.email)}
                          >
                            <Mail className='w-4 h-4 mr-2' />
                            Copy Email
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => copyToClipboard(user.id)}
                          >
                            <Copy className='w-4 h-4 mr-2' />
                            Copy ID
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}

        {/* Stats Cards */}
        <div className='grid grid-cols-1 md:grid-cols-4 gap-6 mt-8'>
          <Card className='border-border bg-card'>
            <CardHeader className='pb-2'>
              <CardTitle className='text-sm font-medium text-muted-foreground'>
                Total Users
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className='text-2xl font-bold text-foreground'>
                {users.length}
              </div>
            </CardContent>
          </Card>

          <Card className='border-border bg-card'>
            <CardHeader className='pb-2'>
              <CardTitle className='text-sm font-medium text-muted-foreground'>
                Active Users
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className='text-2xl font-bold text-foreground'>
                {users.filter((u) => u.status === 'active').length}
              </div>
            </CardContent>
          </Card>

          <Card className='border-border bg-card'>
            <CardHeader className='pb-2'>
              <CardTitle className='text-sm font-medium text-muted-foreground'>
                Admins
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className='text-2xl font-bold text-foreground'>
                {users.filter((u) => u.role === 'admin').length}
              </div>
            </CardContent>
          </Card>

          <Card className='border-border bg-card'>
            <CardHeader className='pb-2'>
              <CardTitle className='text-sm font-medium text-muted-foreground'>
                Pending
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className='text-2xl font-bold text-foreground'>
                {users.filter((u) => u.status === 'pending').length}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Role Change Dialog */}
      <Dialog
        open={isRoleChangeDialogOpen}
        onOpenChange={setIsRoleChangeDialogOpen}
      >
        <DialogContent className='bg-card border-border'>
          <DialogHeader>
            <DialogTitle className='text-foreground'>
              Change User Role
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to change {selectedUser?.name}'s role from{' '}
              <Badge className={getRoleColor(selectedUser?.role || 'user')}>
                {selectedUser?.role}
              </Badge>{' '}
              to <Badge className={getRoleColor(newRole)}>{newRole}</Badge>?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant='outline'
              onClick={() => setIsRoleChangeDialogOpen(false)}
              className='border-border'
            >
              Cancel
            </Button>
            <Button onClick={confirmRoleChange}>Confirm Change</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
