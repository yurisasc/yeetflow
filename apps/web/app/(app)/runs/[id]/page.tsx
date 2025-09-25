'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import { AuthGuard } from '@/components/auth-guard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Play,
  Pause,
  Square,
  ExternalLink,
  Maximize2,
  Clock,
  CheckCircle,
  AlertCircle,
  Info,
  User,
  Bot,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface RunEvent {
  id: string;
  type: 'log' | 'warning' | 'error' | 'checkpoint' | 'user_action';
  message: string;
  timestamp: string;
  step: string;
  progress?: number;
}

interface RunStatus {
  id: string;
  name: string;
  status:
    | 'idle'
    | 'running'
    | 'paused'
    | 'awaiting_input'
    | 'error'
    | 'completed';
  progress: number;
  currentStep: string;
  timeElapsed: string;
  estimatedTimeRemaining?: string;
}

export default function RunMonitoringPage() {
  const params = useParams();
  const runId = params.id as string;
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const [runStatus, setRunStatus] = useState<RunStatus>({
    id: runId,
    name: 'Accounts Payable Reconciliation',
    status: 'running',
    progress: 42,
    currentStep: 'Login to Financial System',
    timeElapsed: '00:03:24',
    estimatedTimeRemaining: '12 min',
  });

  const [events, setEvents] = useState<RunEvent[]>([
    {
      id: '1',
      type: 'log',
      message: 'Flow started successfully',
      timestamp: '2025-01-23T10:00:00Z',
      step: 'Initialization',
      progress: 0,
    },
    {
      id: '2',
      type: 'checkpoint',
      message: 'Connected to primary database',
      timestamp: '2025-01-23T10:01:15Z',
      step: 'Database Connection',
      progress: 15,
    },
    {
      id: '3',
      type: 'log',
      message: 'Navigating to login page',
      timestamp: '2025-01-23T10:02:30Z',
      step: 'Navigation',
      progress: 30,
    },
    {
      id: '4',
      type: 'user_action',
      message: 'Manual login required - awaiting user input',
      timestamp: '2025-01-23T10:03:24Z',
      step: 'Login to Financial System',
      progress: 42,
    },
  ]);

  const [showHandoffDialog, setShowHandoffDialog] = useState(false);
  const [handoffNotes, setHandoffNotes] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [inputJson, setInputJson] = useState('');
  const [iframeError, setIframeError] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Mock embedded URL
  const embeddedUrl = 'https://demo.bank.com/login';

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      if (runStatus.status === 'running') {
        const newEvent: RunEvent = {
          id: Date.now().toString(),
          type: 'log',
          message: `Processing step: ${runStatus.currentStep}`,
          timestamp: new Date().toISOString(),
          step: runStatus.currentStep,
          progress: Math.min(runStatus.progress + Math.random() * 5, 95),
        };

        setEvents((prev) => [newEvent, ...prev]);
        setRunStatus((prev) => ({
          ...prev,
          progress: newEvent.progress || prev.progress,
        }));
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [runStatus.status, runStatus.currentStep, runStatus.progress]);

  const getStatusColor = (status: string) => {
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
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const getEventIcon = (type: string) => {
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

  const handleControlAction = (action: string) => {
    switch (action) {
      case 'start':
      case 'resume':
        setRunStatus((prev) => ({ ...prev, status: 'running' }));
        break;
      case 'pause':
        setRunStatus((prev) => ({ ...prev, status: 'paused' }));
        break;
      case 'stop':
        setRunStatus((prev) => ({ ...prev, status: 'idle' }));
        break;
      case 'handoff':
        setShowHandoffDialog(true);
        break;
    }
  };

  const handleHandoffSubmit = () => {
    setRunStatus((prev) => ({
      ...prev,
      status: 'running',
      currentStep: 'AI Processing',
    }));
    setShowHandoffDialog(false);
    setHandoffNotes('');
    setInputJson('');

    const handoffEvent: RunEvent = {
      id: Date.now().toString(),
      type: 'user_action',
      message: `Handed off to AI${
        handoffNotes ? ` with notes: ${handoffNotes}` : ''
      }`,
      timestamp: new Date().toISOString(),
      step: 'AI Handoff',
      progress: runStatus.progress,
    };

    setEvents((prev) => [handoffEvent, ...prev]);
  };

  return (
    <AuthGuard>
      <div className='min-h-screen bg-background'>
        {/* Header */}
        <div className='border-b border-border bg-card/50'>
          <div className='container mx-auto px-6 py-4'>
            <div className='flex items-center justify-between'>
              <div className='flex items-center space-x-4'>
                <h1 className='text-2xl font-bold text-foreground'>
                  {runStatus.name}
                </h1>
                <Badge
                  className={getStatusColor(runStatus.status)}
                  data-testid='run-status'
                >
                  {runStatus.status.replace('_', ' ')}
                </Badge>
              </div>
              <div className='flex items-center space-x-2 text-sm text-muted-foreground'>
                <Clock className='w-4 h-4' />
                <span>{runStatus.timeElapsed}</span>
                {runStatus.estimatedTimeRemaining && (
                  <>
                    <span>•</span>
                    <span>{runStatus.estimatedTimeRemaining} remaining</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className='container mx-auto px-6 py-6'>
          <div className='grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]'>
            {/* Left Panel - Timeline & Controls */}
            <div className='lg:col-span-1 space-y-6'>
              {/* Status Summary */}
              <Card className='border-border bg-card'>
                <CardHeader className='pb-3'>
                  <CardTitle className='text-lg'>Run Status</CardTitle>
                </CardHeader>
                <CardContent className='space-y-4'>
                  <div>
                    <div className='flex justify-between text-sm mb-2'>
                      <span className='text-muted-foreground'>Progress</span>
                      <span className='text-foreground'>
                        {runStatus.progress}%
                      </span>
                    </div>
                    <Progress value={runStatus.progress} className='h-2' />
                  </div>

                  <div>
                    <Label className='text-sm text-muted-foreground'>
                      Current Step
                    </Label>
                    <p className='text-sm font-medium text-foreground'>
                      {runStatus.currentStep}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Controls */}
              <Card className='border-border bg-card'>
                <CardHeader className='pb-3'>
                  <CardTitle className='text-lg'>Controls</CardTitle>
                </CardHeader>
                <CardContent className='space-y-3'>
                  <div className='grid grid-cols-2 gap-2'>
                    {runStatus.status === 'running' ? (
                      <Button
                        variant='outline'
                        onClick={() => handleControlAction('pause')}
                        className='border-border'
                      >
                        <Pause className='w-4 h-4 mr-2' />
                        Pause
                      </Button>
                    ) : (
                      <Button
                        onClick={() => handleControlAction('resume')}
                        className='bg-primary hover:bg-primary/90'
                      >
                        <Play className='w-4 h-4 mr-2' />
                        Resume
                      </Button>
                    )}

                    <Button
                      variant='outline'
                      onClick={() => handleControlAction('stop')}
                      className='border-border'
                    >
                      <Square className='w-4 h-4 mr-2' />
                      Stop
                    </Button>
                  </div>

                  <Button
                    onClick={() => handleControlAction('handoff')}
                    className='w-full bg-purple-600 hover:bg-purple-700 text-white'
                  >
                    <Bot className='w-4 h-4 mr-2' />
                    Complete Manual Steps
                  </Button>
                </CardContent>
              </Card>

              {/* Timeline */}
              <Card className='border-border bg-card flex-1'>
                <CardHeader className='pb-3'>
                  <CardTitle className='text-lg'>Timeline</CardTitle>
                </CardHeader>
                <CardContent className='p-0'>
                  <ScrollArea className='h-[400px] px-6'>
                    <div className='space-y-4'>
                      {events.map((event, index) => (
                        <div
                          key={event.id}
                          className='flex items-start space-x-3'
                        >
                          <div className='flex-shrink-0 mt-1'>
                            {getEventIcon(event.type)}
                          </div>
                          <div className='flex-1 min-w-0'>
                            <div className='flex items-center justify-between'>
                              <p className='text-sm font-medium text-foreground'>
                                {event.step}
                              </p>
                              <span className='text-xs text-muted-foreground'>
                                {new Date(event.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <p className='text-sm text-muted-foreground'>
                              {event.message}
                            </p>
                            {event.progress !== undefined && (
                              <div className='mt-1'>
                                <Progress
                                  value={event.progress}
                                  className='h-1'
                                />
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>

            {/* Right Panel - Embedded Browser */}
            <div className='lg:col-span-2'>
              <Card className='border-border bg-card h-full'>
                <CardHeader className='pb-3'>
                  <div className='flex items-center justify-between'>
                    <CardTitle className='text-lg'>Browser Session</CardTitle>
                    <div className='flex items-center space-x-2'>
                      <Button
                        variant='outline'
                        size='sm'
                        onClick={() => window.open(embeddedUrl, '_blank')}
                        className='border-border'
                      >
                        <ExternalLink className='w-4 h-4 mr-2' />
                        Open in New Tab
                      </Button>
                      <Button
                        variant='outline'
                        size='sm'
                        onClick={() => setIsFullscreen(!isFullscreen)}
                        className='border-border'
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
                    <div className='h-[600px] flex items-center justify-center bg-muted/20 border border-border rounded-lg mx-6 mb-6'>
                      <div className='text-center space-y-4'>
                        <AlertCircle className='w-12 h-12 text-muted-foreground mx-auto' />
                        <div>
                          <h3 className='text-lg font-semibold text-foreground'>
                            Unable to embed site
                          </h3>
                          <p className='text-muted-foreground'>
                            This site cannot be displayed in an iframe due to
                            security restrictions.
                          </p>
                        </div>
                        <Button
                          onClick={() => window.open(embeddedUrl, '_blank')}
                          className='bg-primary hover:bg-primary/90'
                        >
                          <ExternalLink className='w-4 h-4 mr-2' />
                          Open in New Tab
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className='h-[600px] mx-6 mb-6'>
                      <iframe
                        ref={iframeRef}
                        src={embeddedUrl}
                        className='w-full h-full border border-border rounded-lg'
                        data-testid='session-iframe'
                        onError={() => setIframeError(true)}
                        onLoad={() => setIframeError(false)}
                        sandbox='allow-same-origin allow-scripts allow-forms allow-popups'
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Handoff Dialog */}
          <Dialog open={showHandoffDialog} onOpenChange={setShowHandoffDialog}>
            <DialogContent className='bg-popover border-border'>
              <DialogHeader>
                <DialogTitle>Complete Manual Steps</DialogTitle>
                <DialogDescription>
                  Hand off control to AI to continue the automation flow.
                  Optionally provide context about what you've completed.
                </DialogDescription>
              </DialogHeader>

              <div className='space-y-4'>
                <div>
                  <Label htmlFor='notes'>Notes for AI (optional)</Label>
                  <Textarea
                    id='notes'
                    placeholder="Describe what you've completed or any important context..."
                    value={handoffNotes}
                    onChange={(e) => setHandoffNotes(e.target.value)}
                    className='mt-1 bg-input border-border'
                    rows={3}
                  />
                  <p className='text-xs text-muted-foreground mt-1'>
                    {handoffNotes.length}/280 characters
                  </p>
                </div>

                <div>
                  <Button
                    variant='ghost'
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className='p-0 h-auto text-sm text-muted-foreground hover:text-foreground'
                  >
                    Advanced Options
                    {showAdvanced ? (
                      <ChevronUp className='w-4 h-4 ml-1' />
                    ) : (
                      <ChevronDown className='w-4 h-4 ml-1' />
                    )}
                  </Button>

                  {showAdvanced && (
                    <div className='mt-2'>
                      <Label htmlFor='json'>Input JSON (optional)</Label>
                      <Textarea
                        id='json'
                        placeholder='{"key": "value"}'
                        value={inputJson}
                        onChange={(e) => setInputJson(e.target.value)}
                        className='mt-1 font-mono text-sm bg-input border-border'
                        rows={4}
                      />
                    </div>
                  )}
                </div>
              </div>

              <DialogFooter>
                <Button
                  variant='outline'
                  onClick={() => setShowHandoffDialog(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleHandoffSubmit}
                  className='bg-primary hover:bg-primary/90'
                >
                  Continue with AI
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </AuthGuard>
  );
}
