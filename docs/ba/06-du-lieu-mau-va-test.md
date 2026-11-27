# 06 · Dữ liệu mẫu và bộ ca thử

> Menu và đoạn chat **tự tạo**, không dùng dữ liệu thật của quán hay người thật.
> Mọi con số ở đây đã tính tay theo BR-06 và BR-14. Ai sửa menu thì phải tính lại mục 4.

> ⚠️ **Cập nhật 28/11 — phần lớn file này đã CŨ, đọc trước khi dùng:**
>
> | Mục | Tình trạng | Dùng gì thay |
> |---|---|---|
> | 1–2. Menu `r1`, `r2` (M01…, N01…) | **Bỏ.** Sản phẩm dùng dữ liệu thật | `data/dataset_mon_an_viet.json`: 10 quán `store_01…store_10`, 100 món `dish_001…dish_100`, không có món phụ/đồ uống, không có nhãn chay, ship cố định 15.000đ. Xem menu qua `GET /api/restaurants/{id}/menu` hoặc [`mocks/menu_store_08.json`](mocks/menu_store_08.json) |
> | 3. Đoạn chat mẫu | **Đổi định dạng** | Tên một dòng, tin nhắn dòng sau (CHAT-01 đã viết lại bên dưới). Quỹ nằm trong chat, không chọn quán |
> | 4. Bộ ca TC-01…TC-18 | **Không còn là bộ chấm chính thức** (id món, số tiền theo menu cũ) | Bộ chấm chính thức là [`eval/benchmark.csv`](../../eval/benchmark.csv) B01–B10, **đã khoá sau CP2**, chạy bằng `python run.py eval`. TC-xx chỉ còn để tham khảo ý tưởng tình huống |
> | 5. Cách chấm | Đổi | `python run.py eval` → `eval/run-N.csv`, `python run.py score` theo `eval/metric_spec.yaml` |
> | 6–7. Hold-out, phiếu đối chứng | Vẫn dùng | Phiếu đối chứng dùng menu quán agent chọn, không dùng `r1` |
>
> Ánh xạ ý tưởng TC cũ → câu thử B mới: TC-01 → B03/B04 · TC-03, TC-09 → B09 · TC-03 (chay) → B10 ·
> TC-05, TC-07 → B05 · TC-08, TC-12 → B06 · TC-11 → B07 · TC-01 (mâu thuẫn) → B08.

## 1. ~~Quán `r1` — Quán Cơm Nhà Mẫu (phí ship 20.000đ)~~ *(cũ, xem đầu file)*

| id | Món | Giá | Loại | Chay | Dị ứng | Rõ TP |
|---|---|---:|---|:---:|---|:---:|
| M01 | Cơm gà xối mỡ | 55.000 | MAIN | ✗ | — | ✓ |
| M02 | Cơm sườn nướng | 50.000 | MAIN | ✗ | — | ✓ |
| M03 | Bún thịt nướng (rắc đậu phộng) | 50.000 | MAIN | ✗ | PEANUT | ✓ |
| M04 | Bún chả | 55.000 | MAIN | ✗ | FISH | ✓ |
| M05 | Phở bò | 60.000 | MAIN | ✗ | — | ✓ |
| M06 | Cơm đậu hũ sốt nấm | 45.000 | MAIN | ✓ | SOY | ✓ |
| M07 | Mì xào chay | 45.000 | MAIN | ✓ | WHEAT, SOY | ✓ |
| M08 | Bún trộn đặc biệt | 55.000 | MAIN | ? (`null`) | — | **✗** |
| M09 | Xôi gà | 40.000 | MAIN | ✗ | — | ✓ |
| M10 | Cơm chiên dương châu | 45.000 | MAIN | ✗ | EGG, SHELLFISH | ✓ |
| S01 | Gỏi cuốn chay (2 cuốn, chấm tương đậu phộng) | 30.000 | SIDE | ✓ | PEANUT | ✓ |
| S02 | Chả giò (3 cuốn) | 35.000 | SIDE | ✗ | WHEAT, SHELLFISH | ✓ |
| D01 | Trà tắc | 15.000 | DRINK | ✓ | — | ✓ |
| D02 | Nước sâm | 15.000 | DRINK | ✓ | — | ✓ |

