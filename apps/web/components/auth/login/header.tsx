import React from 'react';
import { Zap } from 'lucide-react';

export function LoginHeader() {
  return (
    <div className='text-center space-y-2'>
      <div className='flex items-center justify-center space-x-2'>
        <div className='w-8 h-8 bg-primary rounded-lg flex items-center justify-center'>
          <Zap className='w-5 h-5 text-primary-foreground' />
        </div>
        <h1 className='text-2xl font-bold text-foreground'>YeetFlow</h1>
      </div>
      <p className='text-muted-foreground'>
        Automation platform with human-in-the-loop
      </p>
    </div>
  );
}
