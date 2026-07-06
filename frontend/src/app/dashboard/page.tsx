'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';
import AppShell from '@/components/AppShell';

interface Stats {
  total_customers: number;
  today_recommendations: number;
  total_recommendations: number;
  acceptance_rate: number;
  applied_count: number;
  accepted_count: number;
  top_products: { name: string; count: number; avg_confidence: number }[];
  recent_activities: { id: number; product: string; confidence: number; status: string; date: string }[];
}

export default function DashboardPage() {
  return <AppShell><DashboardContent /></AppShell>;
}

function DashboardContent() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    api.getDashboardStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#004B8D] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">HDFC AI Next Best Product Advisor</p>
        </div>
        <button
          onClick={() => router.push('/customers')}
          className="bg-[#004B8D] hover:bg-[#003366] text-white px-5 py-2.5 rounded-lg font-medium transition flex items-center gap-2"
        >
          <span>+</span> New Customer
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Total Customers" value={stats?.total_customers || 0} icon="👥" color="blue" />
        <KPICard title="Today's Recommendations" value={stats?.today_recommendations || 0} icon="🎯" color="green" />
        <KPICard title="Total Recommendations" value={stats?.total_recommendations || 0} icon="📋" color="purple" />
        <KPICard title="Acceptance Rate" value={`${stats?.acceptance_rate || 0}%`} icon="✅" color="gold" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Products */}
        <div className="lg:col-span-1 bg-white rounded-xl p-5 card-shadow">
          <h3 className="font-semibold text-gray-800 mb-4">Top Recommended Products</h3>
          <div className="space-y-3">
            {stats?.top_products.map((p, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-[#004B8D]/10 rounded-lg flex items-center justify-center text-[#004B8D] font-bold text-sm">
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{p.name}</p>
                  <p className="text-xs text-gray-500">{p.count} recommendations</p>
                </div>
                <span className="text-xs font-medium text-green-600">{p.avg_confidence}%</span>
              </div>
            ))}
            {(!stats?.top_products || stats.top_products.length === 0) && (
              <p className="text-gray-400 text-sm text-center py-4">No data yet</p>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="lg:col-span-2 bg-white rounded-xl p-5 card-shadow">
          <h3 className="font-semibold text-gray-800 mb-4">Recent Activity</h3>
          <div className="space-y-2">
            {stats?.recent_activities.map((a) => (
              <div key={a.id} className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition">
                <div className={`w-2 h-2 rounded-full ${
                  a.status === 'accepted' ? 'bg-green-500' :
                  a.status === 'applied' ? 'bg-blue-500' :
                  a.status === 'rejected' ? 'bg-red-500' : 'bg-gray-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-800">{a.product}</p>
                  <p className="text-xs text-gray-500">
                    {a.date ? new Date(a.date).toLocaleDateString() : '-'}
                  </p>
                </div>
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                  a.status === 'accepted' ? 'bg-green-100 text-green-700' :
                  a.status === 'applied' ? 'bg-blue-100 text-blue-700' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {a.status}
                </span>
              </div>
            ))}
            {(!stats?.recent_activities || stats.recent_activities.length === 0) && (
              <p className="text-gray-400 text-sm text-center py-4">No recent activity</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-5 card-shadow">
        <h3 className="font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => router.push('/customers')}
            className="p-4 border-2 border-dashed border-gray-200 rounded-xl hover:border-[#004B8D] hover:bg-[#004B8D]/5 transition text-left"
          >
            <div className="text-2xl mb-2">👤</div>
            <p className="font-medium text-gray-800">Add Customer</p>
            <p className="text-xs text-gray-500">Create new customer profile</p>
          </button>
          <button
            onClick={() => router.push('/customers')}
            className="p-4 border-2 border-dashed border-gray-200 rounded-xl hover:border-green-500 hover:bg-green-50 transition text-left"
          >
            <div className="text-2xl mb-2">🎯</div>
            <p className="font-medium text-gray-800">Get AI Recommendations</p>
            <p className="text-xs text-gray-500">AI-powered product suggestions</p>
          </button>
          <button
            onClick={() => router.push('/analytics')}
            className="p-4 border-2 border-dashed border-gray-200 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition text-left"
          >
            <div className="text-2xl mb-2">📊</div>
            <p className="font-medium text-gray-800">View Analytics</p>
            <p className="text-xs text-gray-500">Performance and conversion data</p>
          </button>
        </div>
      </div>
    </div>
  );
}

function KPICard({ title, value, icon, color }: { title: string; value: any; icon: string; color: string }) {
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-50 text-[#004B8D]',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    gold: 'bg-amber-50 text-amber-600',
  };

  return (
    <div className="bg-white rounded-xl p-5 card-shadow card-hover transition">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl ${colorMap[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
