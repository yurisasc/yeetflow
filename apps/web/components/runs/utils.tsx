import React from 'react';
import { Archive, FileSpreadsheet, FileText, ImageIcon } from 'lucide-react';
import type { RunStatus } from './types';

export const getStatusColor = (status: RunStatus) => {
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

export const getArtifactIcon = (type: string) => {
  switch (type) {
    case 'json':
      return <FileText className='w-4 h-4' />;
    case 'csv':
      return <FileSpreadsheet className='w-4 h-4' />;
    case 'zip':
      return <Archive className='w-4 h-4' />;
    case 'image':
      return <ImageIcon className='w-4 h-4' />;
    default:
      return <FileText className='w-4 h-4' />;
  }
};

export const formatDate = (dateString: string) =>
  new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
