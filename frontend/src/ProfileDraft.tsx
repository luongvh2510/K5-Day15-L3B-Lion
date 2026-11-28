import { useId, useState } from "react";
import type { FormEvent, ReactNode, Ref } from "react";
import { ALLERGEN_LABEL } from "./session";
import type { Allergen, HardConstraint, Member, MemberInput, SessionState } from "./session";

function constraintLabel(constraint: HardConstraint) {
  if (constraint.type === "VEGETARIAN") return "Ăn chay";
  return constraint.allergen ? `Dị ứng ${ALLERGEN_LABEL[constraint.allergen]}` : "Dị ứng chưa rõ loại";
}

function toMemberInput(member: MemberInput): MemberInput {
  return {
    name: member.name,
    hard_constraints: member.hard_constraints.map(({ type, allergen }) => ({ type, allergen })),
    preferences: member.preferences.map(({ text }) => ({ text })),
  };
}

type SaveMembers = (members: MemberInput[], memberName: string | null, afterSuccess?: () => void) => void;

type MemberCardProps = {
  member: Member;
  hasQuestion: boolean;
  editable: boolean;
  busy: boolean;
  feedback?: ReactNode;
  onChange: (changes: Partial<MemberInput>, afterSuccess?: () => void) => void;
  onRemove: () => void;
};

function MemberCard({ member, hasQuestion, editable, busy, feedback, onChange, onRemove }: MemberCardProps) {
  const fieldId = useId();
  const [editor, setEditor] = useState<"hard" | "soft" | null>(null);
  const [constraintType, setConstraintType] = useState<HardConstraint["type"]>("VEGETARIAN");
  const [allergen, setAllergen] = useState<Allergen>("PEANUT");
  const [preferenceText, setPreferenceText] = useState("");
  const [error, setError] = useState("");
  const hasLockedConstraint = member.hard_constraints.some((constraint) => constraint.locked);

  function toggleEditor(kind: "hard" | "soft") {
    setEditor(editor === kind ? null : kind);
    setError("");
  }

  function addDetail(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editable || busy) return;
    if (editor === "hard") {
      const newConstraint = { type: constraintType, allergen: constraintType === "ALLERGY" ? allergen : null };
      if (member.hard_constraints.some((item) => item.type === newConstraint.type && item.allergen === newConstraint.allergen)) {
        setError("Ràng buộc này đã có.");
        return;
      }
      onChange({ hard_constraints: [...member.hard_constraints, newConstraint] }, () => setEditor(null));
    } else if (editor === "soft") {
      const text = preferenceText.trim();
      if (!text) {
        setError("Nhập một sở thích hoặc món không thích.");
        return;
      }
      if (member.preferences.some((item) => item.text === text)) {
        setError("Sở thích này đã có.");
        return;
      }
      onChange({ preferences: [...member.preferences, { text }] }, () => {
        setPreferenceText("");
        setEditor(null);
      });
    }
    setError("");
  }

  return (
    <li className="member-card">
      <div className="member-header">
        <h3>{member.name}</h3>
        {hasQuestion && <span className="member-flag"><span aria-hidden="true">❓</span> Cần làm rõ</span>}
        {editable && (
          <button
            className="button button--plain remove-member"
            type="button"
            disabled={busy || hasLockedConstraint}
            title={hasLockedConstraint ? "Thành viên có ràng buộc đã khóa" : undefined}
            aria-label={`Xóa thành viên ${member.name}`}
            onClick={onRemove}
          >
            Xóa người
          </button>
        )}
      </div>

      <dl className="member-details">
        <div>
          <dt>Bắt buộc</dt>
          {member.hard_constraints.length === 0 && <dd className="not-recorded">Chưa ghi nhận</dd>}
          {member.hard_constraints.map((constraint) => (
            <dd className="requirement" key={constraint.id}>
              <div className="requirement-line">
                <span className="requirement-tag requirement-tag--hard">
                  {constraintLabel(constraint)}
                  {constraint.locked && <span role="img" aria-label=" Đã khóa" title="Đã khóa"> 🔒</span>}
                </span>
                {editable && !constraint.locked && (
                  <button className="chip-remove" type="button" disabled={busy}
                    aria-label={`Xóa ràng buộc ${constraintLabel(constraint)} của ${member.name}`}
                    onClick={() => onChange({
                      hard_constraints: member.hard_constraints.filter((item) => item.id !== constraint.id),
                    })}
                  >×</button>
                )}
              </div>
              {constraint.source.kind === "HOST" && <span className="field-hint">Người đặt thêm</span>}
            </dd>
          ))}
        </div>
        <div>
          <dt>Sở thích</dt>
          {member.preferences.length === 0 && <dd className="not-recorded">Chưa ghi nhận</dd>}
          {member.preferences.map((preference) => (
            <dd className="requirement" key={preference.id}>
              <div className="requirement-line">
                <span className="requirement-tag requirement-tag--soft">{preference.text}</span>
                {editable && (
                  <button className="chip-remove" type="button" disabled={busy}
                    aria-label={`Xóa sở thích ${preference.text} của ${member.name}`}
                    onClick={() => onChange({
                      preferences: member.preferences.filter((item) => item.id !== preference.id),
                    })}
                  >×</button>
                )}
              </div>
              {preference.source.kind === "HOST" && <span className="field-hint">Người đặt thêm</span>}
            </dd>
          ))}
        </div>
      </dl>

      {member.quotes.length > 0 && (
        <blockquote className="member-quotes">
          {member.quotes.map((quote, index) => <p key={index}>{quote}</p>)}
        </blockquote>
      )}

      {editable && (
        <div className="member-edit">
          <div className="editor-actions">
            <button className="button button--plain" type="button" disabled={busy} aria-expanded={editor === "hard"}
              onClick={() => toggleEditor("hard")}>Thêm ràng buộc</button>
            <button className="button button--plain" type="button" disabled={busy} aria-expanded={editor === "soft"}
              onClick={() => toggleEditor("soft")}>Thêm sở thích</button>
          </div>
          {editor && (
            <form className="member-editor" onSubmit={addDetail}>
              <fieldset disabled={busy}>
                {editor === "hard" ? (
                  <>
                    <label htmlFor={`${fieldId}-type`}>Loại ràng buộc</label>
                    <select id={`${fieldId}-type`} value={constraintType}
                      onChange={(event) => { setConstraintType(event.target.value as HardConstraint["type"]); setError(""); }}>
                      <option value="VEGETARIAN">Ăn chay</option>
                      <option value="ALLERGY">Dị ứng</option>
                    </select>
                    {constraintType === "ALLERGY" && (
                      <>
                        <label htmlFor={`${fieldId}-allergen`}>Chất gây dị ứng</label>
                        <select id={`${fieldId}-allergen`} value={allergen}
                          onChange={(event) => { setAllergen(event.target.value as Allergen); setError(""); }}>
                          {Object.entries(ALLERGEN_LABEL).map(([code, label]) =>
                            <option key={code} value={code}>{label}</option>
                          )}
                        </select>
                      </>
                    )}
                  </>
                ) : (
                  <>
                    <label htmlFor={`${fieldId}-preference`}>Sở thích hoặc món không thích</label>
                    <input id={`${fieldId}-preference`} value={preferenceText} placeholder="Ví dụ: Không thích món cay"
                      onChange={(event) => { setPreferenceText(event.target.value); setError(""); }} />
                  </>
                )}
                {error && <p className="field-error" role="alert">{error}</p>}
                {feedback}
                <button className="button button--example" type="submit">Lưu</button>
              </fieldset>
            </form>
          )}
          {!editor && feedback}
        </div>
      )}
    </li>
  );
}

