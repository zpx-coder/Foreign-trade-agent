import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/api/client";

// ── 类型 ──

export interface EmailTemplateItem {
  id: string;
  name: string;
  subject: string | null;
  tone: string | null;
  cta_type: string | null;
  status: string;
  spam_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface EmailTemplateDetail {
  id: string;
  tenant_id: string;
  name: string;
  subject: string | null;
  body_html: string | null;
  body_text: string | null;
  tone: string | null;
  cta_type: string | null;
  key_points: string | null;
  icp_id: string | null;
  product_id: string | null;
  spam_score: number | null;
  read_time_seconds: number | null;
  input_data: Record<string, unknown> | null;
  output_data: Record<string, unknown> | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CampaignItem {
  id: string;
  name: string;
  template_id: string | null;
  status: string;
  total_recipients: number;
  sent_count: number;
  opened_count: number;
  created_at: string;
}

export interface CampaignDetail {
  id: string;
  tenant_id: string;
  name: string;
  template_id: string | null;
  status: string;
  total_recipients: number;
  sent_count: number;
  delivered_count: number;
  opened_count: number;
  bounced_count: number;
  schedule_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  smtp_config: Record<string, unknown> | null;
  customer_ids: string[] | null;
  send_logs: SendLogItem[];
  created_at: string;
  updated_at: string;
}

export interface SendLogItem {
  id: string;
  campaign_id: string;
  customer_id: string | null;
  contact_id: string | null;
  recipient_email: string;
  subject: string | null;
  status: string;
  tracking_id: string;
  opened_at: string | null;
  error_message: string | null;
  created_at: string;
}

// ── Store ──

export const useEmailStore = defineStore("email", () => {
  // Templates
  const templates = ref<EmailTemplateItem[]>([]);
  const templatesTotal = ref(0);
  const templatesLoading = ref(false);
  const currentTemplate = ref<EmailTemplateDetail | null>(null);

  // Campaigns
  const campaigns = ref<CampaignItem[]>([]);
  const campaignsTotal = ref(0);
  const campaignsLoading = ref(false);
  const currentCampaign = ref<CampaignDetail | null>(null);

  // ── Template Actions ──

  async function fetchTemplates(params?: Record<string, unknown>) {
    templatesLoading.value = true;
    try {
      const { data } = await api.get("/email-templates", { params });
      templates.value = data.items;
      templatesTotal.value = data.total;
    } finally {
      templatesLoading.value = false;
    }
  }

  async function fetchTemplate(id: string) {
    const { data } = await api.get(`/email-templates/${id}`);
    currentTemplate.value = data;
    return data as EmailTemplateDetail;
  }

  async function createTemplate(formData: Record<string, unknown>): Promise<EmailTemplateDetail> {
    const { data } = await api.post("/email-templates", formData);
    return data as EmailTemplateDetail;
  }

  async function updateTemplate(id: string, formData: Record<string, unknown>) {
    await api.put(`/email-templates/${id}`, formData);
  }

  async function removeTemplate(id: string) {
    await api.delete(`/email-templates/${id}`);
  }

  // ── Campaign Actions ──

  async function fetchCampaigns(params?: Record<string, unknown>) {
    campaignsLoading.value = true;
    try {
      const { data } = await api.get("/email-campaigns", { params });
      campaigns.value = data.items;
      campaignsTotal.value = data.total;
    } finally {
      campaignsLoading.value = false;
    }
  }

  async function fetchCampaign(id: string) {
    const { data } = await api.get(`/email-campaigns/${id}`);
    currentCampaign.value = data;
    return data as CampaignDetail;
  }

  async function createCampaign(formData: Record<string, unknown>): Promise<CampaignDetail> {
    const { data } = await api.post("/email-campaigns", formData);
    return data as CampaignDetail;
  }

  async function removeCampaign(id: string) {
    await api.delete(`/email-campaigns/${id}`);
  }

  async function sendCampaign(id: string) {
    const { data } = await api.post(`/email-campaigns/${id}/send`);
    return data;
  }

  async function pauseCampaign(id: string) {
    await api.post(`/email-campaigns/${id}/pause`);
  }

  async function previewEmail(campaignId: string, customerId: string, contactId?: string) {
    const { data } = await api.post(`/email-campaigns/${campaignId}/preview`, {
      customer_id: customerId,
      contact_id: contactId || null,
    });
    return data;
  }

  async function testSend(templateId: string, email: string) {
    const { data } = await api.post(`/email-templates/${templateId}/test-send`, { email });
    return data;
  }

  return {
    templates, templatesTotal, templatesLoading, currentTemplate,
    campaigns, campaignsTotal, campaignsLoading, currentCampaign,
    fetchTemplates, fetchTemplate, createTemplate, updateTemplate, removeTemplate,
    fetchCampaigns, fetchCampaign, createCampaign, removeCampaign,
    sendCampaign, pauseCampaign, previewEmail, testSend,
  };
});
