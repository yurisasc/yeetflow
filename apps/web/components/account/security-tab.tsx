import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function SecurityTab() {
  return (
    <div className='space-y-6'>
      <Card className='border-border bg-card'>
        <CardHeader>
          <CardTitle className='text-foreground'>
            Password & Authentication
          </CardTitle>
          <p className='text-sm text-muted-foreground'>
            Manage your password and authentication settings
          </p>
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

            <div className='flex items-center justify-between'>
              <div>
                <p className='font-medium text-foreground'>Active Sessions</p>
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
              Security features are coming soon. For now, you can sign out to
              end your current session.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
