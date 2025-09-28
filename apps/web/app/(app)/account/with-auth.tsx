'use client';

import React, { useEffect, useState } from 'react';
import AccountLayout from '@/components/account/layout';
import type { AccountUser } from '@/components/account/types';
import { useAuth } from '@/providers/auth-provider';

type Props = {
  user: AccountUser;
};

export default function AccountWithAuth({ user }: Props) {
  const { logout } = useAuth();

  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(user.name || '');
  const [editedEmail, setEditedEmail] = useState(user.email || '');

  useEffect(() => {
    if (!isEditing) {
      setEditedName(user.name || '');
      setEditedEmail(user.email || '');
    }
  }, [user, isEditing]);

  const onEdit = () => setIsEditing(true);
  const onSave = () => {
    // TODO: integrate with PATCH /auth/me when available
    setIsEditing(false);
  };
  const onCancel = () => {
    setEditedName(user.name || '');
    setEditedEmail(user.email || '');
    setIsEditing(false);
  };

  return (
    <AccountLayout
      user={user}
      onLogout={logout}
      isEditing={isEditing}
      editedName={editedName}
      editedEmail={editedEmail}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      onNameChange={setEditedName}
      onEmailChange={setEditedEmail}
    />
  );
}
