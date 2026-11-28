import type { MouseEventHandler, ReactNode, Ref } from "react";
import type { Action, SessionState } from "./session";

type InfeasibleViewProps = {
  session: SessionState;
  busy: boolean;
  headingRef: Ref<HTMLHeadingElement>;
  lockedProfile: ReactNode;
  feedback: ReactNode;
  returnRestaurantAction: ReactNode;
  onAction: (action: Action) => void;
  onReopen: MouseEventHandler<HTMLButtonElement>;
};

export default function InfeasibleView({
  session, busy, headingRef, lockedProfile, feedback, returnRestaurantAction, onAction, onReopen,
}: InfeasibleViewProps) {
  const info = session.infeasible;
  const membersWithoutOption = info?.kind === "NO_SAFE_ITEM"
    ? info.members_without_option.map((id) => session.members.find((member) => member.id === id)?.name ?? id)
    : [];

  return (
    <div className="infeasible-view">
      <button className="button button--plain profile-back-action" type="button" aria-haspopup="dialog"
        disabled={busy} onClick={onReopen}>← Quay lại sửa hồ sơ</button>
      <div className="infeasible-warning">
        <h2 className="order-panel-title infeasible-heading" ref={headingRef} tabIndex={-1}>
          <span aria-hidden="true">⚠️</span> Chưa khả thi
        </h2>
        <p className="infeasible-message">{info?.message ?? "Chưa có thông tin về lý do giỏ chưa khả thi."}</p>
        {membersWithoutOption.length > 0 && (
          <p className="field-hint">Chưa có món phù hợp cho {membersWithoutOption.join(", ")}.</p>
        )}
      </div>
      <p className="field-hint">Chọn một đề xuất hoặc quay lại sửa hồ sơ để điều chỉnh quỹ và yêu cầu của nhóm.</p>
      {lockedProfile}
      {feedback}
      {info && info.options.length > 0 && (
        <div className="infeasible-options" role="group" aria-label="Đề xuất điều chỉnh">
          {info.options.map((option) => (
            <button className="button button--primary" type="button" key={option.id} disabled={busy}
              onClick={() => onAction(option.action)}>
              {option.label}
            </button>
          ))}
        </div>
      )}
      {returnRestaurantAction && (
        <div className="composer-actions infeasible-secondary">{returnRestaurantAction}</div>
      )}
    </div>
  );
}
