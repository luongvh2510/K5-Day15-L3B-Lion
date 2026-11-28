import { useEffect, useId, useState } from "react";
import type { Ref } from "react";
import type { SessionState } from "./session";

const money = (value: number) => value.toLocaleString("vi-VN") + "đ";

async function copyText(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // Một số trình duyệt chặn Clipboard API dù có hỗ trợ.
  }

  const previousFocus = document.activeElement;
  const buffer = document.createElement("textarea");
  buffer.className = "clipboard-copy-buffer";
  buffer.value = text;
  buffer.readOnly = true;
  buffer.tabIndex = -1;
  document.body.append(buffer);

  try {
    buffer.focus({ preventScroll: true });
    buffer.select();
    return document.execCommand("copy");
  } catch {
    return false;
  } finally {
    buffer.remove();
    if (previousFocus instanceof HTMLElement) previousFocus.focus({ preventScroll: true });
  }
}

type FinalizedViewProps = {
  session: SessionState;
  headingRef: Ref<HTMLHeadingElement>;
};

export default function FinalizedView({ session, headingRef }: FinalizedViewProps) {
  const messageId = useId();
  const [isMessageExpanded, setIsMessageExpanded] = useState(false);
  const [copyStatus, setCopyStatus] = useState<"idle" | "copying" | "copied" | "failed">("idle");
  const { cart, final_message: message } = session;
  const memberNames = new Map(session.members.map(({ id, name }) => [id, name]));

  useEffect(() => {
    if (copyStatus !== "copied") return;
    const timer = setTimeout(() => setCopyStatus("idle"), 2200);
    return () => clearTimeout(timer);
  }, [copyStatus]);

  async function copySummary() {
    if (!message || copyStatus === "copying") return;
    setCopyStatus("copying");
    const copied = await copyText(message);
    setCopyStatus(copied ? "copied" : "failed");
    if (!copied) setIsMessageExpanded(true);
  }

  return (
    <div className="finalized-view">
      <header className="final-celebration">
        <span className="final-success-badge" aria-hidden="true">✓</span>
        <h2 ref={headingRef} tabIndex={-1}>Chúc mừng bạn đã đặt đơn thành công</h2>
        <p>Đơn nhóm đã được chốt. Sao chép tin nhắn để gửi vào nhóm chat.</p>
      </header>
      <table className="final-summary" aria-label="Tóm tắt đơn đã chốt">
        <thead>
          <tr>
            <th scope="col" className="summary-member">Tên thành viên</th>
            <th scope="col">Món ăn</th>
            <th scope="col" className="summary-price">Giá tiền</th>
          </tr>
        </thead>
        <tbody>
          {cart?.lines.length ? cart.lines.map((line) => (
            <tr key={`${line.member_id}:${line.menu_item_id}`}>
              <th scope="row">{memberNames.get(line.member_id) ?? line.member_id}</th>
              <td>{line.name}</td>
              <td className="summary-price">{money(line.unit_price)}</td>
            </tr>
          )) : (
            <tr><td colSpan={3} className="field-hint">Chưa có chi tiết món ăn.</td></tr>
          )}
        </tbody>
        {cart && (
          <tfoot>
            <tr>
              <th scope="row" colSpan={2}>
                Tổng tiền
                <span className="summary-shipping">Đã gồm phí giao {money(cart.shipping_fee)}</span>
              </th>
              <td className="summary-price">{money(cart.total)}</td>
            </tr>
            <tr>
              <th scope="row" colSpan={2}>Quỹ nhóm còn lại</th>
              <td className="summary-price">
                {session.budget === null ? "Chưa xác định" : money(session.budget)}
              </td>
            </tr>
          </tfoot>
        )}
      </table>
      <div>
        <div className="final-message-actions">
          {message && (
            <button className="button button--example" type="button" aria-expanded={isMessageExpanded}
              aria-controls={messageId} onClick={() => setIsMessageExpanded((expanded) => !expanded)}>
              {isMessageExpanded ? "Thu gọn tin nhắn" : "Xem tin nhắn chốt"}
            </button>
          )}
          <button className="button button--primary" type="button" disabled={!message || copyStatus === "copying"}
            onClick={() => void copySummary()}>Copy</button>
        </div>
        <p className={`copy-feedback${copyStatus === "failed" ? " field-error" : ""}`} role="status">
          {copyStatus === "copied" && "Đã sao chép!"}
          {copyStatus === "failed" && "Không thể sao chép tự động. Hãy chọn nội dung để sao chép thủ công."}
        </p>
      </div>
      {message
        ? <pre id={messageId} className="final-message" hidden={!isMessageExpanded} aria-label="Tin nhắn chốt đơn">{message}</pre>
        : <p className="field-hint">Chưa có nội dung chốt giỏ.</p>}
    </div>
  );
}
