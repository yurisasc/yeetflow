'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { getCurrentUser, logout, isAdmin } from '@/lib/auth';
import {
  Menu,
  Zap,
  Workflow,
  Activity,
  User,
  LogOut,
  Users,
  ChevronDown,
} from 'lucide-react';

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

interface MobileNavProps {
  className?: string;
}

export function MobileNav({ className }: MobileNavProps) {
  const pathname = usePathname();
  const user = getCurrentUser();
  const userIsAdmin = isAdmin();
  const [open, setOpen] = React.useState(false);

  const isActivePath = (href: string) => {
    if (href === '/flows') return pathname === '/flows';
    if (href === '/runs') return pathname?.startsWith('/runs');
    if (href === '/admin/users') return pathname?.startsWith('/admin/users');
    return pathname === href;
  };

  const visibleNavigation = navigation.filter(
    (item) => !item.adminOnly || userIsAdmin,
  );

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant='ghost'
          size='sm'
          className={cn('md:hidden', className)}
        >
          <Menu className='w-5 h-5' />
          <span className='sr-only'>Open menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side='left' className='w-80 bg-card border-border'>
        <SheetHeader className='border-b border-border pb-4'>
          <SheetTitle>
            <Link
              href='/flows'
              className='flex items-center space-x-2'
              onClick={() => setOpen(false)}
            >
              <div className='w-8 h-8 bg-primary rounded-lg flex items-center justify-center'>
                <Zap className='w-5 h-5 text-primary-foreground' />
              </div>
              <span className='text-xl font-bold text-foreground'>
                YeetFlow
              </span>
            </Link>
          </SheetTitle>
        </SheetHeader>

        {/* Navigation */}
        <nav className='flex-1 py-6 space-y-2'>
          {visibleNavigation.map((item) => {
            const isActive = isActivePath(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setOpen(false)}
                className={cn(
                  'flex items-center justify-between px-3 py-3 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent',
                )}
              >
                <div className='flex items-center space-x-3'>
                  <item.icon className='w-5 h-5' />
                  <div>
                    <div>{item.name}</div>
                    <div className='text-xs text-muted-foreground'>
                      {item.description}
                    </div>
                  </div>
                </div>
                {item.badge && <Badge variant='secondary'>{item.badge}</Badge>}
              </Link>
            );
          })}
        </nav>

        {/* User Identity */}
        <div className='border-t border-border pt-4'>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant='ghost'
                className='w-full justify-start p-2 h-auto'
              >
                <div className='flex items-center space-x-3 w-full'>
                  <Avatar className='h-8 w-8'>
                    <AvatarFallback className='bg-primary text-primary-foreground text-sm'>
                      {user?.name?.charAt(0) || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div className='flex-1 text-left'>
                    <div className='flex items-center space-x-2'>
                      <p className='text-sm font-medium text-foreground truncate'>
                        {user?.name || 'Demo User'}
                      </p>
                      <Badge
                        variant={
                          user?.role === 'admin' ? 'default' : 'secondary'
                        }
                        className='text-xs'
                      >
                        {user?.role === 'admin' ? 'Admin' : 'User'}
                      </Badge>
                    </div>
                    <p className='text-xs text-muted-foreground truncate'>
                      {user?.email || 'demo@yeetflow.com'}
                    </p>
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
                <Link href='/account' onClick={() => setOpen(false)}>
                  <User className='mr-2 h-4 w-4' />
                  <span>Account Settings</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={logout}
                className='hover:bg-accent text-red-400'
              >
                <LogOut className='mr-2 h-4 w-4' />
                <span>Sign out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </SheetContent>
    </Sheet>
  );
}