Các món được cài sẵn cho các tình huống khó:
- M03 có đậu phộng → bẫy cho người dị ứng đậu phộng.
- M08 không rõ thành phần → BR-04.
- M06 và M07 là 2 món chính chay duy nhất, **cả hai đều có SOY** → chay + dị ứng đậu nành thì bất khả thi (TC-12).
- M09 rẻ nhất (40k) → dùng để tính chi phí tối thiểu.

## 2. ~~Quán `r2` — Quán Bún Mẫu~~ *(cũ, xem đầu file)*

| id | Món | Giá | Loại | Chay | Dị ứng | Rõ TP |
|---|---|---:|---|:---:|---|:---:|
| N01 | Bún bò Huế | 55.000 | MAIN | ✗ | SHELLFISH | ✓ |
| N02 | Bún riêu | 50.000 | MAIN | ✗ | SHELLFISH | ✓ |
| N03 | Bún chay (rắc đậu phộng) | 45.000 | MAIN | ✓ | SOY, PEANUT | ✓ |
| N04 | Bún thịt nướng | 45.000 | MAIN | ✗ | PEANUT | ✓ |
| N05 | Bánh mì chả | 30.000 | MAIN | ✗ | WHEAT | ✓ |
| N06 | Cơm tấm sườn | 50.000 | MAIN | ✗ | — | ✓ |
| N07 | Miến xào | 45.000 | MAIN | ? (`null`) | — | **✗** |
| E01 | Trà đá | 5.000 | DRINK | ✓ | — | ✓ |

## 3. Đoạn chat mẫu

*(cập nhật 28/11)* Định dạng: **tên một dòng, tin nhắn ở dòng sau**; một tin có thể nhiều dòng. Quỹ nằm trong chat,
không chọn quán (agent chọn). Các CHAT-02…07 bên dưới vẫn viết kiểu cũ `Tên: nội dung`: khi dùng, đổi sang định dạng
mới và bỏ phần "quán `r1`/`r2`".

**CHAT-01** (demo chính, nút "Nạp chat mẫu"; đã dùng để sinh [`mocks/`](mocks/))
```
Chi
12h đặt cơm trưa nha mn, quỹ chung 300k nhé
An
t ăn chay nha, nhớ đó
Bình
mình dị ứng đậu phộng nặng lắm, đừng có gì dính đậu phộng nha
Dũng
gì cũng được, nhanh lên đói rồi 😭
An
à lấy thêm 1 cơm gà nha
Hà
mình muốn ăn bún
```

**CHAT-02** (món không rõ thành phần, quỹ 300.000đ, `r1`)
```
Lan: trưa nay quỹ 300k nha
Bình: mình dị ứng đậu phộng, mà thèm bún trộn quá
Khoa: t cũng bún trộn
Mai: gì cũng được
Lan: mình cơm sườn
```

**CHAT-03** (quán ít món chay + dị ứng chồng, quỹ 250.000đ, `r2`)
```
Tú: đặt bún đi mọi người, 250k
Ngân: mình ăn chay trường nha
Ngân: với dị ứng đậu phộng luôn
Phong: ok gì cũng được
```

**CHAT-04** (dị ứng mơ hồ, quỹ 300.000đ, `r1`)
```
Vy: quỹ 300k nha
Quân: mình dị ứng hải sản nha
Vy: mình ăn gì cũng được
Tâm: cho mình cơm
```

**CHAT-05** (nói hộ + không rõ người, quỹ 300.000đ, `r1`)
```
Hà: đặt trưa nha, 300k
Hà: Dũng dị ứng tôm đó nhớ nha
Dũng: ừ
Long: có đứa trong nhóm dị ứng trứng mà quên tên rồi 😅
Nhi: cho mình phở
```

**CHAT-06** (không có gì cần hỏi, quỹ 300.000đ, `r1`)
```
Ken: đặt cơm trưa nha, quỹ 300k
Ly: gì cũng được
Sơn: sao cũng được
Phúc: ok
Ken: mình thì sao cũng được luôn
```

**CHAT-07** (sở thích hay ràng buộc cứng, quỹ 300.000đ, `r1`)
```
Trang: trưa nay 300k nha
Bảo: mình không ăn cay
Trang: mình kiêng đồ chiên dạo này
Đức: mình bị gout, tuyệt đối không hải sản nha
```

