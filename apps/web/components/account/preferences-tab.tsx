import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';

export function PreferencesTab() {
  return (
    <div className='space-y-6'>
      <Card className='border-border bg-card'>
        <CardHeader>
          <CardTitle className='text-foreground'>Appearance</CardTitle>
          <p className='text-sm text-muted-foreground'>
            Customize how YeetFlow looks and feels
          </p>
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
          <p className='text-sm text-muted-foreground'>
            Control what notifications you receive
          </p>
        </CardHeader>
        <CardContent className='space-y-6'>
          <div className='flex items-center justify-between'>
            <div>
              <p className='font-medium text-foreground'>Email Notifications</p>
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
              <p className='font-medium text-foreground'>Error Notifications</p>
              <p className='text-sm text-muted-foreground'>
                Receive alerts when runs encounter errors
              </p>
            </div>
            <Switch disabled defaultChecked />
          </div>

          <div className='bg-muted/50 border border-border rounded-lg p-4'>
            <p className='text-sm text-muted-foreground'>
              Notification preferences are coming soon. All notifications are
              currently enabled by default.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
