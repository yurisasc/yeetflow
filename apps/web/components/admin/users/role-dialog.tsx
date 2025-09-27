import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import type { UserData } from './types';
import { getRoleColor } from './utils';

export type RoleDialogProps = {
  open: boolean;
  user: UserData | null;
  newRole: 'admin' | 'user';
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
};

export function RoleDialog({
  open,
  user,
  newRole,
  onOpenChange,
  onConfirm,
}: RoleDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='bg-card border-border'>
        <DialogHeader>
          <DialogTitle className='text-foreground'>
            Change User Role
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to change {user?.name}'s role from{' '}
            <Badge className={getRoleColor(user?.role || 'user')}>
              {user?.role}
            </Badge>{' '}
            to <Badge className={getRoleColor(newRole)}>{newRole}</Badge>?
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button
            variant='outline'
            onClick={() => onOpenChange(false)}
            className='border-border'
          >
            Cancel
          </Button>
          <Button onClick={onConfirm}>Confirm Change</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
