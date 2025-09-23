'use client';

import type React from 'react';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Search,
  Filter,
  Play,
  Clock,
  Database,
  CreditCard,
  FileText,
  Users,
  Settings,
} from 'lucide-react';

interface Flow {
  id: string;
  name: string;
  description: string;
  longDescription: string;
  tags: string[];
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  icon: React.ReactNode;
}

const mockFlows: Flow[] = [
  {
    id: 'accounts-payable',
    name: 'Accounts Payable Reconciliation',
    description:
      'Reconcile invoices across systems with manual login verification',
    longDescription:
      'Automate the reconciliation of accounts payable by connecting to multiple financial systems. Includes manual verification steps for secure login and data validation.',
    tags: ['finance', 'reconciliation', 'verification'],
    category: 'Finance',
    difficulty: 'intermediate',
    estimatedTime: '15-20 min',
    icon: <CreditCard className='w-5 h-5' />,
  },
  {
    id: 'data-migration',
    name: 'Customer Data Migration',
    description: 'Migrate customer records between CRM systems safely',
    longDescription:
      'Safely migrate customer data from legacy CRM to modern systems with validation checkpoints and manual approval steps for sensitive information.',
    tags: ['data', 'migration', 'crm'],
    category: 'Data',
    difficulty: 'advanced',
    estimatedTime: '30-45 min',
    icon: <Database className='w-5 h-5' />,
  },
  {
    id: 'report-generation',
    name: 'Monthly Report Generation',
    description: 'Generate and distribute monthly business reports',
    longDescription:
      'Automatically compile data from various sources to generate comprehensive monthly reports with manual review and approval workflow.',
    tags: ['reporting', 'analytics', 'automation'],
    category: 'Reporting',
    difficulty: 'beginner',
    estimatedTime: '10-15 min',
    icon: <FileText className='w-5 h-5' />,
  },
  {
    id: 'user-onboarding',
    name: 'Employee Onboarding',
    description: 'Automate new employee setup across systems',
    longDescription:
      'Streamline employee onboarding by automating account creation, access provisioning, and documentation delivery with HR approval checkpoints.',
    tags: ['hr', 'onboarding', 'automation'],
    category: 'HR',
    difficulty: 'intermediate',
    estimatedTime: '20-25 min',
    icon: <Users className='w-5 h-5' />,
  },
  {
    id: 'system-maintenance',
    name: 'System Health Check',
    description: 'Perform automated system health monitoring',
    longDescription:
      'Run comprehensive system health checks across infrastructure with manual intervention points for critical issues and maintenance decisions.',
    tags: ['monitoring', 'maintenance', 'infrastructure'],
    category: 'Operations',
    difficulty: 'advanced',
    estimatedTime: '25-30 min',
    icon: <Settings className='w-5 h-5' />,
  },
  {
    id: 'invoice-processing',
    name: 'Invoice Processing',
    description: 'Process and approve invoices automatically',
    longDescription:
      'Automate invoice processing workflow with OCR data extraction, validation rules, and manual approval steps for amounts above threshold.',
    tags: ['finance', 'invoices', 'approval'],
    category: 'Finance',
    difficulty: 'beginner',
    estimatedTime: '8-12 min',
    icon: <FileText className='w-5 h-5' />,
  },
];

