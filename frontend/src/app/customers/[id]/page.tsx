'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import AppShell from '@/components/AppShell';

type Tab = 'profile' | 'family' | 'employment' | 'banking' | 'products' | 'ai';

export default function CustomerDetailPage() {
  return <AppShell><CustomerDetailContent /></AppShell>;
}

function CustomerDetailContent() {
  const params = useParams();
  const router = useRouter();
  const customerId = params.id as string;

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>('profile');
  const [aiLoading, setAiLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [customerInsights, setCustomerInsights] = useState<any>(null);
  const [hdfcProducts, setHdfcProducts] = useState<any[]>([]);

  const load = async () => {
    try {
      const profile = await api.getCustomer(customerId);
      setData(profile);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadExistingRecs = async () => {
    try {
      const recs = await api.getRecommendations(customerId);
      if (recs && recs.length > 0) {
        setRecommendations(recs);
      }
    } catch (err) {
      console.error('No existing recommendations');
    }
  };

  const loadProducts = async () => {
    try {
      const products = await api.listProducts();
      setHdfcProducts(products);
    } catch (err) {
      console.error('Failed to load products');
    }
  };

  useEffect(() => {
    load();
    loadExistingRecs();
    loadProducts();
  }, [customerId]);

  const generateAI = async () => {
    setAiLoading(true);
    try {
      const res = await api.generateRecommendations(customerId);
      setRecommendations(res.recommendations);
      setCustomerInsights(res.customer_insights);
      setActiveTab('ai');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-[#004B8D] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center py-12 text-gray-500">Customer not found</div>;
  }

  const { customer, family, employment, banking, existing_products } = data;

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'family', label: 'Family', icon: '👨‍👩‍👧' },
    { id: 'employment', label: 'Employment', icon: '💼' },
    { id: 'banking', label: 'Banking', icon: '🏦' },
    { id: 'products', label: 'Products', icon: '📦' },
    { id: 'ai', label: 'AI Insights', icon: '🤖' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => router.back()} className="text-gray-500 hover:text-gray-800 transition">← Back</button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{customer.full_name}</h1>
          <p className="text-gray-500 text-sm">{customer.customer_id} • {customer.occupation || '-'} • {customer.city || '-'}</p>
        </div>
        <button
          onClick={generateAI}
          disabled={aiLoading}
          className="gradient-blue text-white px-6 py-3 rounded-lg font-medium transition flex items-center gap-2 disabled:opacity-50"
        >
          {aiLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Analyzing...
            </>
          ) : (
            <>🤖 Generate AI Recommendations</>
          )}
        </button>
      </div>

      <div className="bg-white rounded-xl card-shadow">
        <div className="flex border-b overflow-x-auto scrollbar-hide">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-3.5 text-sm font-medium whitespace-nowrap transition border-b-2 ${
                activeTab === tab.id
                  ? 'border-[#004B8D] text-[#004B8D]'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
              {tab.id === 'ai' && recommendations.length > 0 && (
                <span className="bg-[#004B8D] text-white text-xs px-1.5 py-0.5 rounded-full">{recommendations.length}</span>
              )}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === 'profile' && <ProfileTab data={customer} customerId={customerId} reload={load} />}
          {activeTab === 'family' && <FamilyTab data={family} customerId={customerId} reload={load} />}
          {activeTab === 'employment' && <EmploymentTab data={employment} customerId={customerId} reload={load} />}
          {activeTab === 'banking' && <BankingTab data={banking} customerId={customerId} reload={load} />}
          {activeTab === 'products' && <ProductsTab data={existing_products} customerId={customerId} reload={load} hdfcProducts={hdfcProducts} />}
          {activeTab === 'ai' && <AITab recommendations={recommendations} insights={customerInsights} loading={aiLoading} customerId={customerId} />}
        </div>
      </div>
    </div>
  );
}

function ProfileTab({ data, customerId, reload }: { data: any; customerId: string; reload: () => void }) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    full_name: data?.full_name || '',
    age: data?.age || '',
    gender: data?.gender || '',
    occupation: data?.occupation || '',
    employer: data?.employer || '',
    annual_income: data?.annual_income || '',
    education: data?.education || '',
    marital_status: data?.marital_status || '',
    city: data?.city || '',
    state: data?.state || '',
    mobile: data?.mobile || '',
    email: data?.email || '',
    pan_number: data?.pan_number || '',
    risk_appetite: data?.risk_appetite || 'moderate',
  });

  const handleSave = async () => {
    try {
      await api.updateCustomer(customerId, {
        ...form,
        age: form.age ? Number(form.age) : null,
        annual_income: form.annual_income ? Number(form.annual_income) : null,
      });
      setEditing(false);
      reload();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (editing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">Edit Profile</h3>
          <div className="flex gap-2">
            <button onClick={() => setEditing(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm">Cancel</button>
            <button onClick={handleSave} className="px-4 py-2 bg-[#004B8D] text-white rounded-lg text-sm font-medium">Save</button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Field label="Full Name" value={form.full_name} onChange={(v: string) => setForm({ ...form, full_name: v })} />
          <Field label="Age" type="number" value={form.age} onChange={(v: string) => setForm({ ...form, age: v })} />
          <SelectField label="Gender" value={form.gender} onChange={(v: string) => setForm({ ...form, gender: v })} options={['Male', 'Female', 'Other']} />
          <Field label="Occupation" value={form.occupation} onChange={(v: string) => setForm({ ...form, occupation: v })} />
          <Field label="Employer" value={form.employer} onChange={(v: string) => setForm({ ...form, employer: v })} />
          <Field label="Annual Income (₹)" type="number" value={form.annual_income} onChange={(v: string) => setForm({ ...form, annual_income: v })} />
          <Field label="Education" value={form.education} onChange={(v: string) => setForm({ ...form, education: v })} />
          <SelectField label="Marital Status" value={form.marital_status} onChange={(v: string) => setForm({ ...form, marital_status: v })} options={['Single', 'Married', 'Divorced', 'Widowed']} />
          <Field label="City" value={form.city} onChange={(v: string) => setForm({ ...form, city: v })} />
          <Field label="State" value={form.state} onChange={(v: string) => setForm({ ...form, state: v })} />
          <Field label="Mobile" value={form.mobile} onChange={(v: string) => setForm({ ...form, mobile: v })} />
          <Field label="Email" value={form.email} onChange={(v: string) => setForm({ ...form, email: v })} />
          <Field label="PAN" value={form.pan_number} onChange={(v: string) => setForm({ ...form, pan_number: v.toUpperCase() })} />
          <SelectField label="Risk Appetite" value={form.risk_appetite} onChange={(v: string) => setForm({ ...form, risk_appetite: v })} options={['conservative', 'moderate', 'aggressive']} />
        </div>
      </div>
    );
  }

  const fields = [
    ['Full Name', data.full_name],
    ['Age', data.age],
    ['Gender', data.gender],
    ['DOB', data.date_of_birth ? new Date(data.date_of_birth).toLocaleDateString() : '-'],
    ['Occupation', data.occupation],
    ['Employer', data.employer],
    ['Annual Income', data.annual_income ? `₹${(data.annual_income / 100000).toFixed(1)}L` : '-'],
    ['Education', data.education],
    ['Marital Status', data.marital_status],
    ['City', data.city],
    ['State', data.state],
    ['Mobile', data.mobile],
    ['Email', data.email],
    ['PAN', data.pan_number],
    ['KYC Status', data.kyc_status],
    ['Risk Appetite', data.risk_appetite],
  ];
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">Personal Details</h3>
        <button onClick={() => setEditing(true)} className="text-[#004B8D] font-medium text-sm hover:underline">Edit</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {fields.map(([label, value]) => (
          <div key={String(label)} className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">{label}</p>
            <p className="text-sm font-medium text-gray-800">{value || '-'}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function FamilyTab({ data, customerId, reload }: { data: any; customerId: string; reload: () => void }) {
  const [editing, setEditing] = useState(!data);
  const [form, setForm] = useState({
    father_name: data?.father_name || '',
    father_age: data?.father_age || '',
    mother_name: data?.mother_name || '',
    mother_age: data?.mother_age || '',
    spouse_name: data?.spouse_name || '',
    spouse_age: data?.spouse_age || '',
    spouse_occupation: data?.spouse_occupation || '',
    num_children: data?.num_children || 0,
    child1_age: data?.child1_age || '',
    child1_education: data?.child1_education || '',
    child2_age: data?.child2_age || '',
    child2_education: data?.child2_education || '',
    family_income: data?.family_income || '',
    family_assets: data?.family_assets || '',
    family_investments: data?.family_investments || '',
    family_insurance_value: data?.family_insurance_value || '',
    family_goals: data?.family_goals || '',
    dependent_parents: data?.dependent_parents || false,
    parents_senior_citizen: data?.parents_senior_citizen || false,
  });

  const handleSave = async () => {
    try {
      await api.upsertFamily(customerId, {
        ...form,
        father_age: form.father_age ? Number(form.father_age) : null,
        mother_age: form.mother_age ? Number(form.mother_age) : null,
        spouse_age: form.spouse_age ? Number(form.spouse_age) : null,
        num_children: Number(form.num_children),
        child1_age: form.child1_age ? Number(form.child1_age) : null,
        child2_age: form.child2_age ? Number(form.child2_age) : null,
        family_income: form.family_income ? Number(form.family_income) : null,
        family_assets: form.family_assets ? Number(form.family_assets) : null,
        family_investments: form.family_investments ? Number(form.family_investments) : null,
        family_insurance_value: form.family_insurance_value ? Number(form.family_insurance_value) : null,
      });
      setEditing(false);
      reload();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (editing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">{data ? 'Edit' : 'Add'} Family Details</h3>
          <div className="flex gap-2">
            {data && <button onClick={() => setEditing(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm">Cancel</button>}
            <button onClick={handleSave} className="px-4 py-2 bg-[#004B8D] text-white rounded-lg text-sm font-medium">Save</button>
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-700 mb-3">Parents</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Field label="Father Name" value={form.father_name} onChange={(v: string) => setForm({ ...form, father_name: v })} />
            <Field label="Father Age" type="number" value={form.father_age} onChange={(v: string) => setForm({ ...form, father_age: v })} />
            <Field label="Mother Name" value={form.mother_name} onChange={(v: string) => setForm({ ...form, mother_name: v })} />
            <Field label="Mother Age" type="number" value={form.mother_age} onChange={(v: string) => setForm({ ...form, mother_age: v })} />
            <CheckboxField label="Dependent Parents" checked={form.dependent_parents} onChange={(v: boolean) => setForm({ ...form, dependent_parents: v })} />
            <CheckboxField label="Parents Senior Citizen" checked={form.parents_senior_citizen} onChange={(v: boolean) => setForm({ ...form, parents_senior_citizen: v })} />
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-700 mb-3">Spouse</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Field label="Spouse Name" value={form.spouse_name} onChange={(v: string) => setForm({ ...form, spouse_name: v })} />
            <Field label="Spouse Age" type="number" value={form.spouse_age} onChange={(v: string) => setForm({ ...form, spouse_age: v })} />
            <Field label="Spouse Occupation" value={form.spouse_occupation} onChange={(v: string) => setForm({ ...form, spouse_occupation: v })} />
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-700 mb-3">Children</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Field label="Number of Children" type="number" value={form.num_children} onChange={(v: string) => setForm({ ...form, num_children: Number(v) })} />
            <Field label="Child 1 Age" type="number" value={form.child1_age} onChange={(v: string) => setForm({ ...form, child1_age: v })} />
            <Field label="Child 1 Education" value={form.child1_education} onChange={(v: string) => setForm({ ...form, child1_education: v })} />
            <Field label="Child 2 Age" type="number" value={form.child2_age} onChange={(v: string) => setForm({ ...form, child2_age: v })} />
            <Field label="Child 2 Education" value={form.child2_education} onChange={(v: string) => setForm({ ...form, child2_education: v })} />
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-700 mb-3">Financial</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Field label="Family Income (₹)" type="number" value={form.family_income} onChange={(v: string) => setForm({ ...form, family_income: v })} />
            <Field label="Family Assets (₹)" type="number" value={form.family_assets} onChange={(v: string) => setForm({ ...form, family_assets: v })} />
            <Field label="Family Investments (₹)" type="number" value={form.family_investments} onChange={(v: string) => setForm({ ...form, family_investments: v })} />
            <Field label="Family Insurance (₹)" type="number" value={form.family_insurance_value} onChange={(v: string) => setForm({ ...form, family_insurance_value: v })} />
            <div className="md:col-span-2">
              <Field label="Family Goals" value={form.family_goals} onChange={(v: string) => setForm({ ...form, family_goals: v })} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) return <EmptyStateWithAdd message="No family details" onAdd={() => setEditing(true)} />;

  const fields = [
    ['Father', data.father_name, data.father_age ? `(${data.father_age})` : ''],
    ['Mother', data.mother_name, data.mother_age ? `(${data.mother_age})` : ''],
    ['Spouse', data.spouse_name, data.spouse_age ? `(${data.spouse_age})` : ''],
    ['Children', data.num_children || 0, ''],
    ['Child 1', data.child1_age ? `Age ${data.child1_age}` : '-', data.child1_education],
    ['Child 2', data.child2_age ? `Age ${data.child2_age}` : '-', data.child2_education],
    ['Family Income', data.family_income ? `₹${(data.family_income / 100000).toFixed(1)}L` : '-'],
    ['Family Assets', data.family_assets ? `₹${(data.family_assets / 100000).toFixed(1)}L` : '-'],
    ['Family Investments', data.family_investments ? `₹${(data.family_investments / 100000).toFixed(1)}L` : '-'],
    ['Family Insurance', data.family_insurance_value ? `₹${(data.family_insurance_value / 100000).toFixed(1)}L` : '-'],
    ['Dependent Parents', data.dependent_parents ? 'Yes' : 'No'],
    ['Parents Senior Citizen', data.parents_senior_citizen ? 'Yes' : 'No'],
    ['Family Goals', data.family_goals],
  ];
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">Family Details</h3>
        <button onClick={() => setEditing(true)} className="text-[#004B8D] font-medium text-sm hover:underline">Edit</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {fields.map(([label, value, sub]) => (
          <div key={String(label)} className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">{label}</p>
            <p className="text-sm font-medium text-gray-800">{value || '-'}</p>
            {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

function EmploymentTab({ data, customerId, reload }: { data: any; customerId: string; reload: () => void }) {
  const [editing, setEditing] = useState(!data);
  const [form, setForm] = useState({
    employment_type: data?.employment_type || '',
    monthly_income: data?.monthly_income || '',
    monthly_expenses: data?.monthly_expenses || '',
    salary_date: data?.salary_date || '',
    years_in_job: data?.years_in_job || '',
    company_category: data?.company_category || '',
    business_turnover: data?.business_turnover || '',
    gst_registered: data?.gst_registered || false,
    credit_score: data?.credit_score || '',
  });

  const handleSave = async () => {
    try {
      await api.upsertEmployment(customerId, {
        ...form,
        monthly_income: form.monthly_income ? Number(form.monthly_income) : null,
        monthly_expenses: form.monthly_expenses ? Number(form.monthly_expenses) : null,
        salary_date: form.salary_date ? Number(form.salary_date) : null,
        years_in_job: form.years_in_job ? Number(form.years_in_job) : null,
        business_turnover: form.business_turnover ? Number(form.business_turnover) : null,
        credit_score: form.credit_score ? Number(form.credit_score) : null,
      });
      setEditing(false);
      reload();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (editing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">{data ? 'Edit' : 'Add'} Employment Details</h3>
          <div className="flex gap-2">
            {data && <button onClick={() => setEditing(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm">Cancel</button>}
            <button onClick={handleSave} className="px-4 py-2 bg-[#004B8D] text-white rounded-lg text-sm font-medium">Save</button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SelectField label="Employment Type" value={form.employment_type} onChange={(v: string) => setForm({ ...form, employment_type: v })} options={['government', 'private', 'business', 'self_employed', 'professional', 'retired', 'student']} />
          <Field label="Monthly Income (₹)" type="number" value={form.monthly_income} onChange={(v: string) => setForm({ ...form, monthly_income: v })} />
          <Field label="Monthly Expenses (₹)" type="number" value={form.monthly_expenses} onChange={(v: string) => setForm({ ...form, monthly_expenses: v })} />
          <Field label="Salary Date (Day)" type="number" value={form.salary_date} onChange={(v: string) => setForm({ ...form, salary_date: v })} />
          <Field label="Years in Job" type="number" value={form.years_in_job} onChange={(v: string) => setForm({ ...form, years_in_job: v })} />
          <SelectField label="Company Category" value={form.company_category} onChange={(v: string) => setForm({ ...form, company_category: v })} options={['MNC', 'PSU', 'Startup', 'MSME', 'Government', 'Other']} />
          <Field label="Business Turnover (₹)" type="number" value={form.business_turnover} onChange={(v: string) => setForm({ ...form, business_turnover: v })} />
          <Field label="Credit Score" type="number" value={form.credit_score} onChange={(v: string) => setForm({ ...form, credit_score: v })} />
            <CheckboxField label="GST Registered" checked={form.gst_registered} onChange={(v: boolean) => setForm({ ...form, gst_registered: v })} />
        </div>
      </div>
    );
  }

  if (!data) return <EmptyStateWithAdd message="No employment details" onAdd={() => setEditing(true)} />;

  const fields = [
    ['Employment Type', data.employment_type],
    ['Monthly Income', data.monthly_income ? `₹${data.monthly_income.toLocaleString()}` : '-'],
    ['Monthly Expenses', data.monthly_expenses ? `₹${data.monthly_expenses.toLocaleString()}` : '-'],
    ['Salary Date', data.salary_date ? `Day ${data.salary_date}` : '-'],
    ['Years in Job', data.years_in_job],
    ['Company Category', data.company_category],
    ['Business Turnover', data.business_turnover ? `₹${(data.business_turnover / 100000).toFixed(1)}L` : '-'],
    ['GST Registered', data.gst_registered ? 'Yes' : 'No'],
    ['Credit Score', data.credit_score],
  ];
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">Employment Details</h3>
        <button onClick={() => setEditing(true)} className="text-[#004B8D] font-medium text-sm hover:underline">Edit</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {fields.map(([label, value]) => (
          <div key={String(label)} className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">{label}</p>
            <p className={`text-sm font-medium ${
              label === 'Credit Score' && value
                ? Number(value) >= 750 ? 'text-green-600' : Number(value) >= 650 ? 'text-amber-600' : 'text-red-600'
                : 'text-gray-800'
            }`}>{value || '-'}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function BankingTab({ data, customerId, reload }: { data: any; customerId: string; reload: () => void }) {
  const [editing, setEditing] = useState(!data);
  const [form, setForm] = useState({
    has_savings_account: data?.has_savings_account || false,
    has_salary_account: data?.has_salary_account || false,
    has_current_account: data?.has_current_account || false,
    current_balance: data?.current_balance || '',
    average_balance: data?.average_balance || '',
    salary_credit: data?.salary_credit || '',
    monthly_debit: data?.monthly_debit || '',
    monthly_credit: data?.monthly_credit || '',
    upi_monthly: data?.upi_monthly || '',
    fd_amount: data?.fd_amount || '',
    rd_amount: data?.rd_amount || '',
    atm_usage_monthly: data?.atm_usage_monthly || '',
  });

  const handleSave = async () => {
    try {
      await api.upsertBanking(customerId, {
        ...form,
        current_balance: form.current_balance ? Number(form.current_balance) : 0,
        average_balance: form.average_balance ? Number(form.average_balance) : 0,
        salary_credit: form.salary_credit ? Number(form.salary_credit) : 0,
        monthly_debit: form.monthly_debit ? Number(form.monthly_debit) : 0,
        monthly_credit: form.monthly_credit ? Number(form.monthly_credit) : 0,
        upi_monthly: form.upi_monthly ? Number(form.upi_monthly) : 0,
        fd_amount: form.fd_amount ? Number(form.fd_amount) : 0,
        rd_amount: form.rd_amount ? Number(form.rd_amount) : 0,
        atm_usage_monthly: form.atm_usage_monthly ? Number(form.atm_usage_monthly) : 0,
      });
      setEditing(false);
      reload();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (editing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">{data ? 'Edit' : 'Add'} Banking Details</h3>
          <div className="flex gap-2">
            {data && <button onClick={() => setEditing(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm">Cancel</button>}
            <button onClick={handleSave} className="px-4 py-2 bg-[#004B8D] text-white rounded-lg text-sm font-medium">Save</button>
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-700 mb-3">Accounts</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <CheckboxField label="Savings Account" checked={form.has_savings_account} onChange={(v: boolean) => setForm({ ...form, has_savings_account: v })} />
            <CheckboxField label="Salary Account" checked={form.has_salary_account} onChange={(v: boolean) => setForm({ ...form, has_salary_account: v })} />
            <CheckboxField label="Current Account" checked={form.has_current_account} onChange={(v: boolean) => setForm({ ...form, has_current_account: v })} />
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-700 mb-3">Balances & Transactions</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Field label="Current Balance (₹)" type="number" value={form.current_balance} onChange={(v: string) => setForm({ ...form, current_balance: v })} />
            <Field label="Average Balance (₹)" type="number" value={form.average_balance} onChange={(v: string) => setForm({ ...form, average_balance: v })} />
            <Field label="Salary Credit (₹)" type="number" value={form.salary_credit} onChange={(v: string) => setForm({ ...form, salary_credit: v })} />
            <Field label="Monthly Debit (₹)" type="number" value={form.monthly_debit} onChange={(v: string) => setForm({ ...form, monthly_debit: v })} />
            <Field label="Monthly Credit (₹)" type="number" value={form.monthly_credit} onChange={(v: string) => setForm({ ...form, monthly_credit: v })} />
            <Field label="UPI Monthly (₹)" type="number" value={form.upi_monthly} onChange={(v: string) => setForm({ ...form, upi_monthly: v })} />
            <Field label="FD Amount (₹)" type="number" value={form.fd_amount} onChange={(v: string) => setForm({ ...form, fd_amount: v })} />
            <Field label="RD Amount (₹)" type="number" value={form.rd_amount} onChange={(v: string) => setForm({ ...form, rd_amount: v })} />
            <Field label="ATM Usage/Month" type="number" value={form.atm_usage_monthly} onChange={(v: string) => setForm({ ...form, atm_usage_monthly: v })} />
          </div>
        </div>
      </div>
    );
  }

  if (!data) return <EmptyStateWithAdd message="No banking details" onAdd={() => setEditing(true)} />;

  const fields = [
    ['Savings Account', data.has_savings_account],
    ['Salary Account', data.has_salary_account],
    ['Current Account', data.has_current_account],
    ['Current Balance', data.current_balance ? `₹${data.current_balance.toLocaleString()}` : '-'],
    ['Average Balance', data.average_balance ? `₹${data.average_balance.toLocaleString()}` : '-'],
    ['Salary Credit', data.salary_credit ? `₹${data.salary_credit.toLocaleString()}` : '-'],
    ['Monthly Debit', data.monthly_debit ? `₹${data.monthly_debit.toLocaleString()}` : '-'],
    ['Monthly Credit', data.monthly_credit ? `₹${data.monthly_credit.toLocaleString()}` : '-'],
    ['UPI Monthly', data.upi_monthly ? `₹${data.upi_monthly.toLocaleString()}` : '-'],
    ['FD Amount', data.fd_amount ? `₹${data.fd_amount.toLocaleString()}` : '-'],
    ['RD Amount', data.rd_amount ? `₹${data.rd_amount.toLocaleString()}` : '-'],
    ['ATM Usage', data.atm_usage_monthly ? `${data.atm_usage_monthly}/month` : '-'],
  ];
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">Banking Details</h3>
        <button onClick={() => setEditing(true)} className="text-[#004B8D] font-medium text-sm hover:underline">Edit</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {fields.map(([label, value]) => (
          <div key={String(label)} className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">{label}</p>
            <p className={`text-sm font-medium ${
              typeof value === 'boolean' ? value ? 'text-green-600' : 'text-gray-400'
              : 'text-gray-800'
            }`}>{typeof value === 'boolean' ? (value ? 'Yes' : 'No') : (value || '-')}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProductsTab({ data, customerId, reload, hdfcProducts }: { data: any[]; customerId: string; reload: () => void; hdfcProducts: any[] }) {
  const [showAdd, setShowAdd] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [customName, setCustomName] = useState('');
  const [useCustom, setUseCustom] = useState(false);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (useCustom) {
        await api.addExistingProduct(customerId, {
          product_id: 0,
          product_name: customName,
          product_category: '',
          account_number: accountNumber,
        });
      } else {
        const product = hdfcProducts.find((p: any) => p.id === Number(selectedProductId));
        if (!product) return alert('Select a product');
        await api.addExistingProduct(customerId, {
          product_id: product.id,
          product_name: product.name,
          product_category: product.category,
          account_number: accountNumber,
        });
      }
      setShowAdd(false);
      setSelectedProductId('');
      setAccountNumber('');
      setCustomName('');
      reload();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRemove = async (productId: number) => {
    if (!confirm('Remove this product?')) return;
    try {
      await api.removeExistingProduct(customerId, productId);
      reload();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const categories = Array.from(new Set(hdfcProducts.map((p: any) => p.category)));
  const [filterCategory, setFilterCategory] = useState('');
  const filteredProducts = filterCategory
    ? hdfcProducts.filter((p: any) => p.category === filterCategory)
    : hdfcProducts;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">{data?.length || 0} existing HDFC products</p>
        <button onClick={() => setShowAdd(!showAdd)} className="text-[#004B8D] font-medium text-sm hover:underline">
          {showAdd ? 'Cancel' : '+ Add HDFC Product'}
        </button>
      </div>

      {showAdd && (
        <form onSubmit={handleAdd} className="bg-gray-50 rounded-lg p-4 mb-4 space-y-3">
          <div className="flex gap-2 mb-2">
            <button type="button" onClick={() => setUseCustom(false)} className={`px-3 py-1.5 rounded-lg text-sm font-medium ${!useCustom ? 'bg-[#004B8D] text-white' : 'bg-white text-gray-600 border'}`}>
              HDFC Product
            </button>
            <button type="button" onClick={() => setUseCustom(true)} className={`px-3 py-1.5 rounded-lg text-sm font-medium ${useCustom ? 'bg-[#004B8D] text-white' : 'bg-white text-gray-600 border'}`}>
              Custom Product
            </button>
          </div>

          {!useCustom ? (
            <div className="flex gap-3">
              <select
                value={filterCategory}
                onChange={(e) => { setFilterCategory(e.target.value); setSelectedProductId(''); }}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-[#004B8D]"
              >
                <option value="">All Categories</option>
                {categories.map((cat: string) => (
                  <option key={cat} value={cat}>{cat.replace('_', ' ').toUpperCase()}</option>
                ))}
              </select>
              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-[#004B8D]"
                required
              >
                <option value="">Select HDFC Product...</option>
                {filteredProducts.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.name} ({p.category.replace('_', ' ')})</option>
                ))}
              </select>
            </div>
          ) : (
            <input
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder="Product name (e.g. HDFC Savings Account)"
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-[#004B8D]"
              required
            />
          )}

          <div className="flex gap-3">
            <input
              value={accountNumber}
              onChange={(e) => setAccountNumber(e.target.value)}
              placeholder="Account/Card Number (optional)"
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-[#004B8D]"
            />
            <button type="submit" className="bg-[#004B8D] text-white px-6 py-2 rounded-lg text-sm font-medium">Add</button>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {data?.map((p: any) => {
          const catColors: Record<string, string> = {
            accounts: 'bg-blue-100 text-blue-700',
            credit_cards: 'bg-purple-100 text-purple-700',
            loans: 'bg-red-100 text-red-700',
            investments: 'bg-green-100 text-green-700',
            insurance: 'bg-amber-100 text-amber-700',
            digital: 'bg-cyan-100 text-cyan-700',
          };
          return (
            <div key={p.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-[#004B8D]/10 rounded-lg flex items-center justify-center text-lg">
                {p.product_category === 'accounts' ? '🏦' :
                 p.product_category === 'credit_cards' ? '💳' :
                 p.product_category === 'loans' ? '📋' :
                 p.product_category === 'investments' ? '📈' :
                 p.product_category === 'insurance' ? '🛡️' :
                 p.product_category === 'digital' ? '📱' : '📦'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800">{p.product_name}</p>
                <div className="flex items-center gap-2 mt-0.5">
                  {p.product_category && (
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${catColors[p.product_category] || 'bg-gray-100 text-gray-600'}`}>
                      {p.product_category.replace('_', ' ')}
                    </span>
                  )}
                  {p.account_number && <span className="text-xs text-gray-400">• {p.account_number}</span>}
                  <span className="text-xs text-gray-400">• {p.status}</span>
                </div>
              </div>
              <button onClick={() => handleRemove(p.id)} className="text-red-400 hover:text-red-600 text-sm px-2">✕</button>
            </div>
          );
        })}
        {(!data || data.length === 0) && <EmptyState message="No existing products added" />}
      </div>
    </div>
  );
}

function AITab({ recommendations, insights, loading, customerId }: { recommendations: any[]; insights: any; loading: boolean; customerId: string }) {
  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="w-12 h-12 border-4 border-[#004B8D] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-500 font-medium">AI is analyzing customer profile...</p>
        <p className="text-gray-400 text-sm mt-1">Applying rule engine + AI analysis + eligibility checks</p>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-5xl mb-4">🤖</div>
        <p className="text-gray-500 font-medium">No AI recommendations yet</p>
        <p className="text-gray-400 text-sm mt-1">Click "Generate AI Recommendations" button above to get started</p>
      </div>
    );
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-50';
    if (score >= 75) return 'text-amber-600 bg-amber-50';
    return 'text-red-600 bg-red-50';
  };

  const catColors: Record<string, string> = {
    accounts: 'bg-blue-500',
    credit_cards: 'bg-purple-500',
    loans: 'bg-red-500',
    investments: 'bg-green-500',
    insurance: 'bg-amber-500',
    digital: 'bg-cyan-500',
  };

  const catIcons: Record<string, string> = {
    accounts: '🏦',
    credit_cards: '💳',
    loans: '📋',
    investments: '📈',
    insurance: '🛡️',
    digital: '📱',
  };

  return (
    <div className="space-y-6">
      {/* Insights Panel */}
      {insights && (
        <div className="bg-gradient-to-r from-[#004B8D] to-[#003366] rounded-xl p-5 text-white">
          <h3 className="font-semibold mb-4">AI Customer Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="bg-white/10 rounded-lg p-3">
              <p className="text-blue-200 text-xs mb-1">Life Stage</p>
              <p className="font-medium text-sm">{insights.life_stage || '-'}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3">
              <p className="text-blue-200 text-xs mb-1">Financial Health</p>
              <p className="font-medium text-sm">{insights.financial_health || '-'}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3">
              <p className="text-blue-200 text-xs mb-1">Key Needs</p>
              <p className="font-medium text-sm">{insights.key_needs?.join(', ') || '-'}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3">
              <p className="text-blue-200 text-xs mb-1">Products Analyzed</p>
              <p className="font-medium text-sm">{recommendations.length} recommendations</p>
            </div>
          </div>
          {/* Gap Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {insights.protection_gap && (
              <div className={`rounded-lg p-3 text-sm ${insights.protection_gap === 'Adequately covered' ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                <p className="text-xs opacity-70 mb-1">🛡️ Protection Gap</p>
                <p className="font-medium">{insights.protection_gap}</p>
              </div>
            )}
            {insights.investment_gap && (
              <div className="bg-amber-500/20 rounded-lg p-3 text-sm">
                <p className="text-xs opacity-70 mb-1">📈 Investment Gap</p>
                <p className="font-medium">{insights.investment_gap}</p>
              </div>
            )}
            {insights.credit_gap && (
              <div className="bg-purple-500/20 rounded-lg p-3 text-sm">
                <p className="text-xs opacity-70 mb-1">💳 Credit Gap</p>
                <p className="font-medium">{insights.credit_gap}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recommendation Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {recommendations.map((rec, i) => {
          const ai = rec.ai_analysis || {};
          return (
            <div key={rec.id || i} className="bg-white border-2 rounded-xl overflow-hidden card-hover transition"
              style={{ borderColor: i === 0 ? '#004B8D' : i === 1 ? '#C5A23E' : '#e5e7eb' }}>
              {/* Header */}
              <div className={`p-4 ${i === 0 ? 'bg-[#004B8D]' : i === 1 ? 'bg-[#C5A23E]' : 'bg-gray-500'}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-xs ${i === 0 ? 'text-blue-200' : i === 1 ? 'text-yellow-100' : 'text-gray-200'}`}>#{i + 1} Recommendation</p>
                    <h4 className="font-bold text-white text-lg mt-1">{rec.product_name}</h4>
                  </div>
                  <div className="text-3xl">{catIcons[rec.product_category] || '📦'}</div>
                </div>
              </div>

              <div className="p-5">
                {/* Category & Confidence */}
                <div className="flex items-center gap-2 mb-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${catColors[rec.product_category] ? 'text-white' : 'bg-gray-100 text-gray-600'}`}
                    style={catColors[rec.product_category] ? { backgroundColor: catColors[rec.product_category] } : {}}>
                    {(rec.product_category || '').replace('_', ' ').toUpperCase()}
                  </span>
                  <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${getConfidenceColor(rec.confidence_score)}`}>
                    {rec.confidence_score}% confidence
                  </span>
                  {rec.eligibility_status && (
                    <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                      rec.eligibility_status === 'eligible' ? 'bg-green-100 text-green-700' :
                      'bg-amber-100 text-amber-700'
                    }`}>{rec.eligibility_status}</span>
                  )}
                </div>

                {/* Reason */}
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <p className="text-xs text-gray-500 mb-1">Why this product?</p>
                  <p className="text-sm text-gray-700 leading-relaxed">{rec.reason}</p>
                </div>

                {/* Benefits */}
                {ai.benefits && ai.benefits.length > 0 && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 mb-1.5">Key Benefits</p>
                    <div className="space-y-1">
                      {ai.benefits.slice(0, 4).map((b: string, j: number) => (
                        <div key={j} className="flex items-start gap-1.5">
                          <span className="text-green-500 text-xs mt-0.5">✓</span>
                          <span className="text-xs text-gray-600">{b}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Cost & ROI */}
                <div className="grid grid-cols-2 gap-2 mb-3">
                  {ai.monthly_cost && (
                    <div className="bg-blue-50 rounded-lg p-2">
                      <p className="text-[10px] text-blue-600 mb-0.5">Monthly Cost</p>
                      <p className="text-xs font-bold text-blue-800">{ai.monthly_cost}</p>
                    </div>
                  )}
                  {ai.expected_roi && (
                    <div className="bg-green-50 rounded-lg p-2">
                      <p className="text-[10px] text-green-600 mb-0.5">Expected ROI</p>
                      <p className="text-xs font-bold text-green-800">{ai.expected_roi}</p>
                    </div>
                  )}
                </div>

                {/* Acceptance Bar */}
                {rec.acceptance_probability && (
                  <div className="flex items-center gap-2 mb-4">
                    <p className="text-xs text-gray-500 whitespace-nowrap">Acceptance:</p>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div className="bg-[#004B8D] h-2 rounded-full transition-all" style={{ width: `${rec.acceptance_probability}%` }} />
                    </div>
                    <span className="text-xs font-bold text-gray-700">{rec.acceptance_probability}%</span>
                  </div>
                )}

                <button className="w-full bg-[#004B8D] hover:bg-[#003366] text-white py-2.5 rounded-lg font-medium text-sm transition">
                  Apply Now
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = 'text' }: { label: string; value: string | number; onChange: (v: string) => void; type?: string }) {
  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-[#004B8D]" />
    </div>
  );
}

function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: string[] }) {
  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-[#004B8D]">
        <option value="">Select...</option>
        {options.map((o: string) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function CheckboxField({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="flex items-center gap-2 py-2">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)}
        className="w-4 h-4 text-[#004B8D] rounded border-gray-300 focus:ring-[#004B8D]" />
      <label className="text-sm text-gray-700">{label}</label>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return <div className="text-center py-8"><p className="text-gray-400 text-sm">{message}</p></div>;
}

function EmptyStateWithAdd({ message, onAdd }: { message: string; onAdd: () => void }) {
  return (
    <div className="text-center py-8">
      <p className="text-gray-400 text-sm mb-3">{message}</p>
      <button onClick={onAdd} className="text-[#004B8D] font-medium text-sm hover:underline">+ Add Details</button>
    </div>
  );
}
