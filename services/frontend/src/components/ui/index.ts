/**
 * Barrel export for UI components
 * Simplifies imports: import { Button, Input, Card } from '@/components/ui'
 */

// Core UI components
export { Button } from './button';
export { Input } from './input';
export { Label } from './label';
export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './card';
export { Badge } from './badge';
export { Alert } from './alert';
export { Progress } from './progress';
export { Tabs } from './tabs';
export { Select } from './select';

// Form components
export { FormField } from './form-field';
export { FormStatus, useFormStatus } from './form-status';
export { PasswordStrength } from './password-strength';

// Loading & feedback components
export { 
  Skeleton, 
  CardSkeleton, 
  ListSkeleton, 
  TableSkeleton 
} from './skeleton';
export { EmptyState, EmptyStateIcons } from './empty-state';

// Navigation components
export { Breadcrumb, generateBreadcrumbs } from './breadcrumb';

// Overlay components
export { Tooltip, SimpleTooltip } from './tooltip';
export { Modal, ConfirmDialog } from './modal';

// Theme
export { ThemeToggle } from './theme-toggle';

// Export types
export type { BreadcrumbItem, BreadcrumbProps } from './breadcrumb';
export type { TooltipProps } from './tooltip';
export type { ModalProps, ConfirmDialogProps } from './modal';
