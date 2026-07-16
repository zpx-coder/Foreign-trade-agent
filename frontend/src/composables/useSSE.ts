import { ref, onUnmounted } from "vue";

export interface SSEEvent {
  type: string;
  content?: string;
  section?: string;
  message?: string;
  elapsed_ms?: number;
}

interface UseSSEOptions {
  onEvent?: (event: SSEEvent) => void;
  onError?: (error: string) => void;
  onComplete?: (elapsedMs: number) => void;
}

export function useSSE(options: UseSSEOptions = {}) {
  const isStreaming = ref(false);
  const currentSection = ref<string | null>(null);
  const accumulatedText = ref("");
  const error = ref<string | null>(null);
  let abortController: AbortController | null = null;
  let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;

  async function start(url: string, body?: Record<string, unknown>) {
    stop();
    isStreaming.value = true;
    error.value = null;
    accumulatedText.value = "";
    currentSection.value = null;

    abortController = new AbortController();

    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          Accept: "text/event-stream",
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: abortController.signal,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: "请求失败" }));
        throw new Error(errData.detail || `HTTP ${response.status}`);
      }

      reader = response.body?.getReader() ?? null;
      if (!reader) throw new Error("不支持流式响应");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const event: SSEEvent = JSON.parse(line.slice(6));
              handleEvent(event);
            } catch { /* skip malformed */ }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        error.value = err.message || "流式连接中断";
        options.onError?.(error.value!);
      }
    } finally {
      isStreaming.value = false;
      reader = null;
      abortController = null;
    }
  }

  function handleEvent(event: SSEEvent) {
    options.onEvent?.(event);
    if (event.type === "text" && event.content) accumulatedText.value += event.content;
    if (event.type === "section" && event.section) currentSection.value = event.section;
    if (event.type === "complete") options.onComplete?.(event.elapsed_ms ?? 0);
    if (event.type === "error" && event.message) {
      error.value = event.message;
      options.onError?.(event.message);
    }
  }

  function stop() {
    abortController?.abort();
    reader?.cancel().catch(() => {});
    isStreaming.value = false;
  }

  onUnmounted(stop);

  return { isStreaming, currentSection, accumulatedText, error, start, stop };
}