export default function FlowsPage() {
  const [flows, setFlows] = useState<Flow[]>([]);
  const [filteredFlows, setFilteredFlows] = useState<Flow[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const categories = [
    'All',
    ...Array.from(new Set(mockFlows.map((flow) => flow.category))),
  ];

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setFlows(mockFlows);
      setFilteredFlows(mockFlows);
      setIsLoading(false);
    }, 1000);
  }, []);

  useEffect(() => {
    let filtered = flows;

    if (searchQuery) {
      filtered = filtered.filter(
        (flow) =>
          flow.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          flow.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          flow.tags.some((tag) =>
            tag.toLowerCase().includes(searchQuery.toLowerCase()),
          ),
      );
    }

    if (selectedCategory !== 'All') {
      filtered = filtered.filter((flow) => flow.category === selectedCategory);
    }

    setFilteredFlows(filtered);
  }, [flows, searchQuery, selectedCategory]);

  const handleStartFlow = (flowId: string) => {
    router.push(`/runs/${flowId}-${Date.now()}`);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'intermediate':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'advanced':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      {/* Header */}
      <div className='border-b border-border bg-card/50'>
        <div className='container mx-auto px-6 py-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold text-foreground'>Flows</h1>
              <p className='text-muted-foreground mt-1'>
                Discover and start automation workflows
              </p>
            </div>
            <div className='flex items-center space-x-4'>
              <div className='relative'>
                <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4' />
                <Input
                  placeholder='Search flows...'
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className='pl-10 w-80 bg-input border-border'
                />
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant='outline'
                    className='border-border bg-transparent'
                  >
                    <Filter className='w-4 h-4 mr-2' />
                    {selectedCategory}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align='end'
                  className='bg-popover border-border'
                >
                  {categories.map((category) => (
                    <DropdownMenuItem
                      key={category}
                      onClick={() => setSelectedCategory(category)}
                      className='hover:bg-accent'
                    >
                      {category}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className='container mx-auto px-6 py-8'>
        {isLoading ? (
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className='border-border bg-card'>
                <CardHeader>
                  <Skeleton className='h-6 w-3/4' />
                  <Skeleton className='h-4 w-full' />
                </CardHeader>
                <CardContent>
                  <div className='space-y-3'>
                    <div className='flex space-x-2'>
                      <Skeleton className='h-5 w-16' />
                      <Skeleton className='h-5 w-20' />
                    </div>
                    <Skeleton className='h-9 w-full' />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredFlows.length === 0 ? (
          <div className='text-center py-16'>
            <div className='w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4'>
              <Search className='w-8 h-8 text-muted-foreground' />
            </div>
            <h3 className='text-lg font-semibold text-foreground mb-2'>
              No flows found
            </h3>
            <p className='text-muted-foreground mb-4'>
              Try adjusting your search or filter criteria
            </p>
            <Button
              variant='outline'
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('All');
              }}
              className='border-border'
            >
              Clear filters
            </Button>
          </div>
        ) : (
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {filteredFlows.map((flow) => (
              <Card
                key={flow.id}
                className='border-border bg-card hover:bg-card/80 transition-colors group'
              >
                <CardHeader className='pb-3'>
                  <div className='flex items-start justify-between'>
                    <div className='flex items-center space-x-3'>
                      <div className='w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center text-primary'>
                        {flow.icon}
                      </div>
                      <div>
                        <CardTitle className='text-lg text-foreground group-hover:text-primary transition-colors'>
                          {flow.name}
                        </CardTitle>
                      </div>
                    </div>
                  </div>
                  <CardDescription className='text-muted-foreground leading-relaxed'>
                    {flow.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className='pt-0'>
                  <div className='space-y-4'>
                    <div className='flex flex-wrap gap-2'>
                      {flow.tags.map((tag) => (
                        <Badge
                          key={tag}
                          variant='secondary'
                          className='text-xs bg-secondary/50 text-secondary-foreground'
                        >
                          {tag}
                        </Badge>
                      ))}
                      <Badge
                        className={`text-xs ${getDifficultyColor(flow.difficulty)}`}
                      >
                        {flow.difficulty}
                      </Badge>
                    </div>

                    <div className='flex items-center justify-between'>
                      <div className='flex items-center text-sm text-muted-foreground'>
                        <Clock className='w-4 h-4 mr-1' />
                        {flow.estimatedTime}
                      </div>
                      <Button
                        onClick={() => handleStartFlow(flow.id)}
                        className='bg-primary hover:bg-primary/90 text-primary-foreground'
                      >
                        <Play className='w-4 h-4 mr-2' />
                        Start Flow
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
