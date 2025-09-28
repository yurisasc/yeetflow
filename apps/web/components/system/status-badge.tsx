import React from 'react';
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react';

export type BadgeTone =
  | 'success'
  | 'danger'
  | 'warning'
  | 'info'
  | 'neutral'
  | 'purple'
  | 'orange'
  | 'muted';

const toneClasses: Record<BadgeTone, string> = {
  success: 'bg-green-500/10 text-green-400 border-green-500/20',
  danger: 'bg-red-500/10 text-red-400 border-red-500/20',
  warning: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  neutral: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  orange: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  muted: 'bg-muted text-muted-foreground',
};

export function getBadgeToneClass(tone: BadgeTone): string {
  return toneClasses[tone] ?? toneClasses.muted;
}

export function getBadgeToneIcon(tone: BadgeTone): React.ReactNode {
  switch (tone) {
    case 'success':
      return <CheckCircle className="w-4 h-4" />;
    case 'danger':
      return <XCircle className="w-4 h-4" />;
    case 'warning':
      return <AlertTriangle className="w-4 h-4" />;
    case 'info':
      return <Info className="w-4 h-4" />;
    default:
      return null;
  }
}
