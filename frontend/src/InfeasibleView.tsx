import type { ReactNode, Ref } from "react";
import type { Action, SessionState } from "./session";

type InfeasibleViewProps = {
  session: SessionState;
  busy: boolean;
  headingRef: Ref<HTMLHeadingElement>;
  feedback: ReactNode;
  onAction: (action: Action) => void;
  onReopen: () => void;
};

export default function InfeasibleView({ session, busy, headingRef, feedback, onAction, onReopen }: InfeasibleViewProps) {
  const info = session.infeasible;
  const membersWithoutOption = info?.kind === "NO_SAFE_ITEM"
    ? info.members_without_option.map((id) => session.members.find((member) => member.id === id)?.name ?? id)
    : [];

  return (
    <div className="infeasible-view">
      <h2 className="order-panel-title" ref={headingRef} tabIndex={-1}>Chưa khả thi</h2>
      <p className="infeasible-message">{info?.message ?? "Chưa có thông tin về lý do giỏ chưa khả thi."}</p>
      {membersWithoutOption.length > 0 && (
        <p className="field-hint">Chưa có món phù hợp cho {membersWithoutOption.join(", ")}.</p>
      )}
      {feedback}
      <div className="composer-actions">
        <button className="button button--example" type="button" disabled={busy} onClick={onReopen}>Sửa hồ sơ</button>
        {info?.options.map((option) => (
          <button className="button button--primary" type="button" key={option.id} disabled={busy}
            onClick={() => onAction(option.action)}>
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
