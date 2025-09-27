import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AccountHeader } from './header';
import { ProfileTab } from './profile-tab';
import { SecurityTab } from './security-tab';
import { PreferencesTab } from './preferences-tab';
import { TokensTab } from './tokens-tab';
import type { AccountUser } from './types';

type Props = {
  user: AccountUser;
  onLogout: () => Promise<void>;
  isEditing: boolean;
  editedName: string;
  editedEmail: string;
  onEdit: () => void;
  onSave: () => void;
  onCancel: () => void;
  onNameChange: (v: string) => void;
  onEmailChange: (v: string) => void;
};

const AccountLayout = ({
  user,
  onLogout,
  isEditing,
  editedName,
  editedEmail,
  onEdit,
  onSave,
  onCancel,
  onNameChange,
  onEmailChange,
}: Props) => {
  return (
    <div className='min-h-screen bg-background'>
      <AccountHeader user={user} />

      <div className='container mx-auto px-6 py-8'>
        <Tabs defaultValue='profile' className='space-y-6'>
          <TabsList className='bg-muted'>
            <TabsTrigger
              value='profile'
              className='data-[state=active]:bg-background'
            >
              <span className='w-4 h-4 mr-2'>👤</span> Profile
            </TabsTrigger>
            <TabsTrigger
              value='security'
              className='data-[state=active]:bg-background'
            >
              <span className='w-4 h-4 mr-2'>🔒</span> Security
            </TabsTrigger>
            <TabsTrigger
              value='preferences'
              className='data-[state=active]:bg-background'
            >
              <span className='w-4 h-4 mr-2'>🎨</span> Preferences
            </TabsTrigger>
            <TabsTrigger
              value='tokens'
              className='data-[state=active]:bg-background'
            >
              <span className='w-4 h-4 mr-2'>🔑</span> API Tokens
            </TabsTrigger>
          </TabsList>

          <TabsContent value='profile'>
            <ProfileTab
              user={user}
              isEditing={isEditing}
              editedName={editedName}
              editedEmail={editedEmail}
              onEdit={onEdit}
              onSave={onSave}
              onCancel={onCancel}
              onNameChange={onNameChange}
              onEmailChange={onEmailChange}
              onLogout={onLogout}
            />
          </TabsContent>

          <TabsContent value='security'>
            <SecurityTab />
          </TabsContent>

          <TabsContent value='preferences'>
            <PreferencesTab />
          </TabsContent>

          <TabsContent value='tokens'>
            <TokensTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AccountLayout;
