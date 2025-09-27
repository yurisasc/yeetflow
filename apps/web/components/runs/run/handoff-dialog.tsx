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
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

export type RunHandoffDialogProps = {
  open: boolean;
  showAdvanced: boolean;
  handoffNotes: string;
  inputJson: string;
  onOpenChange: (open: boolean) => void;
  onToggleAdvanced: () => void;
  onHandoffNotesChange: (value: string) => void;
  onInputJsonChange: (value: string) => void;
  onSubmit: () => void;
};

export function RunHandoffDialog({
  open,
  showAdvanced,
  handoffNotes,
  inputJson,
  onOpenChange,
  onToggleAdvanced,
  onHandoffNotesChange,
  onInputJsonChange,
  onSubmit,
}: RunHandoffDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='bg-popover border-border'>
        <DialogHeader>
          <DialogTitle>Complete Manual Steps</DialogTitle>
          <DialogDescription>
            Hand off control to AI to continue the automation flow. Optionally
            provide context about what you've completed.
          </DialogDescription>
        </DialogHeader>

        <div className='space-y-4'>
          <div>
            <Label htmlFor='notes'>Notes for AI (optional)</Label>
            <Textarea
              id='notes'
              placeholder="Describe what you've completed or any important context..."
              value={handoffNotes}
              onChange={(e) => onHandoffNotesChange(e.target.value)}
              className='mt-1 bg-input border-border'
              rows={3}
              maxLength={280}
            />
            <p className='text-xs text-muted-foreground mt-1'>
              {handoffNotes.length}/280 characters
            </p>
          </div>

          <div>
            <Button
              variant='ghost'
              onClick={onToggleAdvanced}
              className='p-0 h-auto text-sm text-muted-foreground hover:text-foreground'
            >
              Advanced Options
            </Button>

            {showAdvanced && (
              <div className='mt-2'>
                <Label htmlFor='json'>Input JSON (optional)</Label>
                <Textarea
                  id='json'
                  placeholder='{"key": "value"}'
                  value={inputJson}
                  onChange={(e) => onInputJsonChange(e.target.value)}
                  className='mt-1 font-mono text-sm bg-input border-border'
                  rows={4}
                />
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant='outline' onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={onSubmit} className='bg-primary hover:bg-primary/90'>
            Continue with AI
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
