'use client';

import { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { getCurrentUser, logout } from '@/lib/auth';
import {
  User,
  Shield,
  Key,
  Palette,
  LogOut,
  Edit,
  Save,
  X,
} from 'lucide-react';

export default function AccountPage() {
  const user = getCurrentUser();
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(user?.name || '');
  const [editedEmail, setEditedEmail] = useState(user?.email || '');

  const handleSave = () => {
    // In a real app, this would make an API call to update the user
    console.log('Saving user data:', { name: editedName, email: editedEmail });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedName(user?.name || '');
    setEditedEmail(user?.email || '');
    setIsEditing(false);
  };

  return (
    <div className='min-h-screen bg-background'>
      {/* Header */}
      <div className='border-b border-border bg-card/50'>
        <div className='container mx-auto px-6 py-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold text-foreground'>
                Account Settings
              </h1>
              <p className='text-muted-foreground mt-1'>
                Manage your profile and account preferences
              </p>
            </div>
            <div className='flex items-center space-x-3'>
              <Avatar className='h-12 w-12'>
                <AvatarFallback className='bg-primary text-primary-foreground text-lg'>
                  {user?.name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div>
                <div className='flex items-center space-x-2'>
                  <p className='font-medium text-foreground'>
                    {user?.name || 'Demo User'}
                  </p>
                  <Badge
                    variant={user?.role === 'admin' ? 'default' : 'secondary'}
                  >
                    {user?.role === 'admin' ? 'Admin' : 'User'}
                  </Badge>
                </div>
                <p className='text-sm text-muted-foreground'>
                  {user?.email || 'demo@yeetflow.com'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className='container mx-auto px-6 py-8'>
        <Tabs defaultValue='profile' className='space-y-6'>
          <TabsList className='bg-muted'>
            <TabsTrigger
              value='profile'
              className='data-[state=active]:bg-background'
            >
              <User className='w-4 h-4 mr-2' />
              Profile
            </TabsTrigger>
            <TabsTrigger
              value='security'
              className='data-[state=active]:bg-background'
            >
              <Shield className='w-4 h-4 mr-2' />
              Security
            </TabsTrigger>
            <TabsTrigger
              value='preferences'
              className='data-[state=active]:bg-background'
            >
              <Palette className='w-4 h-4 mr-2' />
              Preferences
            </TabsTrigger>
            <TabsTrigger
              value='tokens'
              className='data-[state=active]:bg-background'
            >
              <Key className='w-4 h-4 mr-2' />
              API Tokens
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value='profile' className='space-y-6'>
            <Card className='border-border bg-card'>
              <CardHeader>
                <div className='flex items-center justify-between'>
                  <div>
                    <CardTitle className='text-foreground'>
                      Profile Information
                    </CardTitle>
                    <CardDescription>
                      Update your personal information and profile details
                    </CardDescription>
                  </div>
                  {!isEditing ? (
                    <Button
                      variant='outline'
                      onClick={() => setIsEditing(true)}
                      className='border-border'
                    >
                      <Edit className='w-4 h-4 mr-2' />
                      Edit Profile
                    </Button>
                  ) : (
                    <div className='flex items-center space-x-2'>
                      <Button
                        variant='outline'
                        onClick={handleCancel}
                        className='border-border bg-transparent'
                      >
                        <X className='w-4 h-4 mr-2' />
                        Cancel
                      </Button>
                      <Button onClick={handleSave}>
                        <Save className='w-4 h-4 mr-2' />
                        Save Changes
                      </Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent className='space-y-6'>
                <div className='flex items-center space-x-6'>
                  <Avatar className='h-20 w-20'>
                    <AvatarFallback className='bg-primary text-primary-foreground text-2xl'>
                      {user?.name?.charAt(0) || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div className='space-y-2'>
                    <p className='text-sm text-muted-foreground'>
                      Profile Picture
                    </p>
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

                <Separator className='bg-border' />

                <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                  <div className='space-y-2'>
                    <Label htmlFor='name' className='text-foreground'>
                      Full Name
                    </Label>
                    {isEditing ? (
                      <Input
                        id='name'
                        value={editedName}
                        onChange={(e) => setEditedName(e.target.value)}
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
                        onChange={(e) => setEditedEmail(e.target.value)}
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
                        value={
                          user?.role === 'admin' ? 'Administrator' : 'User'
                        }
                        readOnly
                        className='bg-muted border-border text-muted-foreground'
                      />
                      <Badge
                        variant={
                          user?.role === 'admin' ? 'default' : 'secondary'
                        }
                      >
                        {user?.role === 'admin' ? 'Admin' : 'User'}
                      </Badge>
                    </div>
                  </div>

                  <div className='space-y-2'>
                    <Label htmlFor='userId' className='text-foreground'>
                      User ID
                    </Label>
                    <Input
                      id='userId'
                      value={user?.id || ''}
                      readOnly
                      className='bg-muted border-border text-muted-foreground font-mono text-sm'
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className='border-border bg-card'>
              <CardHeader>
                <CardTitle className='text-foreground'>
                  Account Status
                </CardTitle>
                <CardDescription>
                  Your account information and status
                </CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='font-medium text-foreground'>
                      Account Status
                    </p>
                    <p className='text-sm text-muted-foreground'>
                      Your account is active and in good standing
                    </p>
                  </div>
                  <Badge className='bg-green-500/10 text-green-400 border-green-500/20'>
                    Active
                  </Badge>
                </div>

                <Separator className='bg-border' />

                <div className='flex items-center justify-between'>
                  <div>
                    <p className='font-medium text-foreground'>Member Since</p>
                    <p className='text-sm text-muted-foreground'>
                      January 2025
                    </p>
                  </div>
                </div>

                <Separator className='bg-border' />

                <div className='flex items-center justify-between'>
                  <div>
                    <p className='font-medium text-foreground'>Last Login</p>
                    <p className='text-sm text-muted-foreground'>
                      Today at 2:30 PM
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value='security' className='space-y-6'>
            <Card className='border-border bg-card'>
              <CardHeader>
                <CardTitle className='text-foreground'>
                  Password & Authentication
                </CardTitle>
                <CardDescription>
                  Manage your password and authentication settings
                </CardDescription>
              </CardHeader>
              <CardContent className='space-y-6'>
                <div className='space-y-4'>
                  <div className='flex items-center justify-between'>
                    <div>
                      <p className='font-medium text-foreground'>Password</p>
                      <p className='text-sm text-muted-foreground'>
                        Last changed 30 days ago
                      </p>
                    </div>
                    <Button
                      variant='outline'
                      disabled
                      className='border-border bg-transparent'
                    >
                      Change Password
                    </Button>
                  </div>

                  <Separator className='bg-border' />

                  <div className='flex items-center justify-between'>
                    <div>
                      <p className='font-medium text-foreground'>
                        Two-Factor Authentication
                      </p>
                      <p className='text-sm text-muted-foreground'>
                        Add an extra layer of security to your account
                      </p>
                    </div>
                    <Button
                      variant='outline'
                      disabled
                      className='border-border bg-transparent'
                    >
                      Enable 2FA
                    </Button>
                  </div>

                  <Separator className='bg-border' />

                  <div className='flex items-center justify-between'>
                    <div>
                      <p className='font-medium text-foreground'>
                        Active Sessions
                      </p>
                      <p className='text-sm text-muted-foreground'>
                        Manage your active login sessions
                      </p>
                    </div>
                    <Button
                      variant='outline'
                      disabled
                      className='border-border bg-transparent'
                    >
                      View Sessions
                    </Button>
                  </div>
                </div>

                <div className='bg-muted/50 border border-border rounded-lg p-4'>
                  <p className='text-sm text-muted-foreground'>
                    Security features are coming soon. For now, you can sign out
                    to end your current session.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Preferences Tab */}
          <TabsContent value='preferences' className='space-y-6'>
            <Card className='border-border bg-card'>
              <CardHeader>
                <CardTitle className='text-foreground'>Appearance</CardTitle>
                <CardDescription>
                  Customize how YeetFlow looks and feels
                </CardDescription>
              </CardHeader>
              <CardContent className='space-y-6'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='font-medium text-foreground'>Theme</p>
                    <p className='text-sm text-muted-foreground'>
                      Choose your preferred color scheme
                    </p>
                  </div>
                  <div className='flex items-center space-x-2'>
                    <Badge variant='outline' className='border-border'>
                      Dark
                    </Badge>
                    <Switch disabled />
                  </div>
                </div>

                <Separator className='bg-border' />

                <div className='flex items-center justify-between'>
                  <div>
                    <p className='font-medium text-foreground'>Compact Mode</p>
                    <p className='text-sm text-muted-foreground'>
                      Use a more compact layout to fit more content
                    </p>
                  </div>
                  <Switch disabled />
                </div>
              </CardContent>
            </Card>

            <Card className='border-border bg-card'>
              <CardHeader>
                <CardTitle className='text-foreground'>Notifications</CardTitle>
                <CardDescription>
                  Control what notifications you receive
                </CardDescription>
              </CardHeader>
              <CardContent className='space-y-6'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='font-medium text-foreground'>
                      Email Notifications
                    </p>
                    <p className='text-sm text-muted-foreground'>
                      Receive updates about your runs via email
                    </p>
                  </div>
                  <Switch disabled defaultChecked />
                </div>

                <Separator className='bg-border' />

                <div className='flex items-center justify-between'>
                  <div>
                    <p className='font-medium text-foreground'>
                      Run Completion Alerts
                    </p>
                    <p className='text-sm text-muted-foreground'>
                      Get notified when your automation runs complete
                    </p>
                  </div>
                  <Switch disabled defaultChecked />
                </div>

                <Separator className='bg-border' />

                <div className='flex items-center justify-between'>
                  <div>
                    <p className='font-medium text-foreground'>
                      Error Notifications
                    </p>
                    <p className='text-sm text-muted-foreground'>
                      Receive alerts when runs encounter errors
                    </p>
                  </div>
                  <Switch disabled defaultChecked />
                </div>

                <div className='bg-muted/50 border border-border rounded-lg p-4'>
                  <p className='text-sm text-muted-foreground'>
                    Notification preferences are coming soon. All notifications
                    are currently enabled by default.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* API Tokens Tab */}
          <TabsContent value='tokens' className='space-y-6'>
            <Card className='border-border bg-card'>
              <CardHeader>
                <CardTitle className='text-foreground'>API Tokens</CardTitle>
                <CardDescription>
                  Manage API tokens for programmatic access to YeetFlow
                </CardDescription>
              </CardHeader>
              <CardContent className='space-y-6'>
                <div className='text-center py-8'>
                  <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
                    <Key className='w-8 h-8 text-muted-foreground' />
                  </div>
                  <h3 className='text-lg font-semibold text-foreground mb-2'>
                    No API Tokens
                  </h3>
                  <p className='text-muted-foreground mb-4'>
                    You haven't created any API tokens yet. Create one to access
                    YeetFlow programmatically.
                  </p>
                  <Button disabled className='bg-primary hover:bg-primary/90'>
                    Create API Token
                  </Button>
                </div>

                <div className='bg-muted/50 border border-border rounded-lg p-4'>
                  <p className='text-sm text-muted-foreground'>
                    API token management is coming soon. This will allow you to
                    create and manage tokens for programmatic access to your
                    flows and runs.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Danger Zone */}
        <Card className='border-red-500/20 bg-red-500/5 mt-8'>
          <CardHeader>
            <CardTitle className='text-red-400 flex items-center'>
              <LogOut className='w-5 h-5 mr-2' />
              Account Actions
            </CardTitle>
            <CardDescription>
              Manage your account session and access
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className='flex items-center justify-between'>
              <div>
                <p className='font-medium text-foreground'>Sign Out</p>
                <p className='text-sm text-muted-foreground'>
                  End your current session and return to the login page
                </p>
              </div>
              <Button variant='destructive' onClick={logout}>
                <LogOut className='w-4 h-4 mr-2' />
                Sign Out
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
