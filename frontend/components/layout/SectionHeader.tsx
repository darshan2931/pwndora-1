import React from 'react';

interface SectionHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, description, action, className = '' }) => {
  return (
    <div className={`flex items-center justify-between pb-4 border-b border-[var(--border)] mb-6 ${className}`}>
      <div>
        <h3 className="text-xl font-semibold leading-6 text-[var(--foreground)] tracking-tight">{title}</h3>
        {description && (
          <p className="mt-1 text-sm text-[var(--muted-foreground)]">{description}</p>
        )}
      </div>
      {action && (
        <div className="flex shrink-0 ml-4">
          {action}
        </div>
      )}
    </div>
  );
};
