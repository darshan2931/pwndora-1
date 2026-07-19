'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [pathname, router]);

  if (!mounted) {
    return null; // or a loading spinner
  }

  // Prevent flash of unauthenticated content
  if (!localStorage.getItem('token')) {
    return null;
  }

  return <>{children}</>;
}
