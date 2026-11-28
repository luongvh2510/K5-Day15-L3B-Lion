import type { Action, ApiErrorPayload, ChatMessage, MemberInput, Menu, Restaurant, SessionState, Source } from "./session";

const BASE = (import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000/api").replace(/\/+$/, "");
const TIMEOUT_MS = 120_000;
export const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? "false") === "true";

export class ApiError extends Error {
  constructor(readonly status: number, readonly code: string, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(url, { ...init, signal: controller.signal });
    const data: unknown = await response.json().catch((error: unknown) => {
      if (!(error instanceof SyntaxError)) throw error;
      return undefined;
    });

    if (!response.ok) {
      const payload = (data as Partial<ApiErrorPayload> | null | undefined)?.error;
      throw new ApiError(
        response.status,
        typeof payload?.code === "string" ? payload.code : `HTTP_${response.status}`,
        typeof payload?.message === "string" ? payload.message : "Máy chủ không xử lý được yêu cầu.",
      );
    }
    if (data === undefined) {
      throw new ApiError(response.status, "INVALID_RESPONSE", "Máy chủ trả về dữ liệu không hợp lệ.");
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (controller.signal.aborted) {
      throw new ApiError(0, "TIMEOUT", "Yêu cầu quá thời gian chờ. Vui lòng thử lại.");
    }
    throw new ApiError(0, "NETWORK", "Không kết nối được máy chủ. Kiểm tra backend đã chạy chưa.");
  } finally {
    clearTimeout(timeout);
  }
}

type Method = "GET" | "POST" | "PATCH";

const MOCK_SESSION_KEY = "lion_mock_session";
type MockSnapshot = { session: SessionState; step: number };

let mockStep = 0;
let mockSession: SessionState | null = null;

function saveMockSnapshot(session: SessionState) {
  try {
    sessionStorage.setItem(MOCK_SESSION_KEY, JSON.stringify({ session, step: mockStep } satisfies MockSnapshot));
  } catch {
    // Mock vẫn chạy trong bộ nhớ khi trình duyệt chặn sessionStorage.
  }
}

async function getMockSession(id: string): Promise<SessionState> {
  // Giữ chỉ báo khôi phục đủ lâu để thấy trong bản demo.
  await new Promise<void>((resolve) => setTimeout(resolve, 180));
  try {
    const snapshot = JSON.parse(sessionStorage.getItem(MOCK_SESSION_KEY) ?? "null") as MockSnapshot | null;
    if (snapshot?.session?.session_id === id && typeof snapshot.step === "number") {
      mockSession = snapshot.session;
      mockStep = snapshot.step;
    }
  } catch {
    // Có thể vẫn còn phiên trong bộ nhớ.
  }
  if (mockSession?.session_id !== id) {
    throw new ApiError(404, "NOT_FOUND", "Không tìm thấy phiên.");
  }
  return mockSession;
}

export function clearMockSession() {
  if (!USE_MOCK) return;
  mockSession = null;
  mockStep = 0;
  try {
    sessionStorage.removeItem(MOCK_SESSION_KEY);
  } catch {
    // Trạng thái trong bộ nhớ đã được xóa.
  }
}

function mockInfeasibleEnabled() {
  try {
    return localStorage.getItem("lion_mock_infeasible") === "1";
  } catch {
    return false;
  }
}

function appendMockMessages(session: SessionState, messages: Pick<ChatMessage, "role" | "kind" | "text">[]): SessionState {
  const turn = (session.messages.at(-1)?.turn ?? 0) + 1;
  const created_at = new Date().toISOString();
  return {
    ...session,
    messages: [
      ...session.messages,
      ...messages.map((message, index) => ({
        ...message, id: `mock-${turn}-${index}`, turn, created_at, question_id: null,
      })),
    ],
  };
}

function mockMemberEdit(session: SessionState, inputs: MemberInput[]): SessionState {
  const host: Source = { kind: "HOST", line: null, quote: null };
  return {
    ...session,
    members: inputs.map((input) => {
      const previous = session.members.find((member) => member.name === input.name);
      const id = previous?.id ?? `mock-host:${input.name}`;
      return {
        id,
        name: input.name,
        origin: previous?.origin ?? "HOST_ADDED",
        flags: [],
        quotes: previous?.quotes ?? [],
        hard_constraints: input.hard_constraints.map((constraint) =>
          previous?.hard_constraints.find((entry) => entry.type === constraint.type && entry.allergen === constraint.allergen)
          ?? { ...constraint, id: `${id}:${constraint.type}:${constraint.allergen}`, locked: false, note: null, source: host }
        ),
        preferences: input.preferences.map(({ text }) =>
          previous?.preferences.find((entry) => entry.text === text)
          ?? { text, id: `${id}:preference:${text}`, source: host }
        ),
      };
    }),
  };
}

async function mockCall<T>(method: Method, path: string, body?: object): Promise<T> {
  const pick = (file: string) => fetchJson<T>(`/mocks/${file}.json`);
  async function readSession(file: string) {
    return fetchJson<SessionState>(`/mocks/${file}.json`);
  }

  if (path === "/restaurants") return pick("restaurants");
  if (path === "/restaurants/store_08/menu") return pick("menu_store_08");
  if (path.endsWith("/menu")) {
    throw new ApiError(404, "NOT_FOUND", "Bản demo chưa có menu cho quán này.");
  }
  if (method === "GET" && path.startsWith("/sessions/")) {
    return await getMockSession(decodeURIComponent(path.slice("/sessions/".length))) as T;
  }
  if (method === "POST" && path === "/sessions") {
    await new Promise<void>((resolve) => setTimeout(resolve, 350));
    mockSession = await readSession("session_draft");
    mockStep = 0;
  } else if (path.endsWith("/messages")) {
    const reply = (body as { text: string }).text;
    if (mockSession?.status === "CART_INFEASIBLE") {
      mockSession = appendMockMessages(mockSession, [
        { role: "user", kind: "TEXT", text: reply },
        { role: "assistant", kind: "INFO", text: "Trong bản demo, hãy chọn một đề xuất để lập lại giỏ." },
      ]);
    } else {
      const cartSession = mockSession?.status === "CART_VALID" ? mockSession : null;
      const result = await readSession(!cartSession && mockStep === 0 ? "session_draft_answered" : "session_refusal");
      const refusal = result.messages.at(-1);
      mockSession = cartSession && refusal?.kind === "REFUSAL"
        ? appendMockMessages(cartSession, [
          { role: "user", kind: "TEXT", text: reply },
          { role: "assistant", kind: refusal.kind, text: refusal.text },
        ])
        : result;
      mockStep++;
    }
  } else if (method === "PATCH" && path.endsWith("/members")) {
    const current = mockSession ?? await readSession("session_draft");
    mockSession = mockMemberEdit(current, (body as { members: MemberInput[] }).members);
  } else if (path.endsWith("/confirm")) {
    mockSession = await readSession(mockInfeasibleEnabled() ? "session_infeasible" : "session_cart_valid");
  } else if (path.endsWith("/actions")) {
    const action = (body as { action: Action }).action;
    const restaurant = mockSession?.restaurant;
    if (mockSession?.status === "CART_VALID" && action.type === "CHANGE_RESTAURANT" && !action.restaurant_id && restaurant) {
      mockSession = appendMockMessages(mockSession, [{
        role: "assistant", kind: "INFO", text: `Chưa có quán khác phù hợp. Mình giữ giỏ ở ${restaurant.name}.`,
      }]);
    } else {
      let result = await readSession("session_cart_valid");
      if (action.type === "SELECT_RESTAURANT" && result.restaurant?.id !== action.restaurant_id) {
        result = await readSession("session_infeasible");
        if (result.restaurant?.id !== action.restaurant_id) {
          throw new ApiError(400, "INVALID_INPUT", "Bản demo chưa có dữ liệu giỏ cho quán này.");
        }
      }
      mockSession = result;
    }
  } else if (path.endsWith("/finalize")) {
    const data = await readSession("session_finalized");
    mockSession = { ...data, budget: data.cart?.remaining ?? data.budget };
  } else if (path.endsWith("/reopen")) {
    mockSession = await readSession("session_draft");
    mockStep = 0;
  } else if (!mockSession) {
    mockSession = await readSession("session_draft");
  }
  saveMockSnapshot(mockSession);
  return mockSession as T;
}

function call<T>(method: Method, path: string, body?: object): Promise<T> {
  if (USE_MOCK) return mockCall<T>(method, path, body);

  return fetchJson<T>(BASE + path, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

const sessionPath = (id: string) => `/sessions/${encodeURIComponent(id)}`;

export const api = {
  restaurants: () => call<Restaurant[]>("GET", "/restaurants"),
  menu: (id: string) => call<Menu>("GET", `/restaurants/${encodeURIComponent(id)}/menu`),
  createSession: (chatText: string) => call<SessionState>("POST", "/sessions", { chat_text: chatText }),
  getSession: (id: string) => call<SessionState>("GET", sessionPath(id)),
  sendMessage: (id: string, text: string) =>
    call<SessionState>("POST", `${sessionPath(id)}/messages`, { text }),
  editMembers: (id: string, members: MemberInput[]) =>
    call<SessionState>("PATCH", `${sessionPath(id)}/members`, { members }),
  confirm: (id: string) => call<SessionState>("POST", `${sessionPath(id)}/confirm`),
  reopen: (id: string) => call<SessionState>("POST", `${sessionPath(id)}/reopen`),
  action: (id: string, action: Action) =>
    call<SessionState>("POST", `${sessionPath(id)}/actions`, { action }),
  finalize: (id: string) => call<SessionState>("POST", `${sessionPath(id)}/finalize`),
};
