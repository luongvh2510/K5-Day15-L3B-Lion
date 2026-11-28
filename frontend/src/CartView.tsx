import { useState } from "react";
import type { MouseEventHandler, ReactNode, Ref } from "react";
import type { SessionState } from "./session";

const money = (value: number) => value.toLocaleString("vi-VN") + "đ";
const EXCLUDED_PREVIEW_COUNT = 3;

type CartViewProps = {
  session: SessionState;
  busy: boolean;
  headingRef: Ref<HTMLHeadingElement>;
  lockedProfile: ReactNode;
  feedback: ReactNode;
  onReopen: MouseEventHandler<HTMLButtonElement>;
  onChangeRestaurant: () => void;
  onFinalize: () => void;
};

export default function CartView({
  session, busy, headingRef, lockedProfile, feedback, onReopen, onChangeRestaurant, onFinalize,
}: CartViewProps) {
  const [showAllExcluded, setShowAllExcluded] = useState(false);
  const { cart, restaurant, validation } = session;
  const memberNames = new Map(session.members.map(({ id, name }) => [id, name]));
  const excluded = cart?.excluded ?? [];
  const visibleExcluded = showAllExcluded ? excluded : excluded.slice(0, EXCLUDED_PREVIEW_COUNT);

  return (
    <div className="cart-view">
      <h2 className="order-panel-title" ref={headingRef} tabIndex={-1}>Giỏ hàng</h2>

      {restaurant && (
        <section className="restaurant-card" aria-labelledby="restaurant-heading">
          <div>
            <h3 id="restaurant-heading">{restaurant.name}</h3>
            <p className="restaurant-meta">
              <span>{restaurant.distance_km.toLocaleString("vi-VN")} km</span>
              <span>Phí giao {money(restaurant.shipping_fee)}</span>
            </p>
            <p>{restaurant.summary}</p>
          </div>
          <button className="button button--example" type="button" disabled={busy} onClick={onChangeRestaurant}>
            Đổi quán
          </button>
        </section>
      )}

      {validation?.ok === true && (
        <div className="cart-validation">
          <strong>✓ Giỏ hợp lệ</strong>
          <p>Đã kiểm theo yêu cầu đã xác nhận và menu quán</p>
        </div>
      )}
      {validation?.ok === false && <p className="field-error">Giỏ chưa hợp lệ.</p>}

      {cart ? (
        <>
          <ul className="cart-lines" aria-label="Các suất trong giỏ">
            {cart.lines.map((line) => (
              <li className="cart-line" key={`${line.member_id}:${line.menu_item_id}`}>
                <div className="cart-line-meta">
                  <span className="line-member">{memberNames.get(line.member_id) ?? line.member_id}</span>
                  <strong className="line-price">{money(line.unit_price)}</strong>
                </div>
                <p className="line-dish">{line.name} {line.qty != null && <span className="line-quantity">× {line.qty}</span>}</p>
                {line.reason && <p className="line-reason">{line.reason}</p>}
              </li>
            ))}
          </ul>

          {cart.built_by === "FALLBACK" && <p className="field-hint">Giỏ dự phòng: chọn món rẻ nhất an toàn.</p>}
          <dl className="cart-totals" aria-label="Chi tiết tiền">
            <div><dt>Tạm tính</dt><dd>{money(cart.subtotal)}</dd></div>
            <div><dt>Phí giao</dt><dd>{money(cart.shipping_fee)}</dd></div>
            <div className="cart-total"><dt>Tổng thanh toán</dt><dd>{money(cart.total)}</dd></div>
            <div><dt>Quỹ chung</dt><dd>{money(cart.budget)}</dd></div>
            <div><dt>Còn lại</dt><dd>{money(cart.remaining)}</dd></div>
          </dl>

          {excluded.length > 0 && (
            <section className="excluded-section" aria-labelledby="excluded-heading">
              <div className="excluded-heading">
                <h3 id="excluded-heading">Món bị loại ({excluded.length})</h3>
                {excluded.length > EXCLUDED_PREVIEW_COUNT && (
                  <button className="button button--plain" type="button" disabled={busy}
                    aria-expanded={showAllExcluded} aria-controls="excluded-items"
                    onClick={() => setShowAllExcluded((expanded) => !expanded)}>
                    {showAllExcluded ? "Thu gọn" : "Xem tất cả"}
                  </button>
                )}
              </div>
              <ul id="excluded-items" className="excluded-list">
                {visibleExcluded.map((item) => (
                  <li key={`${item.member_id}:${item.menu_item_id}`}>
                    <strong>{memberNames.get(item.member_id) ?? item.member_id} · {item.name}</strong>
                    {item.reasons.map(({ rule, text }) => <p className="field-hint" key={`${rule}:${text}`}>{text}</p>)}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      ) : (
        <p className="field-hint">Chưa có chi tiết giỏ hàng.</p>
      )}

      {lockedProfile}
      {feedback}
      <div className="composer-actions">
        <button className="button button--example" type="button" disabled={busy} onClick={onReopen}>Sửa hồ sơ</button>
        {cart && validation?.ok === true && (
          <button className="button button--primary" type="button" disabled={busy} onClick={onFinalize}>Chốt giỏ</button>
        )}
      </div>
    </div>
  );
}
