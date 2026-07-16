import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/api/client";

// ── 类型 ──

export interface CustomerListItem {
  id: string;
  name: string;
  industry: string | null;
  country: string | null;
  source: string;
  status: string;
  website: string | null;
  contacts_count: number;
  icp_id: string | null;
  icp_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContactItem {
  id: string;
  customer_id: string;
  tenant_id: string;
  name: string;
  title: string | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  is_primary: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CustomerDetail {
  id: string;
  tenant_id: string;
  name: string;
  industry: string | null;
  website: string | null;
  country: string | null;
  city: string | null;
  company_size: string | null;
  description: string | null;
  source: string;
  source_url: string | null;
  icp_id: string | null;
  status: string;
  source_data: Record<string, unknown> | null;
  ai_summary: string | null;
  notes: string | null;
  contacts_count: number;
  contacts: ContactItem[];
  created_at: string;
  updated_at: string;
}

// ── Store ──

export const useCustomerStore = defineStore("customer", () => {
  const list = ref<CustomerListItem[]>([]);
  const total = ref(0);
  const loading = ref(false);
  const current = ref<CustomerDetail | null>(null);
  const searching = ref(false);

  async function fetchList(params?: Record<string, unknown>) {
    loading.value = true;
    try {
      const { data } = await api.get("/customers", { params });
      list.value = data.items;
      total.value = data.total;
    } finally {
      loading.value = false;
    }
  }

  async function fetchDetail(id: string) {
    const { data } = await api.get(`/customers/${id}`);
    current.value = data;
    return data as CustomerDetail;
  }

  async function create(
    formData: Record<string, unknown>
  ): Promise<CustomerDetail> {
    const { data } = await api.post("/customers", formData);
    return data as CustomerDetail;
  }

  async function update(
    id: string,
    formData: Record<string, unknown>
  ): Promise<void> {
    await api.put(`/customers/${id}`, formData);
  }

  async function remove(id: string): Promise<void> {
    await api.delete(`/customers/${id}`);
  }

  async function batchUpdateStatus(
    ids: string[],
    status: string
  ): Promise<number> {
    const { data } = await api.put("/customers/batch/status", { ids, status });
    return data.updated_count;
  }

  async function addContact(
    customerId: string,
    contactData: Record<string, unknown>
  ) {
    const { data } = await api.post(
      `/customers/${customerId}/contacts`,
      contactData
    );
    return data as ContactItem;
  }

  async function updateContact(
    customerId: string,
    contactId: string,
    contactData: Record<string, unknown>
  ) {
    await api.put(
      `/customers/${customerId}/contacts/${contactId}`,
      contactData
    );
  }

  async function removeContact(
    customerId: string,
    contactId: string
  ): Promise<void> {
    await api.delete(`/customers/${customerId}/contacts/${contactId}`);
  }

  async function enrichCustomer(id: string): Promise<void> {
    const token = localStorage.getItem("access_token");
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";

    const response = await fetch(`${baseUrl}/customers/${id}/enrich`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: "请求失败" }));
      throw new Error(err.detail || "补全请求失败");
    }
  }

  async function importExcel(file: File): Promise<{
    created: number;
    skipped: number;
    total: number;
    errors: { row: number; message: string }[];
  }> {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await api.post("/customers/import", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  }

  async function downloadTemplate(): Promise<void> {
    const response = await api.get("/customers/import-template", {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "customer_import_template.xlsx");
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }

  async function exportData(params?: Record<string, unknown>) {
    const response = await api.get("/customers/export", {
      params,
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "customers.xlsx");
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }

  return {
    list, total, loading, current, searching,
    fetchList, fetchDetail, create, update, remove,
    batchUpdateStatus, enrichCustomer, importExcel, downloadTemplate, exportData,
    addContact, updateContact, removeContact,
  };
});
