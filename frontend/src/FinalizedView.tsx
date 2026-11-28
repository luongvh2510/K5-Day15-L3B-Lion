import { useEffect, useState } from "react";
import type { Ref } from "react";

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
  message: string | null;
  headingRef: Ref<HTMLHeadingElement>;
  onNewOrder: () => void;
};

export default function FinalizedView({ message, headingRef, onNewOrder }: FinalizedViewProps) {
  const [copyStatus, setCopyStatus] = useState<"idle" | "copying" | "copied" | "failed">("idle");

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
      {message
        ? <pre className="final-message" aria-label="Tin nhắn chốt đơn">{message}</pre>
        : <p className="field-hint">Chưa có nội dung chốt giỏ.</p>}
      <div className="composer-actions">
        <p className={`copy-feedback${copyStatus === "failed" ? " field-error" : ""}`} role="status">
          {copyStatus === "copied" && "Đã sao chép!"}
          {copyStatus === "failed" && "Không thể sao chép tự động. Hãy chọn nội dung để sao chép thủ công."}
        </p>
        <button className="button button--example" type="button" onClick={onNewOrder}>Làm đơn mới</button>
        <button className="button button--primary" type="button" disabled={!message || copyStatus === "copying"}
          onClick={() => void copySummary()}>Copy</button>
      </div>
    </div>
  );
}
