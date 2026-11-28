import { useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { api, ApiError } from "./api";
import { ALLERGEN_LABEL } from "./session";
import type { Allergen, Menu, Restaurant } from "./session";

type MenuModalProps = {
  restaurant: Restaurant;
  initialRequest: Promise<Menu>;
  onClose: () => void;
};

type MenuResult = { menu: Menu } | { error: string };

export default function MenuModal({ restaurant, initialRequest, onClose }: MenuModalProps) {
  const titleId = useId();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const [request, setRequest] = useState(initialRequest);
  const [result, setResult] = useState<MenuResult | null>(null);

  useLayoutEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    const opener = document.activeElement;
    dialog.showModal();
    closeRef.current?.focus();
    return () => {
      dialog.close();
      if (opener instanceof HTMLElement && opener.isConnected) opener.focus({ preventScroll: true });
    };
  }, []);

  useEffect(() => {
    let open = true;
    void request.then(
      (menu) => { if (open) setResult({ menu }); },
      (error: unknown) => {
        if (open) setResult({ error: error instanceof ApiError ? error.message : "Chưa tải được menu quán." });
      },
    );
    return () => { open = false; };
  }, [request]);

  return (
    <dialog className="menu-modal" ref={dialogRef} aria-labelledby={titleId}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}>
      <div className="menu-modal-header">
        <h2 id={titleId}>Menu {restaurant.name}</h2>
        <button className="button button--example" type="button" ref={closeRef} onClick={onClose}>Đóng</button>
      </div>
      {!result ? (
        <p className="reading" role="status"><span className="spinner" aria-hidden="true" />Đang tải menu quán…</p>
      ) : "error" in result ? (
        <div className="api-error">
          <p className="field-error" role="alert">{result.error}</p>
          <button className="button button--example" type="button" onClick={() => {
            closeRef.current?.focus();
            setResult(null);
            setRequest(api.menu(restaurant.id));
          }}>Thử lại</button>
        </div>
      ) : result.menu.items.length > 0 ? (
        <ul className="menu-items" aria-label="Món đang bán">
          {result.menu.items.map((item) => (
            <li key={item.id}>
              <div className="menu-item-header">
                <strong>{item.name}</strong>
                <span>{item.price.toLocaleString("vi-VN")}đ</span>
              </div>
              {item.vegetarian && <p className="field-hint">Món chay</p>}
              {item.allergens.length > 0 && (
                <p className="field-hint">
                  Chất gây dị ứng: {item.allergens.map((tag) => ALLERGEN_LABEL[tag.toUpperCase() as Allergen]).join(", ")}
                </p>
              )}
              {!item.ingredients_known && <p className="field-hint">Thông tin thành phần chưa đầy đủ.</p>}
            </li>
          ))}
        </ul>
      ) : (
        <p className="field-hint">Quán chưa có món đang bán.</p>
      )}
    </dialog>
  );
}
