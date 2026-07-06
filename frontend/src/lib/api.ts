const API_BASE = 'https://nba-hdfc.onrender.com';

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('hdfc_token') : null;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('hdfc_token');
      localStorage.removeItem('hdfc_user');
      window.location.href = '/';
    }
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return res.json();
}

export const api = {
  // Auth
  login: (data: { employee_id: string; password: string }) =>
    apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  register: (data: any) =>
    apiFetch('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => apiFetch('/api/auth/me'),

  // Customers
  searchCustomers: (q: string) => apiFetch(`/api/customers/search?q=${encodeURIComponent(q || '')}`),
  getCustomer: (id: string) => apiFetch(`/api/customers/${id}`),
  createCustomer: (data: any) =>
    apiFetch('/api/customers', { method: 'POST', body: JSON.stringify(data) }),
  updateCustomer: (id: string, data: any) =>
    apiFetch(`/api/customers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  // Family
  upsertFamily: (customerId: string, data: any) =>
    apiFetch(`/api/customers/${customerId}/family`, { method: 'POST', body: JSON.stringify(data) }),

  // Employment
  upsertEmployment: (customerId: string, data: any) =>
    apiFetch(`/api/customers/${customerId}/employment`, { method: 'POST', body: JSON.stringify(data) }),

  // Banking
  upsertBanking: (customerId: string, data: any) =>
    apiFetch(`/api/customers/${customerId}/banking`, { method: 'POST', body: JSON.stringify(data) }),

  // Existing Products
  listExistingProducts: (customerId: string) => apiFetch(`/api/customers/${customerId}/products`),
  addExistingProduct: (customerId: string, data: any) =>
    apiFetch(`/api/customers/${customerId}/products`, { method: 'POST', body: JSON.stringify(data) }),
  removeExistingProduct: (customerId: string, productId: number) =>
    apiFetch(`/api/customers/${customerId}/products/${productId}`, { method: 'DELETE' }),

  // Recommendations
  generateRecommendations: (customerId: string) =>
    apiFetch(`/api/recommendations/generate/${customerId}`, { method: 'POST' }),
  getRecommendations: (customerId: string) =>
    apiFetch(`/api/recommendations/customer/${customerId}`),
  applyRecommendation: (id: number, outcome: string) =>
    apiFetch(`/api/recommendations/${id}/apply`, { method: 'PUT', body: JSON.stringify({ recommendation_id: id, outcome }) }),

  // Dashboard
  getDashboardStats: () => apiFetch('/api/dashboard/stats'),
  getConversionAnalytics: () => apiFetch('/api/dashboard/analytics/conversion'),
  getRMPerformance: () => apiFetch('/api/dashboard/analytics/rm-performance'),

  // Products
  listProducts: (category?: string) =>
    apiFetch(`/api/products${category ? `?category=${category}` : ''}`),
  getCategories: () => apiFetch('/api/products/categories'),
  seedProducts: () => apiFetch('/api/products/seed', { method: 'POST' }),
};
