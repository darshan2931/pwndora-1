'use client';

import { HTMLAttributes, forwardRef } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

// Define safe HTML attributes that we can pass through to the div
// We exclude event handlers to prevent issues when used in Server Components
interface SafeHTMLAttributes extends Omit<HTMLAttributes<HTMLDivElement>,
  | 'onAbort' | 'onAnimationEnd' | 'onAnimationIteration' | 'onAnimationStart'
  | 'onAuxClick' | 'onBeforeInput' | 'onBlur' | 'onCanPlay' | 'onCanPlayThrough'
  | 'onChange' | 'onClick' | 'onClickCapture' | 'onCompositionEnd'
  | 'onCompositionStart' | 'onCompositionUpdate' | 'onContextMenu'
  | 'onCopy' | 'onCut' | 'onDoubleClick' | 'onDrag' | 'onDragEnd'
  | 'onDragEnter' | 'onDragExit' | 'onDragLeave' | 'onDragOver'
  | 'onDragStart' | 'onDrop' | 'onDurationChange' | 'onEmptied'
  | 'onEncrypted' | 'onEnded' | 'onError' | 'onFocus' | 'onInput'
  | 'onInvalid' | 'onKeyDown' | 'onKeyPress' | 'onKeyUp'
  | 'onLoad' | 'onLoadedData' | 'onLoadedMetadata' | 'onLoadStart'
  | 'onMouseDown' | 'onMouseEnter' | 'onMouseLeave' | 'onMouseMove'
  | 'onMouseOut' | 'onMouseOver' | 'onMouseUp' | 'onPaste'
  | 'onPause' | 'onPlay' | 'onPlaying' | 'onProgress'
  | 'onRateChange' | 'onReset' | 'onResize' | 'onScroll'
  | 'onSeeked' | 'onSeeking' | 'onSelect' | 'onStalled'
  | 'onSubmit' | 'onSuspend' | 'onTimeUpdate' | 'onToggle'
  | 'onTouchCancel' | 'onTouchEnd' | 'onTouchMove' | 'onTouchStart'
  | 'onTransitionEnd' | 'onVolumeChange' | 'onWaiting' | 'onWheel'> {}

const variantStyles = {
  default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm',
  elevated: 'bg-white dark:bg-gray-800 shadow-md border border-gray-100 dark:border-gray-700',
  outlined: 'bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700',
};

const paddingStyles = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', padding = 'md', hover, className = '', children, ...props }, ref) => {
    // Filter out event handlers to prevent passing them to DOM elements
    const {
      onAbort, onAnimationEnd, onAnimationIteration, onAnimationStart,
      onAuxClick, onBeforeInput, onBlur, onCanPlay, onCanPlayThrough,
      onChange, onClick, onClickCapture, onCompositionEnd,
      onCompositionStart, onCompositionUpdate, onContextMenu,
      onCopy, onCut, onDoubleClick, onDrag, onDragEnd,
      onDragEnter, onDragExit, onDragLeave, onDragOver,
      onDragStart, onDrop, onDurationChange, onEmptied,
      onEncrypted, onEnded, onError, onFocus, onInput,
      onInvalid, onKeyDown, onKeyPress, onKeyUp,
      onLoad, onLoadedData, onLoadedMetadata, onLoadStart,
      onMouseDown, onMouseEnter, onMouseLeave, onMouseMove,
      onMouseOut, onMouseOver, onMouseUp, onPaste,
      onPause, onPlay, onPlaying, onProgress,
      onRateChange, onReset, onScroll,
      onSeeked, onSeeking, onSelect, onStalled,
      onSubmit, onSuspend, onTimeUpdate, onToggle,
      onTouchCancel, onTouchEnd, onTouchMove, onTouchStart,
      onTransitionEnd, onVolumeChange, onWaiting, onWheel,
      ...safeProps
    } = props;

    return (
      <div
        ref={ref}
        className={`
          rounded-xl
          ${variantStyles[variant]}
          ${paddingStyles[padding]}
          ${hover ? 'transition-shadow duration-200 hover:shadow-md cursor-pointer' : ''}
          ${className}
        `.trim()}
        {...safeProps}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

function CardHeader({ title, subtitle, action, className = '', ...props }: CardHeaderProps) {
  // Filter out event handlers for CardHeader as well
  const {
    onAbort, onAnimationEnd, onAnimationIteration, onAnimationStart,
    onAuxClick, onBeforeInput, onBlur, onCanPlay, onCanPlayThrough,
    onChange, onClick, onClickCapture, onCompositionEnd,
    onCompositionStart, onCompositionUpdate, onContextMenu,
    onCopy, onCut, onDoubleClick, onDrag, onDragEnd,
    onDragEnter, onDragExit, onDragLeave, onDragOver,
    onDragStart, onDrop, onDurationChange, onEmptied,
    onEncrypted, onEnded, onError, onFocus, onInput,
    onInvalid, onKeyDown, onKeyPress, onKeyUp,
    onLoad, onLoadedData, onLoadedMetadata, onLoadStart,
    onMouseDown, onMouseEnter, onMouseLeave, onMouseMove,
    onMouseOut, onMouseOver, onMouseUp, onPaste,
    onPause, onPlay, onPlaying, onProgress,
    onRateChange, onReset, onScroll,
    onSeeked, onSeeking, onSelect, onStalled,
    onSubmit, onSuspend, onTimeUpdate, onToggle,
    onTouchCancel, onTouchEnd, onTouchMove, onTouchStart,
    onTransitionEnd, onVolumeChange, onWaiting, onWheel,
    ...safeProps
  } = props;

  return (
    <div className={`flex items-start justify-between ${className}`} {...safeProps}>
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
        {subtitle && <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

export { Card, CardHeader };