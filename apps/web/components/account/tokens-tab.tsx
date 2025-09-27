import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Key } from 'lucide-react';

export function TokensTab() {
  return (
    <div className='space-y-6'>
      <Card className='border-border bg-card'>
        <CardHeader>
          <CardTitle className='text-foreground'>API Tokens</CardTitle>
          <p className='text-sm text-muted-foreground'>
            Manage API tokens for programmatic access to YeetFlow
          </p>
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
              API token management is coming soon. This will allow you to create
              and manage tokens for programmatic access to your flows and runs.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
