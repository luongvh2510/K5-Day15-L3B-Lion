import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent, MouseEvent } from "react";
import { api, ApiError, clearMockSession, USE_MOCK } from "./api";
import CartView from "./CartView";
import ChatPanel, { ChatBubble } from "./ChatPanel";
import ConfirmModal from "./ConfirmModal";
import FinalizedView from "./FinalizedView";
import InfeasibleView from "./InfeasibleView";
import ProfileDraft from "./ProfileDraft";
import type { Action, MemberInput, SessionState } from "./session";

type Work = {
  kind: "create" | "restore" | "message" | "budget" | "edit" | "confirm" | "reopen" | "action" | "finalize";
  request: () => Promise<SessionState>;
  sessionId?: string;
  editMemberName?: string | null;
  afterSuccess?: () => void;
};

type Failure = { kind: Work["kind"]; message: string; editMemberName?: string | null; retry?: Work };

const SESSION_KEY = "lion_session_id";
const RESTORE_MESSAGE = "Đang khôi phục phiên…";
const NETWORK_MESSAGE = "Không kết nối được máy chủ. Kiểm tra backend đã chạy chưa.";
const CHAT_LIMIT = 4000;
const SAMPLE_CHAT = `Chi
12h đặt cơm trưa nha mn, quỹ chung 300k nhé
An
t ăn chay nha, nhớ đó
Bình
mình dị ứng đậu phộng nặng lắm, đừng có gì dính đậu phộng nha
Dũng
gì cũng được, nhanh lên đói rồi 😭
An
à lấy thêm 1 cơm gà nha
Hà
mình muốn ăn bún`;
const formatNumber = new Intl.NumberFormat("vi-VN").format;

function validateChat(text: string) {
  if (!text.trim()) return "Chưa có nội dung chat.";
  if ([...text].length > CHAT_LIMIT) return "Đoạn chat vượt 4.000 ký tự. Hãy rút gọn trước khi phân tích.";
}

function readSavedSession() {
  try {
    return localStorage.getItem(SESSION_KEY);
  } catch {
    return null;
  }
}

