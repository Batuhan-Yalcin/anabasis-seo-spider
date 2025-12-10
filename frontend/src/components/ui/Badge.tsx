import { forwardRef, type HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        critical:
          'bg-severity-critical/20 text-severity-critical border border-severity-critical shadow-glow-critical',
        high:
          'bg-severity-high/20 text-severity-high border border-severity-high',
        medium:
          'bg-severity-medium/20 text-severity-medium border border-severity-medium',
        low:
          'bg-severity-low/20 text-severity-low border border-severity-low',
        default:
          'bg-background-tertiary text-text-secondary border border-glass-border',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export const Badge = forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(badgeVariants({ variant }), className)}
        {...props}
      />
    )
  }
)

Badge.displayName = 'Badge'

