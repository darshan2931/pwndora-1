import React from 'react';
import { Avatar } from '../ui';

export const Topbar: React.FC = () => {
  return (
    <header className="flex h-16 w-full items-center justify-between border-b border-[var(--border)] bg-[var(--background)] px-6">
      <div className="flex items-center">
        {/* Mobile menu toggle could go here */}
        <h2 className="text-lg font-medium text-[var(--foreground)] tracking-tight">Dashboard</h2>
      </div>
      <div className="flex items-center gap-4">
        <button className="text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
          🔔
        </button>
        <Avatar initials="JD" size="sm" />
      </div>
    </header>
  );
};
