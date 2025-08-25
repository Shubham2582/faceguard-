import React from 'react';
import { cn } from '@/lib/utils';

export const MinimalCard = ({ className, children, ...props }) => (
  <div
    className={cn(
      "rounded-[24px] bg-neutral-950/50 p-2 no-underline shadow-sm transition-all duration-300 hover:bg-neutral-950/70 border border-zinc-900/50 hover:border-zinc-800/80 backdrop-blur-sm animated-cards",
      className
    )}
    {...props}
  >
    {children}
  </div>
);

export const MinimalCardImage = ({ className, alt, src, ...props }) => (
  <div
    className={cn(
      "relative mb-6 h-[190px] w-full rounded-[20px] overflow-hidden",
      className
    )}
    {...props}
  >
    <img
      src={src}
      alt={alt}
      className="absolute inset-0 w-full h-full rounded-[16px] object-cover"
      loading="lazy"
    />
    <div className="absolute inset-0 rounded-[16px] bg-gradient-to-t from-black/20 to-transparent" />
  </div>
);

export const MinimalCardTitle = ({ className, ...props }) => (
  <h3
    className={cn(
      "mt-2 px-1 text-lg font-semibold leading-tight text-white",
      className
    )}
    {...props}
  />
);

export const MinimalCardDescription = ({ className, ...props }) => (
  <p
    className={cn("px-1 pb-2 text-sm text-zinc-400", className)}
    {...props}
  />
);

export const MinimalCardContent = ({ className, ...props }) => (
  <div className={cn("p-6 pt-0", className)} {...props} />
);

export const MinimalCardFooter = ({ className, ...props }) => (
  <div className={cn("flex items-center p-6 pt-0", className)} {...props} />
);