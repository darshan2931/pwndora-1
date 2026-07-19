import Sidebar from '@/components/shared/Sidebar';
import TopBar from '@/components/shared/TopBar';
import AuthProvider from '@/components/providers/AuthProvider';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-[#09090b]">
        <Sidebar />
        <TopBar />
        <main className="ml-56 pt-14 min-h-screen">
          <div className="p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </AuthProvider>
  );
}
