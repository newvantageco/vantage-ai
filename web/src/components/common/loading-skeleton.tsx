"use client";

import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
  variant?: "default" | "circular" | "rectangular" | "text" | "button" | "card" | "avatar" | "image" | "table" | "list";
  size?: "sm" | "md" | "lg" | "xl";
  width?: string | number;
  height?: string | number;
  animate?: boolean;
  children?: React.ReactNode;
}

export function Skeleton({
  className,
  variant = "default",
  size = "md",
  width,
  height,
  animate = true,
  children,
  ...props
}: SkeletonProps) {
  const baseClasses = "bg-neutral-200 rounded";
  
  const variantClasses = {
    default: "rounded",
    circular: "rounded-full",
    rectangular: "rounded-none",
    text: "rounded-sm",
    button: "rounded-lg",
    card: "rounded-xl",
    avatar: "rounded-full",
    image: "rounded-lg",
    table: "rounded-sm",
    list: "rounded-md"
  };
  
  const sizeClasses = {
    sm: "h-3",
    md: "h-4",
    lg: "h-6",
    xl: "h-8"
  };
  
  const animationClasses = animate ? "animate-pulse" : "";
  
  const style = {
    ...(width && { width: typeof width === "number" ? `${width}px` : width }),
    ...(height && { height: typeof height === "number" ? `${height}px` : height })
  };

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        !width && !height && sizeClasses[size],
        animationClasses,
        className
      )}
      style={style}
      {...props}
    >
      {children}
    </div>
  );
}

// Predefined skeleton components for common use cases
export function SkeletonText({ lines = 1, className, ...props }: { lines?: number; className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          className={cn(
            i === lines - 1 ? "w-3/4" : "w-full",
            className
          )}
          {...props}
        />
      ))}
    </div>
  );
}

export function SkeletonButton({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <Skeleton
      variant="button"
      size="md"
      className={cn("h-10 w-24", className)}
      {...props}
    />
  );
}

export function SkeletonCard({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("p-6 space-y-4", className)}>
      <Skeleton variant="text" className="h-6 w-3/4" {...props} />
      <Skeleton variant="text" className="h-4 w-full" {...props} />
      <Skeleton variant="text" className="h-4 w-2/3" {...props} />
    </div>
  );
}

export function SkeletonAvatar({ size = "md", className, ...props }: { size?: "sm" | "md" | "lg" | "xl"; className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  const sizeClasses = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-12 w-12",
    xl: "h-16 w-16"
  };
  
  return (
    <Skeleton
      variant="avatar"
      className={cn(sizeClasses[size], className)}
      {...props}
    />
  );
}

export function SkeletonImage({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <Skeleton
      variant="image"
      className={cn("h-48 w-full", className)}
      {...props}
    />
  );
}

export function SkeletonTable({ rows = 5, columns = 4, className, ...props }: { rows?: number; columns?: number; className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("space-y-3", className)}>
      {/* Header */}
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} variant="text" className="h-4 flex-1" {...props} />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} variant="text" className="h-4 flex-1" {...props} />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonList({ items = 5, className, ...props }: { items?: number; className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("space-y-3", className)}>
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center space-x-3">
          <Skeleton variant="avatar" className="h-10 w-10" {...props} />
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" className="h-4 w-3/4" {...props} />
            <Skeleton variant="text" className="h-3 w-1/2" {...props} />
          </div>
        </div>
      ))}
    </div>
  );
}

// Dashboard specific skeletons
export function SkeletonKPICard({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("p-6 space-y-4", className)}>
      <div className="flex items-center justify-between">
        <Skeleton variant="text" className="h-4 w-24" {...props} />
        <Skeleton variant="circular" className="h-12 w-12" {...props} />
      </div>
      <Skeleton variant="text" className="h-8 w-16" {...props} />
      <Skeleton variant="text" className="h-4 w-20" {...props} />
    </div>
  );
}

export function SkeletonChart({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("p-6 space-y-4", className)}>
      <div className="flex items-center justify-between">
        <Skeleton variant="text" className="h-6 w-48" {...props} />
        <Skeleton variant="button" className="h-8 w-8" {...props} />
      </div>
      <Skeleton variant="rectangular" className="h-80 w-full" {...props} />
    </div>
  );
}

