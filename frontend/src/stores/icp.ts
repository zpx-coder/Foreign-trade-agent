import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/api/client";

export interface IcpInputData {
  target_industry?: string;
  target_region?: string;
  company_size?: string;
  product_category?: string;
  product_price_range?: string;
  product_features?: string;
  customer_budget?: string;
  pain_points?: string;
  decision_makers?: string;
  additional_notes?: string;
}

export interface IcpItem {
  id: string;
  name: string;
  status: string;
  input_data: IcpInputData;
  output_data: Record<string, unknown> | null;
  generation_time_ms: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export const useIcpStore = defineStore("icp", () => {
  const list = ref<IcpItem[]>([]);
  const total = ref(0);
  const loading = ref(false);
  const current = ref<IcpItem | null>(null);

  async function fetchList(params?: Record<string, unknown>) {
    loading.value = true;
    try {
      const { data } = await api.get("/icps", { params });
      list.value = data.items;
      total.value = data.total;
    } finally {
      loading.value = false;
    }
  }

  async function fetchDetail(id: string) {
    const { data } = await api.get(`/icps/${id}`);
    current.value = data;
    return data as IcpItem;
  }

  async function create(inputData: IcpInputData & { name: string }) {
    const { data } = await api.post("/icps", {
      name: inputData.name,
      input_data: inputData,
    });
    return data as IcpItem;
  }

  async function remove(id: string) {
    await api.delete(`/icps/${id}`);
  }

  return { list, total, loading, current, fetchList, fetchDetail, create, remove };
});
