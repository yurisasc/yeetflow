export type RunArtifact = {
  id: string;
  filename: string;
  type: 'json' | 'csv' | 'zip' | 'image' | 'pdf';
  size: string;
  generatedAt: string;
};

export type RunStatus =
  | 'pending'
  | 'running'
  | 'awaiting_input'
  | 'completed'
  | 'failed';

export type RunListItem = {
  id: string;
  flowName: string;
  flowId: string;
  status: RunStatus;
  progress: number;
  startedAt: string;
  duration: string;
  currentStep?: string;
  artifacts: RunArtifact[];
};

export type FilterOption = {
  value: string;
  label: string;
};

export type RunEventType =
  | 'log'
  | 'warning'
  | 'error'
  | 'checkpoint'
  | 'user_action';

export type RunEvent = {
  id: string;
  type: RunEventType;
  message: string;
  timestamp: string;
  step: string;
  progress?: number;
};

export type RunStatusSummary = {
  id: string;
  name: string;
  status: RunStatus;
  progress: number;
  currentStep: string;
  timeElapsed: string;
  estimatedTimeRemaining?: string;
};
