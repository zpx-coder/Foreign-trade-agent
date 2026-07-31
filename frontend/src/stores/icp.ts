import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/api/client";

export interface IcpInputData {
  target_industry?: string;
  target_region?: string;
  company_size?: string | string[];  // v1.3: 支持多选
  // v1.3: 产品关联
  product_ids?: string[];
  // 旧字段（保留兼容）
  product_category?: string;
  product_price_range?: string;
  product_features?: string;
  // v1.3: 客户单批次采购预算结构化
  customer_budget_min?: number;
  customer_budget_max?: number;
  customer_budget?: string;  // 旧字段
  // v1.3: 采购商核心特征
  buyer_type?: string;
  key_decision_factors?: string[];
  pain_points?: string;
  decision_makers?: string;
  additional_notes?: string;
  // v1.3 内部快照：前端传入产品内联数据供 AI prompt 使用
  _products_inline?: ProductInline[];
}

export interface ProductInline {
  id: string;
  name: string;
  description?: string;
  category?: string;
  price_usd?: number;
  moq?: number;
  hs_code?: string;
  image_url?: string;
  images?: string[];
}

export interface IcpItem {
  id: string;
  name: string;
  status: string;
  input_data: IcpInputData;
  output_data: Record<string, unknown> | null;
  generation_time_ms: number | null;
  error_message: string | null;
  // v1.3: 列表新增显示字段
  target_region?: string | null;
  target_industry?: string | null;
  company_size?: string[] | null;
  customer_budget?: string | null;
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

  async function createDraft(inputData: IcpInputData & { name: string }) {
    const { data } = await api.post("/icps", {
      name: inputData.name,
      input_data: inputData,
    });
    return data as IcpItem;
  }

  async function update(id: string, data: { name?: string; input_data?: IcpInputData }) {
    const { data: result } = await api.put(`/icps/${id}`, data);
    current.value = result;
    return result as IcpItem;
  }

  async function remove(id: string) {
    await api.delete(`/icps/${id}`);
  }

  return { list, total, loading, current, fetchList, fetchDetail, create, createDraft, update, remove };
});
