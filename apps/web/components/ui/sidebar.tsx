'use client';

import type React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/providers/auth-provider';
import {
  Zap,
  Workflow,
  Activity,
  User,
  LogOut,
  Users,
  ChevronDown,
} from 'lucide-react';
import { SecurityUtils } from '@/lib/security';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  badge?: number;
  adminOnly?: boolean;
}

const navigation: NavigationItem[] = [
  {
    name: 'Flows',
    href: '/flows',
    icon: Workflow,
    description: 'Browse and start automation workflows',
  },
  {
    name: 'Runs',
    href: '/runs',
    icon: Activity,
    description: 'View run history and monitor progress',
    badge: 3, // Mock running count
  },
  {
    name: 'User Management',
    href: '/admin/users',
    icon: Users,
    description: 'Manage users and roles',
    adminOnly: true,
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const { user, isAdmin, logout, isLoading } = useAuth();

  const isActivePath = (href: string) => {
    if (href === '/flows') return pathname === '/flows';
    if (href === '/runs') return pathname?.startsWith('/runs');
    if (href === '/admin/users') return pathname?.startsWith('/admin/users');
    return pathname === href;
  };

  const visibleNavigation = navigation.filter(
    (item) => !item.adminOnly || isAdmin,
  );

  return (
    <div
      className={cn(
        'flex h-full w-64 flex-col bg-card border-r border-border',
        className,
      )}
    >
      {/* Logo */}
      <div className='flex h-16 items-center px-6 border-b border-border'>
        <Link href='/flows' className='flex items-center space-x-2'>
          <div className='w-8 h-8 bg-primary rounded-lg flex items-center justify-center'>
            <Zap className='w-5 h-5 text-primary-foreground' />
          </div>
          <span className='text-xl font-bold text-foreground'>YeetFlow</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className='flex-1 px-4 py-6 space-y-2'>
        {visibleNavigation.map((item) => {
          const isActive = isActivePath(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors group',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent',
              )}
            >
              <div className='flex items-center space-x-3'>
                <item.icon className='w-5 h-5' />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <Badge variant='secondary' className='ml-auto'>
                  {item.badge}
                </Badge>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Identity */}
      <div className='border-t border-border p-4'>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant='ghost' className='w-full justify-start p-2 h-auto'>
              <div className='flex items-center space-x-3 w-full'>
                {isLoading ? (
                  <Skeleton className='h-8 w-8 rounded-full' />
                ) : (
                  <Avatar className='h-8 w-8'>
                    <AvatarFallback className='bg-primary text-primary-foreground text-sm'>
                      {user?.name?.charAt(0) || 'U'}
                    </AvatarFallback>
                  </Avatar>
                )}
                <div className='flex-1 text-left'>
                  {isLoading ? (
                    <>
                      <Skeleton className='h-4 w-24 mb-1' />
                      <Skeleton className='h-3 w-32' />
                    </>
                  ) : (
                    <>
                      <div className='flex items-center space-x-2'>
                        <p className='text-sm font-medium text-foreground truncate'>
                          {user?.name || ''}
                        </p>
                        <Badge
                          variant={
                            user?.role === 'admin' ? 'default' : 'secondary'
                          }
                          className='text-xs'
                        >
                          {user?.role === 'admin'
                            ? 'Admin'
                            : user
                              ? 'User'
                              : 'Guest'}
                        </Badge>
                      </div>
                      <p className='text-xs text-muted-foreground truncate'>
                        {SecurityUtils.sanitizeInput(user?.email || '')}
                      </p>
                    </>
                  )}
                </div>
                <ChevronDown className='w-4 h-4 text-muted-foreground' />
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className='w-56 bg-popover border-border'
            align='end'
          >
            <DropdownMenuItem asChild className='hover:bg-accent'>
              <Link href='/account'>
                <User className='mr-2 h-4 w-4' />
                <span>Account Settings</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            {user && (
              <DropdownMenuItem
                onClick={logout}
                className='hover:bg-accent text-red-400'
              >
                <LogOut className='mr-2 h-4 w-4' />
                <span>Sign out</span>
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
