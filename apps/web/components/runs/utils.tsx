import React from 'react';
import { Archive, FileSpreadsheet, FileText, ImageIcon } from 'lucide-react';
import type { RunStatus } from './types';
import { getBadgeToneClass, type BadgeTone } from '../system/status-badge';

const RUN_STATUS_TONE: Record<RunStatus, BadgeTone> = {
  idle: 'neutral',
  running: 'info',
  paused: 'warning',
  awaiting_input: 'purple',
  error: 'danger',
  completed: 'success',
  canceled: 'orange',
};

export const getStatusColor = (status: RunStatus) => {
  const tone = RUN_STATUS_TONE[status] ?? 'muted';
  return getBadgeToneClass(tone);
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
  new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
