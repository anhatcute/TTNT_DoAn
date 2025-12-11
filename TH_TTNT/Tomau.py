import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import math



#  THUẬT TOÁN TÔ MÀU ĐỒ THỊ
class GraphColoring:
    """
    - Ràng buộc: 2 đỉnh kề nhau không trùng màu
    - Chiến lược: chọn đỉnh có bậc lớn nhất, tô màu hiện tại,
      hạ bậc + cấm màu cho các đỉnh kề
    """

    def __init__(self, adjacency):
      #Đỉnh kề
        self.adj = adjacency
        self.n = len(adjacency)
        self.colors = [0] * self.n
        self.deg = [len(self.adj[u]) for u in range(self.n)]
        self.forbidden = [set() for _ in range(self.n)]

    def all_colored(self):
        return all(c != 0 for c in self.colors)

    def choose_vertex(self, color_id: int):
        """
        Chọn đỉnh:
        - chưa tô
        - bậc hiện tại lớn nhất
        """
        best = None
        best_deg = -1
        for u in range(self.n):
            if self.colors[u] == 0 and color_id not in self.forbidden[u]:
                if self.deg[u] > best_deg:
                    best_deg = self.deg[u]
                    best = u
        return best

    def color_graph(self):
        current_color = 0

        while not self.all_colored():
            current_color += 1

            while True:
                u = self.choose_vertex(current_color)
                if u is None:
                    break

                #tô màu 
                self.colors[u] = current_color
                self.deg[u] = 0

                #hạ bậc
                for v in self.adj[u]:
                    if self.colors[v] == 0:
                        if self.deg[v] > 0:
                            self.deg[v] -= 1
                        self.forbidden[v].add(current_color)

        return self.colors



#  GIAO DIỆN TÔ MÀU BẢN ĐỒ

class MapColoringApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tô màu bản đồ")

        #Thanh đk
        top_frame = tk.Frame(root)
        top_frame.pack(pady=5)

        tk.Label(top_frame, text="Số vùng (đỉnh) 3–12:").pack(side=tk.LEFT, padx=5)
        self.n_entry = tk.Entry(top_frame, width=5)
        self.n_entry.insert(0, "6")
        self.n_entry.pack(side=tk.LEFT)

        tk.Button(top_frame, text="Tạo bản đồ", command=self.generate_map).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Tô màu tự động", command=self.auto_color).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Cập nhật màu", command=self.update_colors).pack(side=tk.LEFT, padx=5)

        #vẽ bản đồ
        self.canvas = tk.Canvas(root, width=700, height=500, bg="white")
        self.canvas.pack(pady=10)

        #click 
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        #Bảng màu
        palette_frame = tk.LabelFrame(root, text="Bảng màu (có thể sửa tên/mã màu)")
        palette_frame.pack(pady=5, padx=10, fill=tk.X)

       
        default_colors = [
                 "red",        
                 "blue",      
                 "yellow",    
                 "green",      
                 "purple",     
                 "orange",    
                 "pink",     
                 "cyan",      
]


        self.color_entries = []
        for i, col in enumerate(default_colors, start=1):
            f = tk.Frame(palette_frame)
            f.pack(side=tk.LEFT, padx=4, pady=3)
            tk.Label(f, text=f"Màu {i}:").pack()
            e = tk.Entry(f, width=10)
            e.insert(0, col)
            e.pack()
            self.color_entries.append(e)

        #Dữ liệu
        self.n = 0
        self.adj = {}             
        self.positions = []        
        self.colors = []          
        self.node_names = []       
        self.node_radius = 25      


    def get_palette(self):
        palette = [e.get().strip() for e in self.color_entries if e.get().strip()]
        if not palette:
            palette = ["lightgray"]
        return palette

    def compute_positions(self):
        #Tính vị trí các đỉnh trên vòng tròn
        self.positions = []
        cx, cy = 350, 250
        R = 200
        for i in range(self.n):
            angle = 2 * math.pi * i / self.n
            x = cx + R * math.cos(angle)
            y = cy + R * math.sin(angle)
            self.positions.append((x, y))


    def generate_map(self):
        #Tạo bản đồ ngẫu nhiên với n đỉnh
        try:
            n = int(self.n_entry.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Số vùng phải là số nguyên.")
            return

        if n < 3 or n > 12:
            messagebox.showerror("Lỗi", "Nên chọn từ 3 đến 12 vùng để hiển thị đẹp.")
            return

        self.n = n
        self.node_names = [chr(ord('A') + i) for i in range(n)]

        #tạo adjacency list rỗng
        self.adj = {u: set() for u in range(n)}

        #tạo cạnh ngẫu nhiên
        for u in range(n):
            for v in range(u + 1, n):
                if random.random() < 0.35:
                    self.adj[u].add(v)
                    self.adj[v].add(u)

        #đảm bảo không đỉnh nào cô đơn (degree >= 1)
        for u in range(n):
            if len(self.adj[u]) == 0:
                v = random.randint(0, n - 1)
                if v == u:
                    v = (v + 1) % n
                self.adj[u].add(v)
                self.adj[v].add(u)

        self.colors = [0] * n
        self.compute_positions()
        self.draw_map()

        messagebox.showinfo("Thông báo", "Đã tạo bản đồ ngẫu nhiên với {} vùng.".format(n))


    def draw_map(self):
        self.canvas.delete("all")
        if self.n == 0:
            return

        palette = self.get_palette()

        # vẽ cạnh
        for u in range(self.n):
            x1, y1 = self.positions[u]
            for v in self.adj[u]:
                if v > u:
                    x2, y2 = self.positions[v]
                    self.canvas.create_line(x1, y1, x2, y2, fill="#aaaaaa")

        # vẽ vùng (đỉnh)
        r = self.node_radius
        for u in range(self.n):
            x, y = self.positions[u]
            cid = self.colors[u] if self.colors else 0

            if cid == 0:
                fill = "white"
            else:
                idx = (cid - 1) % len(palette)
                fill = palette[idx]

            self.canvas.create_oval(
                x - r, y - r,
                x + r, y + r,
                fill=fill, outline="black", width=2
            )
            label = self.node_names[u]
            self.canvas.create_text(x, y, text=label, font=("Arial", 14, "bold"))



    def auto_color(self):
        if self.n == 0:
            messagebox.showwarning("Chưa có bản đồ", "Hãy bấm 'Tạo bản đồ' trước.")
            return

        solver = GraphColoring(self.adj)
        self.colors = solver.color_graph()

        # kiểm tra lại ràng buộc
        for u in range(self.n):
            for v in self.adj[u]:
                if self.colors[u] == self.colors[v]:
                    messagebox.showerror("Lỗi",
                                         "Có lỗi tô màu: 2 đỉnh kề nhau trùng màu! ({}-{})".format(
                                             self.node_names[u], self.node_names[v]
                                         ))
                    return

        self.draw_map()

        num_colors = len(set(self.colors))
        messagebox.showinfo(
            "Kết quả",
            f"Đã tô màu tự động thành công.\n"
            f"Số màu thực sự dùng: {num_colors}\n"
            f"Mã màu từng vùng (theo thứ tự {self.node_names}): {self.colors}"
        )

    # ------------------ cập nhật bảng màu hiển thị ------------------

    def update_colors(self):
        """Chỉ đổi bảng màu hiển thị, giữ nguyên kết quả tô."""
        if self.n == 0:
            messagebox.showwarning("Chưa có bản đồ", "Hãy tạo bản đồ trước.")
            return

        self.draw_map()
        messagebox.showinfo("Thông báo", "Đã áp dụng bảng màu mới.")

    # ------------------ xử lý click vào đỉnh ------------------

    def on_canvas_click(self, event):
        """Khi click chuột trái vào canvas → nếu trúng 1 đỉnh thì cho sửa màu."""
        if self.n == 0:
            return

        #nếu chưa có mảng màu, khởi tạo
        if not self.colors or len(self.colors) != self.n:
            self.colors = [0] * self.n

        #đỉnh bị click
        clicked_vertex = None
        r = self.node_radius
        for u in range(self.n):
            x, y = self.positions[u]
            dx = event.x - x
            dy = event.y - y
            if dx * dx + dy * dy <= r * r:
                clicked_vertex = u
                break

        if clicked_vertex is None:
            return

        palette = self.get_palette()
        max_color_id = len(palette)

        #màu muốn chọn
        current_id = self.colors[clicked_vertex]
        prompt = f"Nhập số màu (1..{max_color_id}) cho vùng {self.node_names[clicked_vertex]}"
        if current_id != 0:
            prompt += f" (màu hiện tại: {current_id})"

        new_id = simpledialog.askinteger(
            "Đổi màu vùng",
            prompt,
            minvalue=1,
            maxvalue=max_color_id
        )

        if new_id is None:
            return

        # kiểm tra ràng buộc: không được trùng màu với bên cạnh
        for v in self.adj[clicked_vertex]:
            if self.colors[v] == new_id:
                messagebox.showerror(
                    "Lỗi ràng buộc",
                    f"Không thể tô màu {new_id} cho vùng {self.node_names[clicked_vertex]} "
                    f"vì kề với vùng {self.node_names[v]} đang dùng cùng màu."
                )
                return

        #gán màu mới
        self.colors[clicked_vertex] = new_id
        self.draw_map()



#MAIN


if __name__ == "__main__":
    root = tk.Tk()
    app = MapColoringApp(root)
    root.mainloop()
