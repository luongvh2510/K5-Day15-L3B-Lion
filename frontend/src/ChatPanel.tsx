import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import type { Question, SessionState } from "./session";

export function ChatBubble({ role, refusal, children }: {
  role: "user" | "assistant";
  refusal?: boolean;
  children: ReactNode;
}) {
  const isLeader = role === "user";

  return (
    <article className={`message message--${isLeader ? "leader" : "lion"}${refusal ? " message--refusal" : ""}`}>
      <span className="message-avatar" aria-hidden="true">{isLeader ? "B" : "L"}</span>
      <div className="message-content">
        <p className="message-sender">{isLeader ? "Bạn" : "Lion"}</p>
        <div className="message-bubble">{children}</div>
      </div>
    </article>
  );
}

type ChatPanelProps = {
  session: SessionState;
  questions: Question[];
  busy: boolean;
  sending: boolean;
  reply: string;
  onReplyChange: (text: string) => void;
  onSend: (text: string) => void;
  feedback: ReactNode;
};

export default function ChatPanel({
  session, questions, busy, sending, reply, onReplyChange, onSend, feedback,
}: ChatPanelProps) {
  const [emptyReply, setEmptyReply] = useState(false);
  const conversation = useRef<HTMLDivElement>(null);
  const previousCount = useRef(0);
  const messageCount = session.messages.length;
  const original = session.messages.find((message) => message.role === "user");

  useEffect(() => {
    const list = conversation.current;
    if (list && (messageCount > previousCount.current || sending)) {
      list.scrollTop = list.scrollHeight;
    }
    previousCount.current = messageCount;
  }, [messageCount, sending]);

  function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    if (!reply.trim()) {
      setEmptyReply(true);
      return;
    }
    onSend(reply);
  }

  return (
    <section className="chat-panel" aria-labelledby="chat-heading">
      <h2 id="chat-heading">Cuộc trò chuyện</h2>
      <div className="conversation session-conversation" ref={conversation} tabIndex={0}
        role="log" aria-label="Lịch sử trò chuyện">
        {session.messages.map((message) => (
          <ChatBubble key={message.id} role={message.role} refusal={message.kind === "REFUSAL"}>
            {message === original ? (
              <details className="original-chat">
                <summary>
                  <span className="original-expand">Xem đoạn chat gốc</span>
                  <span className="original-collapse">Thu gọn</span>
                </summary>
                <p className="submitted-chat">{message.text}</p>
              </details>
            ) : (
              <p className="chat-text">
                {message.kind === "REFUSAL" && <span aria-label="Từ chối">🛡️ </span>}
                {message.text}
              </p>
            )}
          </ChatBubble>
        ))}
        {sending && (
          <ChatBubble role="assistant">
            <p role="status" aria-label="Lion đang trả lời">…</p>
          </ChatBubble>
        )}
      </div>

      {session.status !== "FINALIZED" && (
        <form className="composer reply-composer" onSubmit={send}>
          <fieldset disabled={busy}>
            {questions.length > 0 && (
              <div className="question-note">
                <h3>Câu hỏi cần trả lời</h3>
                <ul>
                  {questions.map((question) => <li key={question.id}>{question.text}</li>)}
                </ul>
              </div>
            )}
            <label htmlFor="chat-reply">Tin nhắn của bạn</label>
            <textarea
              id="chat-reply"
              rows={3}
              value={reply}
              onChange={(event) => {
                setEmptyReply(false);
                onReplyChange(event.target.value);
              }}
              aria-invalid={emptyReply}
              aria-describedby={emptyReply ? "empty-reply" : undefined}
            />
            {emptyReply && <p id="empty-reply" className="field-error" role="alert">Chưa có nội dung tin nhắn.</p>}
            {feedback}
            <div className="composer-actions">
              <button className="button button--primary" type="submit">Gửi</button>
            </div>
          </fieldset>
        </form>
      )}
    </section>
  );
}
