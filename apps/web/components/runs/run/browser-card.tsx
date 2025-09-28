import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ExternalLink, Maximize2, AlertCircle } from 'lucide-react';

export type RunBrowserCardProps = {
  embeddedUrl: string;
  iframeError: boolean;
  heightClass?: string;
  onOpenInNewTab: () => void;
  onToggleFullscreen: () => void;
  onIframeError: () => void;
  onIframeLoad: () => void;
};

export function RunBrowserCard({
  embeddedUrl,
  iframeError,
  heightClass = 'h-[600px]',
  onOpenInNewTab,
  onToggleFullscreen,
  onIframeError,
  onIframeLoad,
}: RunBrowserCardProps) {
  return (
    <Card className='border-border bg-card h-full'>
      <CardHeader className='pb-3'>
        <div className='flex items-center justify-between'>
          <CardTitle className='text-lg'>Browser Session</CardTitle>
          <div className='flex items-center space-x-2'>
            <Button
              variant='outline'
              size='sm'
              onClick={onOpenInNewTab}
              className='border-border'
              aria-label='Open in new tab'
            >
              <ExternalLink className='w-4 h-4 mr-2' />
              Open in New Tab
            </Button>
            <Button
              variant='outline'
              size='sm'
              onClick={onToggleFullscreen}
              className='border-border'
              aria-label='Toggle fullscreen'
            >
              <Maximize2 className='w-4 h-4' />
            </Button>
          </div>
        </div>
        <div className='flex items-center space-x-2 text-sm text-muted-foreground'>
          <div className='w-2 h-2 bg-green-400 rounded-full'></div>
          <span>{embeddedUrl}</span>
        </div>
      </CardHeader>
      <CardContent className='p-0'>
        {iframeError ? (
          <div
            className={`${heightClass} flex items-center justify-center bg-muted/20 border border-border rounded-lg mx-6 mb-6`}
          >
            <div className='text-center space-y-4'>
              <AlertCircle className='w-12 h-12 text-muted-foreground mx-auto' />
              <div>
                <h3 className='text-lg font-semibold text-foreground'>
                  Unable to embed site
                </h3>
                <p className='text-muted-foreground'>
                  This site cannot be displayed in an iframe due to security
                  restrictions.
                </p>
              </div>
              <Button
                onClick={onOpenInNewTab}
                className='bg-primary hover:bg-primary/90'
              >
                <ExternalLink className='w-4 h-4 mr-2' />
                Open in New Tab
              </Button>
            </div>
          </div>
        ) : (
          <div className={`${heightClass} mx-6 mb-6`}>
            <iframe
              src={embeddedUrl}
              className='w-full h-full border border-border rounded-lg'
              data-testid='session-iframe'
              onError={onIframeError}
              onLoad={onIframeLoad}
              title='Embedded browser session'
              referrerPolicy='no-referrer'
              sandbox='allow-scripts allow-forms allow-popups'
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
