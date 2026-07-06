'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';
import AppShell from '@/components/AppShell';

export default function RecommendationsPage() {
  return <AppShell><RecommendationsContent /></AppShell>;
}

function RecommendationsContent() {
  const [stats, setStats] = useState<any>(null);
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
        <div className="w-12 h-12 border-4 border-[#004B8D] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Recommendations</h1>
        <p className="text-gray-500 text-sm mt-1">All AI-generated product recommendations</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 card-shadow">
          <p className="text-sm text-gray-500">Total Generated</p>
          <p className="text-2xl font-bold text-gray-900">{stats?.total_recommendations || 0}</p>
        </div>
        <div className="bg-white rounded-xl p-5 card-shadow">
          <p className="text-sm text-gray-500">Applied</p>
          <p className="text-2xl font-bold text-blue-600">{stats?.applied_count || 0}</p>
        </div>
        <div className="bg-white rounded-xl p-5 card-shadow">
          <p className="text-sm text-gray-500">Accepted</p>
          <p className="text-2xl font-bold text-green-600">{stats?.accepted_count || 0}</p>
        </div>
        <div className="bg-white rounded-xl p-5 card-shadow">
          <p className="text-sm text-gray-500">Conversion Rate</p>
          <p className="text-2xl font-bold text-[#004B8D]">{stats?.acceptance_rate || 0}%</p>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="bg-white rounded-xl card-shadow">
        <div className="p-5 border-b">
          <h3 className="font-semibold text-gray-800">Recent Recommendations</h3>
        </div>
        <div className="divide-y">
          {stats?.recent_activities?.map((a: any) => (
            <div key={a.id} className="flex items-center gap-4 p-4 hover:bg-gray-50 transition">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                a.confidence >= 90 ? 'bg-green-100' : a.confidence >= 75 ? 'bg-amber-100' : 'bg-red-100'
              }`}>
                <span className={`font-bold text-sm ${
                  a.confidence >= 90 ? 'text-green-600' : a.confidence >= 75 ? 'text-amber-600' : 'text-red-600'
                }`}>{a.confidence}%</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-800">{a.product}</p>
                <p className="text-sm text-gray-500">
                  {a.date ? new Date(a.date).toLocaleString() : '-'}
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                a.status === 'accepted' ? 'bg-green-100 text-green-700' :
                a.status === 'applied' ? 'bg-blue-100 text-blue-700' :
                a.status === 'rejected' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-600'
              }`}>{a.status}</span>
            </div>
          ))}
          {(!stats?.recent_activities || stats.recent_activities.length === 0) && (
            <div className="p-12 text-center text-gray-400">No recommendations yet</div>
          )}
        </div>
      </div>
    </div>
  );
}
