import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Save, Edit, X } from 'lucide-react';
import type { AccountUser } from './types';

type ProfileTabProps = {
  user: AccountUser;
  isEditing: boolean;
  editedName: string;
  editedEmail: string;
  onEdit: () => void;
  onSave: () => void;
  onCancel: () => void;
  onNameChange: (name: string) => void;
  onEmailChange: (email: string) => void;
  onLogout: () => Promise<void>;
};

export function ProfileTab({
  user,
  isEditing,
  editedName,
  editedEmail,
  onEdit,
  onSave,
  onCancel,
  onNameChange,
  onEmailChange,
  onLogout,
}: ProfileTabProps) {
  return (
    <div className='space-y-6'>
      <div className='border-border bg-card'>
        <div className='p-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h3 className='text-lg font-medium text-foreground'>
                Profile Information
              </h3>
              <p className='text-sm text-muted-foreground'>
                Update your personal information and profile details
              </p>
            </div>
            {!isEditing ? (
              <Button
                variant='outline'
                onClick={onEdit}
                className='border-border'
              >
                <Edit className='w-4 h-4 mr-2' /> Edit Profile
              </Button>
            ) : (
              <div className='flex items-center space-x-2'>
                <Button
                  variant='outline'
                  onClick={onCancel}
                  className='border-border bg-transparent'
                >
                  <X className='w-4 h-4 mr-2' /> Cancel
                </Button>
                <Button onClick={onSave}>
                  <Save className='w-4 h-4 mr-2' /> Save Changes
                </Button>
              </div>
            )}
          </div>

          <div className='mt-6'>
            <div className='flex items-center space-x-6'>
              <Avatar className='h-20 w-20'>
                <AvatarFallback className='bg-primary text-primary-foreground text-2xl'>
                  {user?.name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className='space-y-2'>
                <p className='text-sm text-muted-foreground'>Profile Picture</p>
                <div className='flex items-center space-x-2'>
                  <Button
                    variant='outline'
                    size='sm'
                    disabled
                    className='border-border bg-transparent'
                  >
                    Upload Photo
                  </Button>
                  <Button
                    variant='ghost'
                    size='sm'
                    disabled
                    className='text-muted-foreground'
                  >
                    Remove
                  </Button>
                </div>
                <p className='text-xs text-muted-foreground'>
                  Photo upload coming soon
                </p>
              </div>
            </div>

            <Separator className='my-6 bg-border' />

            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              <div className='space-y-2'>
                <Label htmlFor='name' className='text-foreground'>
                  Full Name
                </Label>
                {isEditing ? (
                  <Input
                    id='name'
                    value={editedName}
                    onChange={(e) => onNameChange(e.target.value)}
                    className='bg-input border-border'
                  />
                ) : (
                  <Input
                    id='name'
                    value={user?.name || ''}
                    readOnly
                    className='bg-muted border-border text-muted-foreground'
                  />
                )}
              </div>

              <div className='space-y-2'>
                <Label htmlFor='email' className='text-foreground'>
                  Email Address
                </Label>
                {isEditing ? (
                  <Input
                    id='email'
                    type='email'
                    value={editedEmail}
                    onChange={(e) => onEmailChange(e.target.value)}
                    className='bg-input border-border'
                  />
                ) : (
                  <Input
                    id='email'
                    value={user?.email || ''}
                    readOnly
                    className='bg-muted border-border text-muted-foreground'
                  />
                )}
              </div>

              <div className='space-y-2'>
                <Label htmlFor='role' className='text-foreground'>
                  Role
                </Label>
                <div className='flex items-center space-x-2'>
                  <Input
                    id='role'
                    value={user.role === 'admin' ? 'Administrator' : 'User'}
                    readOnly
                    className='bg-muted border-border text-muted-foreground'
                  />
                  <Badge
                    variant={user.role === 'admin' ? 'default' : 'secondary'}
                  >
                    {user.role === 'admin' ? 'Admin' : 'User'}
                  </Badge>
                </div>
              </div>

              <div className='space-y-2'>
                <Label htmlFor='userId' className='text-foreground'>
                  User ID
                </Label>
                <Input
                  id='userId'
                  value={user.id}
                  readOnly
                  className='bg-muted border-border text-muted-foreground font-mono text-sm'
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className='border-red-500/20 bg-red-500/5'>
        <div className='p-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h3 className='font-medium text-foreground'>Sign Out</h3>
              <p className='text-sm text-muted-foreground'>
                End your current session and return to the login page
              </p>
            </div>
            <Button variant='destructive' onClick={onLogout}>
              <span>Sign Out</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
