import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Copy, Mail, MoreHorizontal, Shield } from 'lucide-react';
import type { UserData } from './types';
import {
  RoleIcon,
  formatLastLogin,
  getRoleColor,
  getStatusColor,
  getStatusIcon,
} from './utils';

export type UsersTableProps = {
  users: UserData[];
  onCopy: (text: string) => void;
  onChangeRole: (user: UserData) => void;
};

export function UsersTable({ users, onCopy, onChangeRole }: UsersTableProps) {
  return (
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
          {users.map((user) => (
            <TableRow key={user.id} className='border-border hover:bg-muted/50'>
              <TableCell>
                <div className='flex items-center space-x-3'>
                  <Avatar className='h-8 w-8'>
                    <AvatarFallback className='bg-primary text-primary-foreground text-sm'>
                      {user.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className='font-medium text-foreground'>{user.name}</p>
                    <p className='text-sm text-muted-foreground'>
                      {user.email}
                    </p>
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <Badge className={getRoleColor(user.role)}>
                  <RoleIcon role={user.role} />
                  {user.role === 'admin' ? 'Admin' : 'User'}
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
                    <DropdownMenuItem onClick={() => onChangeRole(user)}>
                      <Shield className='w-4 h-4 mr-2' />
                      Change Role
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onCopy(user.email)}>
                      <Mail className='w-4 h-4 mr-2' />
                      Copy Email
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onCopy(user.id)}>
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
  );
}
