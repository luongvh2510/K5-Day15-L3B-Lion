import { useId, useLayoutEffect, useRef } from "react";

type ConfirmModalProps = {
  onCancel: () => void;
  onConfirm: () => void;
};

export default function ConfirmModal({ onCancel, onConfirm }: ConfirmModalProps) {
  const titleId = useId();
  const descriptionId = useId();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);

  useLayoutEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    const previousFocus = document.activeElement;
    dialog.showModal();
    cancelRef.current?.focus();
    return () => {
      dialog.close();
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) {
        previousFocus.focus({ preventScroll: true });
      }
    };
  }, []);

  return (
    <dialog
      className="confirm-modal"
      ref={dialogRef}
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
      onCancel={(event) => {
        event.preventDefault();
        onCancel();
      }}
    >
      <h2 id={titleId}>Sửa hồ sơ</h2>
      <p id={descriptionId}>Giỏ hiện tại sẽ bị huỷ và bạn phải xác nhận lại hồ sơ. Tiếp tục?</p>
      <div className="confirm-modal-actions">
        <button className="button button--example" type="button" ref={cancelRef} onClick={onCancel}>Huỷ</button>
        <button className="button button--primary" type="button" onClick={onConfirm}>Tiếp tục sửa hồ sơ</button>
      </div>
    </dialog>
  );
}
