# Đồ án thực Hành Trí tuệ nhân tạo – Các bài toán minh họa

Dự án gồm 3 chương trình minh họa các bài toán cơ bản trong môn thực hành Trí tuệ nhân tạo,  
được xây dựng bằng Python và giao diện Tkinter, tập trung vào tính trực quan và dễ hiểu.

---

## Các chương trình trong dự án

# Tìm đường trong bản đồ – A\*

Chương trình mô phỏng bài toán tìm đường đi ngắn nhất từ điểm bắt đầu (Start)  
đến điểm đích (Goal) trong bản đồ dạng lưới 2D bằng thuật toán A\*

---

## Mục tiêu

- Giúp hiểu rõ cách hoạt động của thuật toán A\* và heuristic

---

## Thuật toán sử dụng

- A\*
- Heuristic
- Chi phí mỗi bước đi = 1

---

## Mô tả bản đồ

- `#` : Vật cản (không đi được)
- `.` : Đường đi
- `S` : Start (điểm bắt đầu)
- `G` : Goal (điểm đích)

---

## Chức năng chính

- Hiển thị bản đồ dạng lưới 2D
- Click chuột để:
  - Thêm / xóa vật cản
  - Thay đổi vị trí Start hoặc Goal
- Chạy thuật toán A\* để:
  - Tìm đường đi ngắn nhất
  - Hiển thị các ô đã duyệt
  - Hiển thị đường đi tìm được

---

## Giao diện

- Màu đen: vật cản
- Màu xanh nhạt: các ô đã duyệt
- Màu vàng: đường đi kết quả
- Màu xanh lá: Start
- Màu đỏ: Goal

---

## Cách chạy chương trình

```bash
python Mapmini.py
```

### 2. Caro AI – Minimax + Alpha-Beta (`Caro.py`)

Mô phỏng trò chơi Caro giữa người chơi và máy

**Mô tả ngắn gọn:**

- Người chơi đánh trước (X), AI đánh sau (O)
- AI sử dụng thuật toán **Minimax** kết hợp **cắt tỉa Alpha-Beta**
- Tự động chọn nước đi tối ưu

**Chức năng chính:**

- Hỗ trợ bàn cờ: 3×3, 5×5, 10×10
- Kiểm tra thắng – thua – hòa
- Hiển thị kết quả bằng giao diện đồ họa

**Chạy chương trình:**

```bash
python Caro.py
```

# Tô màu

Chương trình mô phỏng bài toán tô màu đồ thị (Graph Coloring)
với ràng buộc: hai vùng (đỉnh) kề nhau không được trùng màu

---

## Mục tiêu

- Minh họa bài toán ràng buộc
- Hiểu cách áp dụng heuristic trong tô màu đồ thị

---

## Thuật toán sử dụng

- Chiến lược tham lam (heuristic):
  - Chọn đỉnh có bậc lớn nhất
  - Tô màu hợp lệ nhỏ nhất có thể
  - Cập nhật ràng buộc cho các đỉnh kề

---

## Chức năng chính

- Tạo bản đồ ngẫu nhiên với:
  - 3 đến 12 vùng (đỉnh)
- Tô màu tự động sao cho:
  - Không có 2 vùng kề nhau trùng màu
- Cho phép:
  - Chỉnh sửa bảng màu hiển thị
  - Click vào từng vùng để đổi màu thủ công
- Luôn kiểm tra ràng buộc tô màu hợp lệ

---

## Giao diện

- Mỗi vùng được biểu diễn bằng một hình tròn
- Các cạnh thể hiện mối quan hệ kề nhau
- Màu sắc hiển thị theo bảng màu người dùng nhập

---

## ▶ Cách chạy chương trình

```bash
python Tomau.py
```