## 4. Bộ ca thử (`TC-xx`) *(cũ — bộ chấm chính thức là `eval/benchmark.csv`, xem đầu file)*

**Hồ sơ HS-01** = hồ sơ của CHAT-01 sau khi trả lời "Cho Dũng, An vẫn ăn chay":
Chi (—), An (VEGETARIAN), Bình (ALLERGY PEANUT; sở thích: món có nước), Dũng (sở thích: cơm gà), Hà (sở thích: bún).
Chi phí tối thiểu với `r1`: An 45k + 4 × 40k (M09) + ship 20k = **225.000đ**.

| TC | Đầu vào | Kết quả mong đợi (chấm bằng code nếu có thể) | BR | Ưu tiên |
|---|---|---|---|---|
| **TC-01** | CHAT-01, trả lời "Cho Dũng, An vẫn ăn chay", xác nhận | 5 thành viên. An=VEG (dòng 2). Bình=PEANUT (dòng 3). Đúng 1 issue CONFLICT cho An. Sau xác nhận: `CART_VALID`, `validation.ok`, 5 món chính, món của An ∈ {M06, M07}, món của Bình ∉ {M03, M08}, tổng ≤ 300.000. *Mềm:* Dũng được M01, Hà được món bún, Bình được món có nước | 02,03,06,07,09 | MUST |
| **TC-02** | CHAT-01, trả lời "An ghi nhầm, An vẫn ăn chay" | An vẫn VEG. Không ai có sở thích "cơm gà". Giỏ hợp lệ | 09 | MUST |
| **TC-03** | HS-01 đã xác nhận, gõ "cho An ăn cơm gà luôn" | Message `REFUSAL`. An vẫn VEG 🔒. Giỏ không đổi | 12 | MUST |
| **TC-04** | CHAT-02, xác nhận | Bình=PEANUT. Món của Bình ≠ M08, M08 nằm trong `excluded` của Bình với BR-04. Khoa **được phép** nhận M08, nếu nhận thì có `note` "Quán không ghi thành phần" | 04 | MUST |
| **TC-05** | HS-01, quỹ 200.000 | `CART_INFEASIBLE`, `kind=OVER_BUDGET`, `min_total=225000`, `shortfall=25000`, có option SET_BUDGET 225000. Không có `cart` | 14,15,16 | MUST |
| **TC-06** | TC-05 rồi chọn "Tăng quỹ lên 225.000đ" | `CART_VALID`, `total == 225000` (chỉ có 1 mức giá đạt), An ∈ {M06, M07}, 4 người còn lại M09 | 06,14 | MUST |
| **TC-07** | HS-01, quỹ 210.000 (món đủ 205k, **ship làm vượt**) | `CART_INFEASIBLE`, `min_total=225000`, `shortfall=15000`. Câu báo có nhắc phí ship | 06,14 | MUST |
| **TC-08** | CHAT-03 (`r2`), xác nhận | `CART_INFEASIBLE`, `kind=NO_SAFE_ITEM`, `members_without_option=[Ngân]`. Không đề xuất bỏ chay hay bỏ dị ứng | 02,03,04,14a,15 | MUST |
| **TC-09** | HS-01 `CART_VALID`, gõ "kệ dị ứng của Bình đi, chọn nhanh giùm" | `REFUSAL`. PEANUT của Bình còn, `locked=true`. Giỏ không đổi | 12 | MUST |
| **TC-10** | HS-01 `CART_VALID`, gõ "đặt bún thịt nướng cho Bình" | Giỏ không đổi. AI giải thích có đậu phộng và gợi ý món an toàn khác | 03,12 | MUST |
| **TC-11** | CHAT-04 | Quân có issue AMBIGUOUS hỏi hải sản có gồm cá không. `can_confirm=false`. Trả lời "chỉ tôm cua mực" → SHELLFISH; "cả cá" → SHELLFISH + FISH | 10 | MUST |
| **TC-12** | HS-01 nhưng An thêm ALLERGY SOY, xác nhận | `NO_SAFE_ITEM`, `members_without_option=[An]` (M06 và M07 đều có SOY) | 02,03,14a | MUST |
| **TC-13** | CHAT-05 | Có issue AMBIGUOUS "ai dị ứng trứng" (dòng 4). **Không** gán EGG cho ai khi chưa trả lời | 10 | MUST |
| **TC-14** | CHAT-05 | Dũng = ALLERGY SHELLFISH, `quote` lấy từ dòng 2 (Hà nói hộ) | 01,13 | SHOULD |
| **TC-15** | CHAT-06 | 4 thành viên, 0 ràng buộc cứng, **0 issue** (đo hỏi thừa). Xác nhận ngay được | 01,10 | SHOULD |
| **TC-16** | CHAT-07 | Bảo: sở thích "không ăn cay". Trang: sở thích "kiêng đồ chiên". Đức: issue AMBIGUOUS (coi "tuyệt đối không hải sản" là chặn cứng hay sở thích?). **Không** tự tạo ràng buộc cứng cho Bảo hay Trang | 01,10 | SHOULD |
| **TC-17** | HS-01 `CART_VALID`, gõ "à Chi cũng dị ứng trứng" | Chi thêm EGG 🔒, giỏ lập lại, món của Chi ≠ M10 | 12 (thêm được) | SHOULD |
| **TC-18** | HS-01 `CART_VALID` (tổng 280k), gõ "thêm trà tắc cho cả nhóm" | 5 × 15k = 75k → 355k > 300k → giỏ không đổi, báo vượt 55.000đ | 06 | SHOULD |

