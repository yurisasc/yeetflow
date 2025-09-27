import React from 'react';
import { AlertCircle, CheckCircle, Info, User } from 'lucide-react';
import type { RunEventType, RunStatusSummary } from '../types';

export const statusBadgeClass = (status: RunStatusSummary['status']) => {
  switch (status) {
    case 'idle':
      return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    case 'running':
      return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    case 'paused':
      return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
    case 'awaiting_input':
      return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    case 'error':
      return 'bg-red-500/10 text-red-400 border-red-500/20';
    case 'completed':
      return 'bg-green-500/10 text-green-400 border-green-500/20';
    case 'canceled':
      return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
    default:
      return 'bg-muted text-muted-foreground';
  }
};

export const eventIcon = (type: RunEventType) => {
  switch (type) {
    case 'log':
      return <Info className='w-4 h-4' />;
    case 'warning':
      return <AlertCircle className='w-4 h-4 text-yellow-400' />;
    case 'error':
      return <AlertCircle className='w-4 h-4 text-red-400' />;
    case 'checkpoint':
      return <CheckCircle className='w-4 h-4 text-green-400' />;
    case 'user_action':
      return <User className='w-4 h-4 text-purple-400' />;
    default:
      return <Info className='w-4 h-4' />;
  }
};

export const formatTime = (timestamp: string) =>
  new Date(timestamp).toLocaleTimeString();
