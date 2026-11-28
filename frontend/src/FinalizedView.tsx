import { useEffect, useState } from "react";
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
    setCopyStatus(await copyText(message) ? "copied" : "failed");
  }

  return (
    <div className="finalized-view">
      <h2 className="order-panel-title" ref={headingRef} tabIndex={-1}>Đơn đã được chốt</h2>
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
          </tfoot>
        )}
      </table>
      {message
        ? <pre className="final-message" aria-label="Tin nhắn chốt đơn">{message}</pre>
        : <p className="field-hint">Chưa có nội dung chốt giỏ.</p>}
      <div className="composer-actions">
        <p className={`copy-feedback${copyStatus === "failed" ? " field-error" : ""}`} role="status">
          {copyStatus === "copied" && "Đã sao chép!"}
          {copyStatus === "failed" && "Không thể sao chép tự động. Hãy chọn nội dung để sao chép thủ công."}
        </p>
        <button className="button button--primary" type="button" disabled={!message || copyStatus === "copying"}
          onClick={() => void copySummary()}>Copy</button>
      </div>
    </div>
  );
}
