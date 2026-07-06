'use client';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { label: 'Customers', path: '/customers', icon: '👥' },
  { label: 'Recommendations', path: '/recommendations', icon: '🎯' },
  { label: 'Analytics', path: '/analytics', icon: '📈' },
  { label: 'Admin', path: '/admin', icon: '⚙️' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <aside className="sidebar w-64 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
            <span className="text-[#004B8D] font-black text-sm">H</span>
          </div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">NBA 2.0</h1>
            <p className="text-blue-200 text-xs">AI Product Advisor</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.path || pathname.startsWith(item.path + '/');
          return (
            <button
              key={item.path}
              onClick={() => router.push(item.path)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition ${
                isActive
                  ? 'bg-white/20 text-white font-medium'
                  : 'text-blue-200 hover:bg-white/10 hover:text-white'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="text-sm">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* User Info */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-9 h-9 bg-[#C5A23E] rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">
              {user?.full_name?.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">{user?.full_name}</p>
            <p className="text-blue-300 text-xs">{user?.employee_id}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full text-blue-200 hover:text-white text-sm py-2 rounded-lg hover:bg-white/10 transition"
        >
          Sign Out
        </button>
      </div>
    </aside>
  );
}
