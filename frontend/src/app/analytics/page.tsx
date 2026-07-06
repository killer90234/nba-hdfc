'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import AppShell from '@/components/AppShell';

export default function AnalyticsPage() {
  return <AppShell><AnalyticsContent /></AppShell>;
}

function AnalyticsContent() {
  const [conversion, setConversion] = useState<any[]>([]);
  const [rmPerformance, setRmPerformance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getConversionAnalytics(), api.getRMPerformance()])
      .then(([c, r]) => { setConversion(c); setRmPerformance(r); })
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
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-500 text-sm mt-1">Product conversion and RM performance</p>
      </div>

      {/* Product Conversion */}
      <div className="bg-white rounded-xl card-shadow">
        <div className="p-5 border-b">
          <h3 className="font-semibold text-gray-800">Product Conversion Rates</h3>
        </div>
        <div className="p-5">
          {conversion.length > 0 ? (
            <div className="space-y-4">
              {conversion.map((c, i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className="w-48 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{c.product_name}</p>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-100 rounded-full h-3">
                        <div
                          className="bg-[#004B8D] h-3 rounded-full transition-all"
                          style={{ width: `${c.conversion_rate}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-700 w-12 text-right">{c.conversion_rate}%</span>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 w-32 text-right">
                    {c.applied}/{c.total_recommended} applied
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">No conversion data yet</p>
          )}
        </div>
      </div>

      {/* RM Performance */}
      <div className="bg-white rounded-xl card-shadow">
        <div className="p-5 border-b">
          <h3 className="font-semibold text-gray-800">Relationship Manager Performance</h3>
        </div>
        <div className="p-5">
          {rmPerformance.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-xs text-gray-500 border-b">
                    <th className="pb-3 font-medium">RM</th>
                    <th className="pb-3 font-medium">Employee ID</th>
                    <th className="pb-3 font-medium text-right">Total Recs</th>
                    <th className="pb-3 font-medium text-right">Accepted</th>
                    <th className="pb-3 font-medium text-right">Conversion</th>
                    <th className="pb-3 font-medium text-right">Avg Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {rmPerformance.map((rm, i) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-[#004B8D]/10 rounded-full flex items-center justify-center">
                            <span className="text-[#004B8D] font-bold text-xs">
                              {rm.name?.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                            </span>
                          </div>
                          <span className="text-sm font-medium text-gray-800">{rm.name}</span>
                        </div>
                      </td>
                      <td className="py-3 text-sm text-gray-600">{rm.employee_id}</td>
                      <td className="py-3 text-sm text-gray-800 text-right">{rm.total_recommendations}</td>
                      <td className="py-3 text-sm text-green-600 text-right font-medium">{rm.accepted}</td>
                      <td className="py-3 text-right">
                        <span className={`text-sm font-medium ${
                          rm.conversion_rate >= 50 ? 'text-green-600' :
                          rm.conversion_rate >= 25 ? 'text-amber-600' : 'text-red-600'
                        }`}>{rm.conversion_rate}%</span>
                      </td>
                      <td className="py-3 text-sm text-gray-700 text-right">{rm.avg_confidence}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">No RM performance data yet</p>
          )}
        </div>
      </div>
    </div>
  );
}
