import React, { useActionState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Play, FileText } from 'lucide-react';
import type { FlowListItem } from './types';
import { useFormStatus } from 'react-dom';

type StartFlowFormAction = (
  prevState: { error: string | null },
  formData: FormData,
) => Promise<{ error: string | null }>;

type FlowCardProps = {
  flow: FlowListItem;
  startFlow: StartFlowFormAction;
  onError?: (error: string | null) => void;
};

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button
      type='submit'
      className='bg-primary hover:bg-primary/90 text-primary-foreground hover:cursor-pointer'
      data-testid='start-flow-button'
      disabled={pending}
    >
      {pending ? (
        <>
          <span className='mr-2 inline-flex h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent align-[-0.125em]' />
          Starting...
        </>
      ) : (
        <>
          <Play className='w-4 h-4 mr-2' />
          Start Flow
        </>
      )}
    </Button>
  );
}

export function FlowCard({ flow, startFlow, onError }: FlowCardProps) {
  const [state, formAction] = useActionState(startFlow, { error: null });

  useEffect(() => {
    onError?.(state.error);
  }, [state.error, onError]);

  return (
    <Card
      className='border-border bg-card hover:bg-card/80 transition-colors group'
      data-testid='flow-card'
    >
      <CardHeader className='pb-3'>
        <div className='flex items-start justify-between'>
          <div className='flex items-center space-x-3'>
            <div className='w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center text-primary'>
              <FileText className='w-5 h-5' />
            </div>
            <div>
              <CardTitle
                className='text-lg text-foreground group-hover:text-primary transition-colors'
                data-testid='flow-name'
              >
                {flow.name}
              </CardTitle>
            </div>
          </div>
        </div>
        <CardDescription
          className='text-muted-foreground leading-relaxed'
          data-testid='flow-description'
        >
          {flow.description || 'No description provided'}
        </CardDescription>
      </CardHeader>
      <CardContent className='pt-0'>
        <div className='flex items-center justify-end'>
          <form action={formAction}>
            <input type='hidden' name='flow_id' value={flow.id} />
            <SubmitButton />
          </form>
        </div>
      </CardContent>
    </Card>
  );
}