export function SkeletonSidebar({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("p-4 space-y-4", className)}>
      {/* Logo */}
      <div className="flex items-center space-x-3">
        <Skeleton variant="circular" className="h-9 w-9" {...props} />
        <Skeleton variant="text" className="h-6 w-32" {...props} />
      </div>
      
      {/* Navigation items */}
      <div className="space-y-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className="flex items-center space-x-3 p-3">
            <Skeleton variant="circular" className="h-5 w-5" {...props} />
            <Skeleton variant="text" className="h-4 w-24" {...props} />
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonTopbar({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("flex items-center justify-between p-6", className)}>
      <div className="flex items-center space-x-4">
        <Skeleton variant="text" className="h-6 w-32" {...props} />
        <Skeleton variant="text" className="h-10 w-64" {...props} />
      </div>
      <div className="flex items-center space-x-2">
        <Skeleton variant="button" className="h-9 w-9" {...props} />
        <Skeleton variant="button" className="h-9 w-9" {...props} />
        <Skeleton variant="avatar" className="h-9 w-9" {...props} />
      </div>
    </div>
  );
}

export function SkeletonForm({ fields = 3, className, ...props }: { fields?: number; className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("space-y-6", className)}>
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton variant="text" className="h-4 w-24" {...props} />
          <Skeleton variant="rectangular" className="h-10 w-full" {...props} />
        </div>
      ))}
      <div className="flex space-x-3">
        <Skeleton variant="button" className="h-10 w-24" {...props} />
        <Skeleton variant="button" className="h-10 w-24" {...props} />
      </div>
    </div>
  );
}

export function SkeletonModal({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("p-6 space-y-6", className)}>
      <div className="flex items-center justify-between">
        <Skeleton variant="text" className="h-6 w-48" {...props} />
        <Skeleton variant="button" className="h-8 w-8" {...props} />
      </div>
      <div className="space-y-4">
        <Skeleton variant="text" className="h-4 w-full" {...props} />
        <Skeleton variant="text" className="h-4 w-3/4" {...props} />
        <Skeleton variant="text" className="h-4 w-1/2" {...props} />
      </div>
      <div className="flex justify-end space-x-3">
        <Skeleton variant="button" className="h-10 w-20" {...props} />
        <Skeleton variant="button" className="h-10 w-20" {...props} />
      </div>
    </div>
  );
}

// Loading states for specific components
export function SkeletonContentTable({ rows = 5, className, ...props }: { rows?: number; className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("space-y-4", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <Skeleton variant="text" className="h-8 w-48" {...props} />
        <div className="flex space-x-2">
          <Skeleton variant="button" className="h-10 w-24" {...props} />
          <Skeleton variant="button" className="h-10 w-24" {...props} />
        </div>
      </div>
      
      {/* Table */}
      <SkeletonTable rows={rows} columns={6} {...props} />
    </div>
  );
}

export function SkeletonCalendar({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("space-y-4", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <Skeleton variant="text" className="h-8 w-48" {...props} />
        <div className="flex space-x-2">
          <Skeleton variant="button" className="h-10 w-24" {...props} />
          <Skeleton variant="button" className="h-10 w-24" {...props} />
        </div>
      </div>
      
      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-px bg-neutral-200">
        {/* Day headers */}
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className="bg-neutral-50 p-3">
            <Skeleton variant="text" className="h-4 w-8 mx-auto" {...props} />
          </div>
        ))}
        
        {/* Calendar days */}
        {Array.from({ length: 35 }).map((_, i) => (
          <div key={i} className="bg-white p-2 min-h-[120px]">
            <Skeleton variant="text" className="h-4 w-6 mb-2" {...props} />
            <div className="space-y-1">
              <Skeleton variant="rectangular" className="h-4 w-full" {...props} />
              <Skeleton variant="rectangular" className="h-4 w-3/4" {...props} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonComposer({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant' | 'size'>) {
  return (
    <div className={cn("space-y-6", className)}>
      {/* Platform Selection */}
      <div className="space-y-4">
        <Skeleton variant="text" className="h-6 w-32" {...props} />
        <div className="grid grid-cols-3 gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} variant="rectangular" className="h-16 w-full" {...props} />
          ))}
        </div>
      </div>
      
      {/* Content Editor */}
      <div className="space-y-4">
        <Skeleton variant="text" className="h-6 w-24" {...props} />
        <Skeleton variant="rectangular" className="h-48 w-full" {...props} />
      </div>
      
      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <Skeleton variant="button" className="h-10 w-24" {...props} />
        <Skeleton variant="button" className="h-10 w-24" {...props} />
      </div>
    </div>
  );
}

// Utility function to create custom skeletons
export function createSkeleton(
  variant: SkeletonProps['variant'] = "default",
  size: SkeletonProps['size'] = "md",
  className?: string
) {
  return function CustomSkeleton(props: Omit<SkeletonProps, 'variant' | 'size'>) {
    return <Skeleton variant={variant} size={size} className={className} {...props} />;
  };
}