type ProfileDraftProps = {
  session: SessionState;
  busy: boolean;
  openMemberIds: ReadonlySet<string | null>;
  onEdit: SaveMembers;
  headingRef?: Ref<HTMLHeadingElement>;
  editFeedback?: { memberName: string | null; content: ReactNode };
};

const nameKey = (name: string) => name.trim().normalize("NFC").toLocaleLowerCase("vi-VN");

export default function ProfileDraft({ session, busy, openMemberIds, onEdit, headingRef, editFeedback }: ProfileDraftProps) {
  const [newName, setNewName] = useState("");
  const [nameError, setNameError] = useState("");
  const editable = session.status === "PROFILE_DRAFT";
  const useAddFormForFeedback = editFeedback && !session.members.some((member) => member.name === editFeedback.memberName);

  function save(members: MemberInput[], memberName: string | null, afterSuccess?: () => void) {
    if (!editable || busy) return;
    onEdit(members.map(toMemberInput), memberName, afterSuccess);
  }

  function addMember(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const name = newName.trim();
    if (!name) {
      setNameError("Nhập tên thành viên.");
      return;
    }
    if (session.members.some((member) => nameKey(member.name) === nameKey(name))) {
      setNameError("Tên này đã có trong nhóm.");
      return;
    }
    setNameError("");
    save([...session.members, { name, hard_constraints: [], preferences: [] }], null, () => setNewName(""));
  }

  return (
    <div className="draft">
      <div className="draft-header">
        <h2 ref={headingRef} tabIndex={-1}>Hồ sơ nhóm</h2>
        {editable && <span className="draft-badge">Bản nháp</span>}
      </div>
      <ul className="members" aria-label="Hồ sơ từng người">
        {session.members.map((member) => (
          <MemberCard
            key={member.name}
            member={member}
            hasQuestion={openMemberIds.has(member.id)}
            editable={editable}
            busy={busy}
            feedback={editFeedback?.memberName === member.name ? editFeedback.content : undefined}
            onChange={(changes, afterSuccess) =>
              save(session.members.map((item) => item.id === member.id ? { ...item, ...changes } : item),
                member.name, afterSuccess)
            }
            onRemove={() => {
              if (!member.hard_constraints.some((constraint) => constraint.locked)) {
                save(session.members.filter((item) => item.id !== member.id), member.name);
              }
            }}
          />
        ))}
      </ul>
      {editable && (
        <form className="add-member" onSubmit={addMember}>
          <label htmlFor="member-name">Tên thành viên mới</label>
          <div className="editor-actions">
            <input id="member-name" value={newName} disabled={busy} aria-invalid={Boolean(nameError)}
              aria-describedby={nameError ? "member-name-error" : undefined}
              onChange={(event) => { setNewName(event.target.value); setNameError(""); }} />
            <button className="button button--example" type="submit" disabled={busy}>Thêm người</button>
          </div>
          {nameError && <p id="member-name-error" className="field-error" role="alert">{nameError}</p>}
          {useAddFormForFeedback && editFeedback.content}
        </form>
      )}
    </div>
  );
}