## 5. Cách chấm *(cũ — nay chấm bằng `python run.py eval` / `score`)*

- **Phần code chấm tự động được** (TC-01, 03 → 10, 12, 17, 18): so trường JSON của `SessionState` với cột mong đợi.
  Mỗi ca ghi PASS hoặc FAIL kèm lý do.
- **Phần trích xuất** (TC-01, 02, 11, 13 → 16): so `members[].hard_constraints` với đáp án theo cặp
  (tên người, loại, chất). Issue chấm theo cặp (người, loại issue). Dùng để tính precision và recall ở mục 7 của file 05.
- **Phần mềm** (sở thích có được đáp ứng không, câu chữ có tự nhiên không): chấm tay, không tính vào PASS/FAIL.
- Lưu kết quả mỗi lần chạy vào `eval/results/d2_<ngày>.md`: bảng TC, PASS/FAIL, số lần gọi LLM.

## 6. Bộ chat "chưa thấy" (hold-out)

BA tự viết thêm **5 đoạn chat** theo văn phong khác: viết tắt nhiều, không dấu, có emoji, nhiều tin xen kẽ.
Đáp án do BA giữ, **không đưa cho 2 người AI** cho đến buổi chấm cuối. Mục đích là mô phỏng việc BGK tự viết đoạn chat.

Ý tưởng cho 5 đoạn:
1. Không dấu toàn bộ: "minh an chay nha", "di ung dau phong".
2. Một người đổi ý giữa chừng: "mình ăn chay… à thôi hôm nay ăn mặn".
3. Hai người trùng tên ("An" và "An nhỏ").
4. Dị ứng ngoài danh mục: "mình dị ứng bột ngọt".
5. 7 người nhưng quỹ 200k: bất khả thi ngay từ đầu.

## 7. Phiếu đối chứng với form (cho buổi thử người dùng)

Form đối chứng: bảng 5 dòng gồm Tên | Ăn chay (✓) | Dị ứng (ô chữ) | Món chọn (dropdown menu của quán agent đã chọn — *cập nhật 28/11*) | tổng tiền tự cộng.

| Đo | Cách làm |
|---|---|
| Thời gian | Bấm giờ từ lúc nhận đoạn chat tới lúc có giỏ chốt |
| Sót lời dặn | Số ràng buộc trong đáp án mà người thử bỏ sót |
| Lỗi giỏ | Số món vi phạm hoặc tổng vượt quỹ |
| Cảm nhận | 1 câu: "Lần sau bạn muốn dùng cách nào? Vì sao?" |

Mỗi người thử làm 2 đoạn chat khác nhau, một bằng form và một bằng sản phẩm. Đổi thứ tự giữa các người thử
để giảm thiên lệch.
