'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import AppShell from '@/components/AppShell';

export default function AdminPage() {
  return <AppShell><AdminContent /></AppShell>;
}

function AdminContent() {
  const [products, setProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [seedMessage, setSeedMessage] = useState('');

  useEffect(() => {
    Promise.all([api.listProducts(), api.getCategories()])
      .then(([p, c]) => { setProducts(p); setCategories(c); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSeed = async () => {
    setSeeding(true);
    setSeedMessage('');
    try {
      const res = await api.seedProducts();
      setSeedMessage(res.message);
      const [p, c] = await Promise.all([api.listProducts(), api.getCategories()]);
      setProducts(p);
      setCategories(c);
    } catch (err: any) {
      setSeedMessage(err.message);
    } finally {
      setSeeding(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-[#004B8D] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-500 text-sm mt-1">Product catalogue and system configuration</p>
        </div>
        <button
          onClick={handleSeed}
          disabled={seeding}
          className="bg-[#004B8D] hover:bg-[#003366] text-white px-5 py-2.5 rounded-lg font-medium transition disabled:opacity-50"
        >
          {seeding ? 'Seeding...' : '🌱 Seed HDFC Products'}
        </button>
      </div>

      {seedMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
          {seedMessage}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 card-shadow">
          <p className="text-sm text-gray-500">Total Products</p>
          <p className="text-2xl font-bold text-gray-900">{products.length}</p>
        </div>
        {categories.map((cat) => (
          <div key={cat} className="bg-white rounded-xl p-5 card-shadow">
            <p className="text-sm text-gray-500 capitalize">{cat.replace('_', ' ')}</p>
            <p className="text-2xl font-bold text-[#004B8D]">
              {products.filter(p => p.category === cat).length}
            </p>
          </div>
        ))}
      </div>

      {/* Product Catalogue */}
      <div className="bg-white rounded-xl card-shadow">
        <div className="p-5 border-b">
          <h3 className="font-semibold text-gray-800">HDFC Product Catalogue</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs text-gray-500 border-b bg-gray-50">
                <th className="px-5 py-3 font-medium">Product</th>
                <th className="px-5 py-3 font-medium">Category</th>
                <th className="px-5 py-3 font-medium">Min Income</th>
                <th className="px-5 py-3 font-medium">Min Credit</th>
                <th className="px-5 py-3 font-medium">Interest Rate</th>
                <th className="px-5 py-3 font-medium">Premium</th>
                <th className="px-5 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {products.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50 transition">
                  <td className="px-5 py-3">
                    <p className="text-sm font-medium text-gray-800">{p.name}</p>
                    <p className="text-xs text-gray-500">{p.subcategory || '-'}</p>
                  </td>
                  <td className="px-5 py-3">
                    <span className="px-2 py-1 bg-[#004B8D]/10 text-[#004B8D] rounded text-xs font-medium capitalize">
                      {p.category?.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-700">
                    {p.min_income ? `₹${(p.min_income / 100000).toFixed(1)}L` : '-'}
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-700">
                    {p.min_credit_score || '-'}
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-700">
                    {p.interest_rate ? `${p.interest_rate}%` : '-'}
                  </td>
                  <td className="px-5 py-3">
                    {p.is_premium ? (
                      <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-medium">Premium</span>
                    ) : (
                      <span className="text-gray-400 text-xs">Standard</span>
                    )}
                  </td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      p.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {p.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {products.length === 0 && (
            <div className="p-12 text-center text-gray-400">
              <p>No products in catalogue. Click "Seed HDFC Products" to populate.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
