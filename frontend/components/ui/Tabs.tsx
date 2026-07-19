"use client";

import React, { useState } from 'react';

interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, defaultTab, className = '' }) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  return (
    <div className={`w-full ${className}`}>
      <div className="flex w-full items-center justify-start border-b border-[var(--border)] mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              inline-flex items-center justify-center whitespace-nowrap px-4 py-2 text-sm font-medium transition-colors
              ${activeTab === tab.id 
                ? 'border-b-2 border-[var(--primary)] text-[var(--foreground)]' 
                : 'text-[var(--muted-foreground)] hover:text-[var(--foreground)]'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="mt-2">
        {tabs.find(t => t.id === activeTab)?.content}
      </div>
    </div>
  );
};
