export const ALLERGEN_LABEL = {
  PEANUT: "đậu phộng",
  SOY: "đậu nành",
  WHEAT: "lúa mì",
  EGG: "trứng",
  MILK: "sữa",
  FISH: "cá",
  CRUSTACEAN: "giáp xác (tôm, cua)",
  MOLLUSC: "nhuyễn thể (mực, nghêu, hàu)",
  SESAME: "mè",
  CELERY: "cần tây",
} as const;

export type Allergen = keyof typeof ALLERGEN_LABEL;

export type Restaurant = {
  id: string;
  name: string;
  menu_type: string;
  summary: string;
  distance_km: number;
  shipping_fee: number;
};

export type MenuItem = {
  id: string;
  name: string;
  price: number;
  ingredients: string[];
  allergens: Lowercase<Allergen>[];
  allergen_sources: Partial<Record<Lowercase<Allergen>, string[]>>;
  animal_ingredients: string[];
  vegetarian: boolean;
  available: boolean;
  ingredients_known: boolean;
};

export type Menu = { restaurant: Restaurant; items: MenuItem[] };

export type Source = {
  kind: "CHAT" | "HOST";
  line: number | null;
  quote: string | null;
};

export type HardConstraint = {
  id: string;
  type: "VEGETARIAN" | "ALLERGY";
  allergen: Allergen | null;
  note: null;
  source: Source;
  locked: boolean;
};

export type Preference = {
  id: string;
  text: string;
  source: Source;
};

export type Member = {
  id: string;
  name: string;
  origin: "CHAT" | "HOST_ADDED";
  hard_constraints: HardConstraint[];
  preferences: Preference[];
  flags: [];
  quotes: string[];
};

export type MemberInput = {
  name: string;
  hard_constraints: Pick<HardConstraint, "type" | "allergen">[];
  preferences: Pick<Preference, "text">[];
};

export type Question = {
  id: string;
  member_id: string | null;
  text: string;
  options: [];
  status: "OPEN" | "ANSWERED";
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  kind: "TEXT" | "QUESTION" | "REFUSAL" | "INFO";
  text: string;
  question_id: null;
  turn: number;
  created_at: string;
};

export type CartLine = {
  member_id: string;
  menu_item_id: string;
  name: string;
  type: "MAIN";
  unit_price: number;
  qty: 1;
  line_total: number;
  reason: string | null;
  note: null;
};

export type ExcludedItem = {
  member_id: string;
  menu_item_id: string;
  name: string;
  reasons: { rule: string; text: string }[];
};

export type Cart = {
  lines: CartLine[];
  subtotal: number;
  shipping_fee: number;
  total: number;
  budget: number;
  remaining: number;
  excluded: ExcludedItem[];
  built_by: "AI" | "FALLBACK";
};

export type ValidationResult = {
  ok: boolean;
  violations: [];
};

export type Action =
  | { type: "SET_BUDGET"; budget: number }
  | { type: "CHANGE_RESTAURANT"; restaurant_id?: string };

export type InfeasibleOption = {
  id: "budget" | "restaurant";
  label: string;
  action: Action;
};

export type InfeasibleInfo = {
  kind: "NO_SAFE_ITEM" | "OVER_BUDGET";
  members_without_option: string[];
  min_total: number | null;
  shortfall: number | null;
  message: string;
  options: InfeasibleOption[];
};

export type SessionStatus = "PROFILE_DRAFT" | "CART_VALID" | "CART_INFEASIBLE" | "FINALIZED";

export type SessionState = {
  session_id: string;
  status: SessionStatus;
  restaurant: Restaurant | null;
  budget: number | null;
  chat_lines: [];
  members: Member[];
  questions: Question[];
  can_confirm: boolean;
  messages: ChatMessage[];
  cart: Cart | null;
  validation: ValidationResult | null;
  infeasible: InfeasibleInfo | null;
  final_message: string | null;
};

export type ApiErrorPayload = {
  error: { code: string; message: string };
};
