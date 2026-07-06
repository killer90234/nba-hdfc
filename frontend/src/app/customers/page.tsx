'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';
import AppShell from '@/components/AppShell';

export default function CustomersPage() {
  return <AppShell><CustomersContent /></AppShell>;
}

function CustomersContent() {
  const [search, setSearch] = useState('');
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    full_name: '', age: '', gender: '', occupation: '', employer: '',
    annual_income: '', education: '', marital_status: '', city: '',
    mobile: '', email: '', pan_number: '', risk_appetite: 'moderate',
  });
  const router = useRouter();

  const handleSearch = async (query?: string) => {
    const searchTerm = query !== undefined ? query : search;
    setLoading(true);
    try {
      const results = await api.searchCustomers(searchTerm);
      setCustomers(results);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch('');
  }, []);

  useEffect(() => {
    const debounce = setTimeout(() => {
      handleSearch();
    }, 400);
    return () => clearTimeout(debounce);
  }, [search]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = {
        ...form,
        age: form.age ? parseInt(form.age) : null,
        annual_income: form.annual_income ? parseFloat(form.annual_income) : null,
      };
      const customer = await api.createCustomer(data);
      setShowCreate(false);
      setForm({
        full_name: '', age: '', gender: '', occupation: '', employer: '',
        annual_income: '', education: '', marital_status: '', city: '',
        mobile: '', email: '', pan_number: '', risk_appetite: 'moderate',
      });
      router.push(`/customers/${customer.customer_id}`);
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
          <p className="text-gray-500 text-sm mt-1">Search or create customer profiles</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="bg-[#004B8D] hover:bg-[#003366] text-white px-5 py-2.5 rounded-lg font-medium transition"
        >
          {showCreate ? 'Cancel' : '+ New Customer'}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="bg-white rounded-xl p-6 card-shadow">
          <h3 className="font-semibold text-gray-800 mb-4">Create New Customer</h3>
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input label="Full Name *" value={form.full_name} onChange={(v: string) => setForm({ ...form, full_name: v })} required />
            <Input label="Age" type="number" value={form.age} onChange={(v: string) => setForm({ ...form, age: v })} />
            <Select label="Gender" value={form.gender} onChange={(v: string) => setForm({ ...form, gender: v })} options={['Male', 'Female', 'Other']} />
            <Input label="Occupation" value={form.occupation} onChange={(v: string) => setForm({ ...form, occupation: v })} />
            <Input label="Employer" value={form.employer} onChange={(v: string) => setForm({ ...form, employer: v })} />
            <Input label="Annual Income (₹)" type="number" value={form.annual_income} onChange={(v: string) => setForm({ ...form, annual_income: v })} />
            <Input label="Education" value={form.education} onChange={(v: string) => setForm({ ...form, education: v })} />
            <Select label="Marital Status" value={form.marital_status} onChange={(v: string) => setForm({ ...form, marital_status: v })} options={['Single', 'Married', 'Divorced', 'Widowed']} />
            <Input label="City" value={form.city} onChange={(v: string) => setForm({ ...form, city: v })} />
            <Input label="Mobile" value={form.mobile} onChange={(v: string) => setForm({ ...form, mobile: v })} />
            <Input label="Email" value={form.email} onChange={(v: string) => setForm({ ...form, email: v })} />
            <Input label="PAN" value={form.pan_number} onChange={(v: string) => setForm({ ...form, pan_number: v.toUpperCase() })} />
            <Select label="Risk Appetite" value={form.risk_appetite} onChange={(v: string) => setForm({ ...form, risk_appetite: v })} options={['conservative', 'moderate', 'aggressive']} />
            <div className="md:col-span-3 flex justify-end">
              <button type="submit" className="bg-[#004B8D] hover:bg-[#003366] text-white px-6 py-2.5 rounded-lg font-medium transition">
                Create Customer
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Search */}
      <div className="bg-white rounded-xl p-4 card-shadow">
        <div className="flex gap-3">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, customer ID, mobile, email, PAN..."
            className="flex-1 px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[#004B8D] focus:border-transparent outline-none"
          />
          <button onClick={handleSearch} className="bg-[#004B8D] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#003366] transition">
            Search
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="bg-white rounded-xl card-shadow">
        {loading ? (
          <div className="p-12 text-center">
            <div className="w-8 h-8 border-4 border-[#004B8D] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-gray-500">Searching...</p>
          </div>
        ) : customers.length > 0 ? (
          <div className="divide-y">
            {customers.map((c) => (
              <button
                key={c.id}
                onClick={() => router.push(`/customers/${c.customer_id}`)}
                className="w-full flex items-center gap-4 p-4 hover:bg-gray-50 transition text-left"
              >
                <div className="w-11 h-11 bg-[#004B8D]/10 rounded-full flex items-center justify-center">
                  <span className="text-[#004B8D] font-bold text-sm">
                    {c.full_name?.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900">{c.full_name}</p>
                  <p className="text-sm text-gray-500">{c.customer_id} • {c.occupation || '-'} • {c.city || '-'}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">₹{c.annual_income ? `${(c.annual_income / 100000).toFixed(1)}L` : '-'}</p>
                  <p className="text-xs text-gray-500">{c.mobile || '-'}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  c.kyc_status === 'verified' ? 'bg-green-100 text-green-700' :
                  c.kyc_status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {c.kyc_status}
                </span>
              </button>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <p className="text-gray-400">Search for customers to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}

function Input({ label, value, onChange, type = 'text', required = false }: any) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        className="w-full px-3 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[#004B8D] focus:border-transparent outline-none text-sm"
      />
    </div>
  );
}

function Select({ label, value, onChange, options }: any) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[#004B8D] focus:border-transparent outline-none text-sm"
      >
        <option value="">Select...</option>
        {options.map((o: string) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}