export default function App() {
  const [chatText, setChatText] = useState("");
  const [reply, setReply] = useState("");
  const [budgetDraft, setBudgetDraft] = useState<string | null>(null);
  const [reopenModalOpen, setReopenModalOpen] = useState(false);
  const [showErrors, setShowErrors] = useState(false);
  const [initialSessionId] = useState(readSavedSession);
  const [session, setSession] = useState<SessionState | null>(null);
  const [pending, setPending] = useState<Work["kind"] | null>(initialSessionId ? "restore" : null);
  const [failure, setFailure] = useState<Failure | null>(null);
  const [storageBlocked, setStorageBlocked] = useState(false);
  const chatInput = useRef<HTMLTextAreaElement>(null);
  const budgetEditButton = useRef<HTMLButtonElement>(null);
  const draftHeading = useRef<HTMLHeadingElement>(null);
  const replyError = useRef<HTMLParagraphElement>(null);
  const inFlight = useRef(false);

  const charCount = [...chatText].length;
  const overLimit = charCount > CHAT_LIMIT;
  const chatError = showErrors || overLimit ? validateChat(chatText) : undefined;
  const isLoading = pending !== null;
  const openQuestions = session?.questions.filter((question) => question.status === "OPEN") ?? [];
  const openMemberIds = new Set(openQuestions.map((question) => question.member_id));
  const sessionStatus = session?.status;
  const isCartStage = sessionStatus === "CART_VALID" || sessionStatus === "CART_INFEASIBLE";
  const canEditBudget = sessionStatus === "PROFILE_DRAFT";
  const isBudgetEditorOpen = canEditBudget && budgetDraft !== null;

  const resetOrder = useCallback(() => {
    setSession(null);
    setReply("");
    setChatText("");
    setBudgetDraft(null);
    setReopenModalOpen(false);
    setShowErrors(false);
    setFailure(null);
    clearMockSession();
    try {
      localStorage.removeItem(SESSION_KEY);
      setStorageBlocked(false);
    } catch {
      setStorageBlocked(true);
    }
  }, []);

  const run = useCallback(async (work: Work) => {
    if (inFlight.current) return;
    inFlight.current = true;
    setPending(work.kind);
    setFailure(null);

    let attemptedWork = work;
    try {
      let next: SessionState;
      let refreshed = false;
      try {
        next = await work.request();
      } catch (error) {
        if (!(error instanceof ApiError) || error.status !== 409 || !work.sessionId || work.kind === "restore") {
          throw error;
        }
        const sessionId = work.sessionId;
        attemptedWork = { kind: "restore", sessionId, request: () => api.getSession(sessionId) };
        setPending("restore");
        next = await attemptedWork.request();
        refreshed = true;
      }

      setSession(next);
      try {
        localStorage.setItem(SESSION_KEY, next.session_id);
        setStorageBlocked(false);
      } catch {
        setStorageBlocked(true);
      }
      if (!refreshed) work.afterSuccess?.();
    } catch (error) {
      const apiError = error instanceof ApiError ? error : undefined;
      if (apiError?.status === 404) {
        resetOrder();
        setFailure({ kind: "restore", message: "Không tìm thấy phiên. Hãy dán đoạn chat để bắt đầu lại." });
        return;
      }
      const unavailable = apiError?.status === 502 || apiError?.status === 500;
      const networkError = apiError?.status === 0 && apiError.code === "NETWORK";
      setFailure({
        kind: work.kind,
        editMemberName: work.editMemberName,
        message: unavailable
          ? "Hệ thống AI tạm thời không phản hồi, vui lòng thử lại."
          : networkError ? NETWORK_MESSAGE : apiError?.message ?? "Chưa xử lý được yêu cầu. Vui lòng thử lại.",
        retry: unavailable || networkError || apiError?.code === "TIMEOUT" ? attemptedWork : undefined,
      });
    } finally {
      setPending(null);
      inFlight.current = false;
    }
  }, [resetOrder]);

  useEffect(() => {
    if (initialSessionId) {
      void run({ kind: "restore", sessionId: initialSessionId, request: () => api.getSession(initialSessionId) });
    }
  }, [initialSessionId, run]);

  useEffect(() => {
    if (sessionStatus !== "PROFILE_DRAFT") setBudgetDraft(null);
    if (sessionStatus) draftHeading.current?.focus();
  }, [sessionStatus]);

  useEffect(() => {
    if (failure) replyError.current?.focus();
  }, [failure]);

  function loadExample() {
    updateChat(SAMPLE_CHAT);
    setShowErrors(false);
    chatInput.current?.focus();
  }

  function updateChat(text: string) {
    setChatText(text);
    if (failure?.kind === "create") setFailure(null);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (validateChat(chatText)) {
      setShowErrors(true);
      chatInput.current?.focus();
      return;
    }
    setShowErrors(false);
    void run({ kind: "create", request: () => api.createSession(chatText) });
  }

  function sendMessage(text: string) {
    if (!session || session.status === "FINALIZED" || !text.trim()) return;
    const sessionId = session.session_id;
    void run({
      kind: "message", sessionId, request: () => api.sendMessage(sessionId, text),
      afterSuccess: () => setReply((current) => current === text ? "" : current),
    });
  }

  function closeBudgetEditor() {
    setBudgetDraft(null);
    if (failure?.kind === "budget") setFailure(null);
    budgetEditButton.current?.focus({ preventScroll: true });
  }

  function submitBudget(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = budgetDraft?.trim();
    if (session?.status !== "PROFILE_DRAFT" || !value) return;
    const sessionId = session.session_id;
    void run({
      kind: "budget",
      sessionId,
      request: () => api.sendMessage(sessionId, `Đổi quỹ thành ${value}`),
      afterSuccess: () => setBudgetDraft(null),
    });
  }

  function editMembers(members: MemberInput[], editMemberName: string | null, afterSuccess?: () => void) {
    if (session?.status !== "PROFILE_DRAFT") return;
    const sessionId = session.session_id;
    void run({ kind: "edit", sessionId, editMemberName, request: () => api.editMembers(sessionId, members), afterSuccess });
  }

  function confirmProfile() {
    if (session?.status !== "PROFILE_DRAFT" || !session.can_confirm) return;
    const sessionId = session.session_id;
    void run({ kind: "confirm", sessionId, request: () => api.confirm(sessionId) });
  }

  function askToReopenProfile(event: MouseEvent<HTMLButtonElement>) {
    if (!isCartStage || inFlight.current) return;
    event.currentTarget.focus({ preventScroll: true });
    setReopenModalOpen(true);
  }

  function reopenProfile() {
    if (!session || !isCartStage || inFlight.current) return;
    setReopenModalOpen(false);
    const sessionId = session.session_id;
    void run({ kind: "reopen", sessionId, request: () => api.reopen(sessionId) });
  }

  function changeCart(action: Action) {
    if (!session || !isCartStage) return;
    const sessionId = session.session_id;
    void run({ kind: "action", sessionId, request: () => api.action(sessionId, action) });
  }

  function finalizeCart() {
    if (session?.status !== "CART_VALID" || !session.cart || session.validation?.ok !== true) return;
    const sessionId = session.session_id;
    void run({ kind: "finalize", sessionId, request: () => api.finalize(sessionId) });
  }

  function startNewOrder() {
    if (!inFlight.current) resetOrder();
  }

  const questionHint = session?.can_confirm === false && openQuestions.length > 0
    ? `Còn ${openQuestions.length} câu hỏi cần trả lời` : undefined;
  const failureFeedback = failure && (
    <div className="api-error">
      <p className="field-error" ref={replyError} tabIndex={-1} role="alert">{failure.message}</p>
      {failure.retry && (
        <button className="button button--example" type="button" disabled={isLoading}
          onClick={() => { if (failure.retry) void run(failure.retry); }}>
          Thử lại
        </button>
      )}
    </div>
  );
  const cartFeedback = (
    <>
      {failure && failure.kind !== "message" && failure.kind !== "budget" && failureFeedback}
      {pending === "action" && (
        <p className="reading cart-request" role="status">
          <span className="spinner" aria-hidden="true" />Đang chọn quán và lập giỏ…
        </p>
      )}
      {pending === "reopen" && <p className="field-hint cart-request" role="status">Đang mở lại hồ sơ…</p>}
      {pending === "finalize" && <p className="field-hint cart-request" role="status">Đang chốt giỏ…</p>}
      {pending === "restore" && <p className="field-hint cart-request" role="status">{RESTORE_MESSAGE}</p>}
    </>
  );
  const budgetAction = (
    <button className="button button--plain budget-edit-button" type="button" ref={budgetEditButton}
      disabled={isLoading} aria-label="Sửa quỹ chung" aria-expanded={isBudgetEditorOpen}
      aria-controls={isBudgetEditorOpen ? "budget-editor" : undefined}
      onClick={() => isBudgetEditorOpen ? closeBudgetEditor() : setBudgetDraft("")}>Sửa</button>
  );
  const budgetEditor = isBudgetEditorOpen && (
    <form id="budget-editor" className="budget-editor" onSubmit={submitBudget}
      onKeyDown={(event) => {
        if (event.key === "Escape" && !isLoading) {
          event.preventDefault();
          closeBudgetEditor();
        }
      }}>
      <fieldset disabled={isLoading}>
        <label htmlFor="budget-amount">Quỹ mới</label>
        <div className="budget-editor-actions">
          <input id="budget-amount" value={budgetDraft ?? ""} placeholder="VD: 200k hoặc 200000"
            autoFocus autoComplete="off" onChange={(event) => {
              setBudgetDraft(event.target.value);
              if (failure?.kind === "budget") setFailure(null);
            }} />
          <button className="button button--primary" type="submit" disabled={!budgetDraft?.trim()}>
            {pending === "budget" ? "Đang gửi…" : "Cập nhật quỹ"}
          </button>
          <button className="button button--plain" type="button" onClick={closeBudgetEditor}>Huỷ</button>
        </div>
        {failure?.kind === "budget" && failureFeedback}
      </fieldset>
    </form>
  );
  const lockedProfile = session && isCartStage ? (
    <details className="locked-profiles">
      <summary>Xem hồ sơ đã khóa</summary>
      <ProfileDraft session={session} busy={isLoading} onEdit={editMembers} openMemberIds={openMemberIds} />
    </details>
  ) : null;
  const sessionStorageFeedback = storageBlocked && <p className="field-error">Trình duyệt không cho lưu mã phiên.</p>;

  return (
    <>
      <header className="site-header">
        <div className={`header-content${session ? " session-width" : ""}`}>
          <div className="brand">
            <span className="brand-icon" aria-hidden="true">L</span>
            <div>
              <div className="brand-label">
                <p className="brand-name">Lion</p>
                {USE_MOCK && <span className="demo-label">Bản demo</span>}
              </div>
              <h1>Đặt đơn nhóm</h1>
            </div>
          </div>
          {session && (
            <div className="header-actions">
              <button className="button button--example" type="button" disabled={isLoading}
                onClick={startNewOrder}>Làm đơn mới</button>
            </div>
          )}
        </div>
      </header>

      {session?.status === "FINALIZED" ? (
        <main className="workspace finalized-workspace">
          {sessionStorageFeedback}
          <section className="composer finalized-card" aria-label="Đơn đã chốt">
            <FinalizedView session={session} headingRef={draftHeading} />
          </section>
        </main>
      ) : session ? (
        <main className="workspace session-width">
          {sessionStorageFeedback}
          <div className="session-layout">
            <section className="composer profile-panel" aria-label="Hồ sơ và đơn nhóm">
              {session.status === "PROFILE_DRAFT" ? (
                <>
                  <ProfileDraft session={session} busy={isLoading} onEdit={editMembers} headingRef={draftHeading}
                    budgetAction={budgetAction} budgetEditor={budgetEditor}
                    editFeedback={failure?.kind === "edit"
                      ? { memberName: failure.editMemberName ?? null, content: failureFeedback } : undefined}
                    openMemberIds={openMemberIds} />
                  {failure && failure.kind !== "message" && failure.kind !== "budget" && failure.kind !== "edit" && failureFeedback}
                  {pending === "edit" && <p className="field-hint" role="status">Đang lưu hồ sơ…</p>}
                  {pending === "restore" && <p className="field-hint" role="status">{RESTORE_MESSAGE}</p>}
                  <div className="composer-actions">
                    {questionHint && <p className="field-hint" id="confirm-hint">{questionHint}</p>}
                    {pending === "confirm" && (
                      <p className="reading" role="status">
                        <span className="spinner" aria-hidden="true" />Đang chọn quán và lập giỏ…
                      </p>
                    )}
                    <button className="button button--primary" type="button"
                      disabled={isLoading || !session.can_confirm}
                      title={questionHint}
                      aria-describedby={questionHint ? "confirm-hint" : undefined}
                      onClick={confirmProfile}>Xác nhận hồ sơ</button>
                  </div>
                </>
              ) : session.status === "CART_VALID" ? (
                <CartView session={session} busy={isLoading} headingRef={draftHeading}
                  lockedProfile={lockedProfile} feedback={cartFeedback}
                  onReopen={askToReopenProfile} onChangeRestaurant={() => changeCart({ type: "CHANGE_RESTAURANT" })}
                  onFinalize={finalizeCart} />
              ) : (
                <InfeasibleView session={session} busy={isLoading} headingRef={draftHeading}
                  lockedProfile={lockedProfile} feedback={cartFeedback}
                  onAction={changeCart} onReopen={askToReopenProfile} />
              )}
            </section>
            <ChatPanel session={session} questions={openQuestions} busy={isLoading}
              sending={pending === "message" || pending === "budget"}
              reply={reply} onSend={sendMessage} onReplyChange={(text) => {
                setReply(text);
                if (failure?.kind === "message") setFailure(null);
              }}
              feedback={failure?.kind === "message" && failureFeedback}
            />
          </div>
        </main>
      ) : (
        <main className="workspace">
          <section className="conversation" aria-label="Cuộc trò chuyện">
            <ChatBubble role="assistant">
              <p>Chào bạn! Mình giúp tóm tắt yêu cầu ăn uống của từng người từ đoạn chat nhóm.</p>
            </ChatBubble>

            {isLoading && (
              <ChatBubble role="assistant">
                <p className="reading" role="status">
                  <span className="spinner" aria-hidden="true" />
                  {pending === "restore" ? RESTORE_MESSAGE : "Đang đọc đoạn chat…"}
                </p>
              </ChatBubble>
            )}
          </section>

          <form className="composer" onSubmit={handleSubmit} noValidate aria-label="Nhập đoạn chat nhóm">
            <fieldset disabled={isLoading}>
              <div className="composer-heading">
                <label htmlFor="chat-text">Đoạn chat nhóm</label>
                <button className="button button--example" type="button" onClick={loadExample}>
                  Nạp chat mẫu
                </button>
              </div>
              <p className="field-hint" id="chat-hint">
                Dán tên người gửi trên một dòng, rồi đến nội dung tin nhắn. Ghi quỹ chung trong đoạn chat.
              </p>
              <textarea
                id="chat-text"
                name="chat_text"
                ref={chatInput}
                required
                rows={8}
                value={chatText}
                placeholder="Dán đoạn chat nhóm vào đây (Zalo, Messenger…)"
                onChange={(event) => updateChat(event.target.value)}
                aria-invalid={Boolean(chatError)}
                aria-describedby={chatError ? "chat-hint chat-count chat-error" : "chat-hint chat-count"}
              />
              <div className="field-footer">
                {chatError && <p className="field-error" id="chat-error" role="alert">{chatError}</p>}
                <p className={`char-count${overLimit ? " char-count--over" : ""}`} id="chat-count">
                  {formatNumber(charCount)} / {formatNumber(CHAT_LIMIT)}
                </p>
              </div>

              {failureFeedback}
              {storageBlocked && <p className="field-error">Trình duyệt không cho cập nhật phiên đã lưu.</p>}

              <div className="composer-actions">
                {USE_MOCK && <p className="field-hint">Bản demo luôn hiển thị hồ sơ mẫu.</p>}
                <button className="button button--primary" type="submit">
                  Phân tích
                </button>
              </div>
            </fieldset>
          </form>
        </main>
      )}
      {isCartStage && reopenModalOpen && (
        <ConfirmModal onCancel={() => setReopenModalOpen(false)} onConfirm={reopenProfile} />
      )}
    </>
  );
}
