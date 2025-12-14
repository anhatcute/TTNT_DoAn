import tkinter as tk
import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set


Pos = Tuple[int, int]  # Tọa độ ô trong lưới: (row, col)



# 1) HÀM CHUẨN HÓA MAP

def normalize_map(lines: List[str]) -> List[str]:
    """
    Chuẩn hóa bản đồ để tất cả dòng có cùng độ dài.
    - target = độ dài dòng dài nhất.
    - Nếu dòng có dạng '# ... #' thì giữ 2 biên '#', padding phần giữa bằng '.'
    - Ngược lại: pad bên phải bằng '.'.
    """
    if not lines:
        raise ValueError("Map rỗng.")

    target = max(len(line) for line in lines)
    normalized: List[str] = []

    for line in lines:
        if len(line) == target:
            normalized.append(line)
            continue

        if line.startswith("#") and line.endswith("#") and len(line) >= 2:
            middle = line[1:-1]
            # pad/truncate phần giữa sao cho tổng dài = target
            middle = (middle + "." * (target - 2))[: target - 2]
            normalized.append("#" + middle + "#")
        else:
            normalized.append(line.ljust(target, "."))

    return normalized


# 2) MAP MẪU "TRƯỜNG HỌC"

def preset_school_map() -> List[str]:
    """
    Map mini trường:
    - S: cổng trường
    - G: phòng học/Lab
    - #: tường/bồn cây/khu vực cấm
    - .: đường đi
    """
    raw = [
        "########################",
        "#S..#......#..........#",
        "#..##.####.#.#####.##.#",
        "#......#...#.....#....#",
        "###.##.#.#######.#.####",
        "#...#..#.....#...#....#",
        "#.###.#####.#.###..##.#",
        "#.....#...#.#...#..#G.#",
        "########################",
    ]
    return normalize_map(raw)


# 3) LỚP BẢN ĐỒ (GRID MAP)

class GridMap:
    """
    Bản đồ dạng lưới 2D:
    - '#' : vật cản (không đi được)
    - '.' : ô trống (đi được)
    - 'S' : Start
    - 'G' : Goal
    """

    def __init__(self, lines: List[str]):
        if not lines:
            raise ValueError("Map rỗng.")

        self.rows = len(lines)
        self.cols = len(lines[0])

        # Kiểm tra mọi dòng phải cùng độ dài
        if any(len(line) != self.cols for line in lines):
            raise ValueError("Map không hợp lệ: các dòng phải có cùng độ dài.")

        self.grid = [list(line) for line in lines]
        self.start = self._find_char("S")
        self.goal = self._find_char("G")

    def _find_char(self, ch: str) -> Pos:
        """Tìm tọa độ ký tự ch (S hoặc G) trong map."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == ch:
                    return (r, c)
        raise ValueError(f"Không tìm thấy '{ch}' trong map.")

    def in_bounds(self, p: Pos) -> bool:
        #Ô p có nằm trong map không
        r, c = p
        return 0 <= r < self.rows and 0 <= c < self.cols

    def passable(self, p: Pos) -> bool:
        #Ô p có đi qua được không 
        r, c = p
        return self.grid[r][c] != "#"

    def get_cell(self, p: Pos) -> str:
        #Lấy ký tự tại ô p
        r, c = p
        return self.grid[r][c]

    def set_cell(self, p: Pos, ch: str) -> None:
        #Gán ký tự ch cho ô p
        r, c = p
        self.grid[r][c] = ch

    def neighbors_4(self, p: Pos) -> List[Pos]:
        #Lấy hàng xóm 4 hướng (lên/xuống/trái/phải) hợp lệ và đi được
        r, c = p
        cand = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        out: List[Pos] = []
        for q in cand:
            if self.in_bounds(q) and self.passable(q):
                out.append(q)
        return out



# 4) THUẬT TOÁN A* (A-STAR)

@dataclass(frozen=True)
class AStarInfo:
    #Thông tin chạy A*: đường đi + tập đã duyệt để vẽ trực quan
    path: List[Pos]
    visited: Set[Pos]


class AStarPathfinder:
    """
    A* tìm đường ngắn nhất:
    - Mỗi bước đi cost = 1
    - Heuristic: Manhattan distance (phù hợp grid 4 hướng)
    """

    @staticmethod
    def manhattan(a: Pos, b: Pos) -> int:
        #h = |x1-x2| + |y1-y2|
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, grid_map: GridMap) -> AStarInfo:
        start = grid_map.start
        goal = grid_map.goal

        #open_heap: min-heap theo (f, g, pos)
        open_heap: List[Tuple[int, int, Pos]] = []
        heapq.heappush(open_heap, (self.manhattan(start, goal), 0, start))

        #came_from: để truy vết đường đi
        came_from: Dict[Pos, Optional[Pos]] = {start: None}

        #g_score: lưu chi phí tốt nhất từ Start đến mỗi ô
        g_score: Dict[Pos, int] = {start: 0}

        #visited: tập các ô đã được mở rộng (closed set)
        visited: Set[Pos] = set()

        while open_heap:
            f, g, cur = heapq.heappop(open_heap)

            if cur in visited:
                continue
            visited.add(cur)

            #tới goal -> reconstruct path
            if cur == goal:
                path = self._reconstruct(came_from, goal)
                return AStarInfo(path=path, visited=visited)

            #mở rộng hàng xóm
            for nxt in grid_map.neighbors_4(cur):
                tentative_g = g_score[cur] + 1

                #nếu tìm được đường rẻ hơn tới nxt thì update
                if nxt not in g_score or tentative_g < g_score[nxt]:
                    g_score[nxt] = tentative_g
                    h = self.manhattan(nxt, goal)
                    f_new = tentative_g + h
                    heapq.heappush(open_heap, (f_new, tentative_g, nxt))
                    came_from[nxt] = cur

        #không có đường
        return AStarInfo(path=[], visited=visited)

    def _reconstruct(self, came_from: Dict[Pos, Optional[Pos]], goal: Pos) -> List[Pos]:
        #Truy vết từ goal về start qua came_from
        path: List[Pos] = []
        cur: Optional[Pos] = goal
        while cur is not None:
            path.append(cur)
            cur = came_from.get(cur)
        path.reverse()
        return path



# 5) GUI

class SchoolPathfindingGUI:
    """
    Giao diện:
    - Click để đặt/bỏ tường
    - Đặt Start / Goal
    - Run A* để tìm đường
    - Tô màu trực quan visited/path
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Demo Tìm đường trong trường")

        #Load map
        self.map = GridMap(preset_school_map())

        # ----------- CONTROL PANEL -----------
        ctrl = tk.Frame(root)
        ctrl.pack(pady=5)

        self.mode = tk.StringVar(value="wall") 

        tk.Label(ctrl, text="Chế độ click:").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(ctrl, text="Vật cản", variable=self.mode, value="wall").pack(side=tk.LEFT)
        tk.Radiobutton(ctrl, text="Đặt Start", variable=self.mode, value="start").pack(side=tk.LEFT)
        tk.Radiobutton(ctrl, text="Đặt Goal", variable=self.mode, value="goal").pack(side=tk.LEFT)

        tk.Button(ctrl, text="Run A*", command=self.run_astar).pack(side=tk.LEFT, padx=10)
        tk.Button(ctrl, text="Reset map", command=self.reset_map).pack(side=tk.LEFT, padx=5)

        self.info_label = tk.Label(root, text="Click để chỉnh map. Bấm Run A* để tìm đường.", fg="blue")
        self.info_label.pack(pady=5)

        # ----------- CANVAS -----------
        # đổi số này để map to/nhỏ (giao diện)
        self.cell = 28

        w = self.map.cols * self.cell
        h = self.map.rows * self.cell
        self.canvas = tk.Canvas(root, width=w, height=h, bg="white")
        self.canvas.pack(pady=8)

        self.canvas.bind("<Button-1>", self.on_click)

        # Lưu dữ liệu để vẽ lại
        self.last_visited: Set[Pos] = set()
        self.last_path: List[Pos] = []

        self.draw_grid()

    def reset_map(self) -> None:
        """Reset map về bản mẫu ban đầu."""
        self.map = GridMap(preset_school_map())
        self.last_visited = set()
        self.last_path = []
        self.info_label.config(text="Đã reset map. Bấm Run A* để tìm đường.", fg="blue")

        # cập nhật kích thước canvas nếu cần
        w = self.map.cols * self.cell
        h = self.map.rows * self.cell
        self.canvas.config(width=w, height=h)

        self.draw_grid()

    def on_click(self, event) -> None:
        """Xử lý click: toggle wall hoặc đặt Start/Goal."""
        r = event.y // self.cell
        c = event.x // self.cell
        p = (r, c)

        if not self.map.in_bounds(p):
            return

        mode = self.mode.get()

        if mode == "wall":
            # không cho đặt tường lên S/G
            if p == self.map.start or p == self.map.goal:
                return
            cur_ch = self.map.get_cell(p)
            self.map.set_cell(p, "." if cur_ch == "#" else "#")

        elif mode == "start":
            # không đặt start vào tường
            if self.map.get_cell(p) == "#":
                return
            self.map.set_cell(self.map.start, ".")
            self.map.start = p
            self.map.set_cell(p, "S")

        elif mode == "goal":
            if self.map.get_cell(p) == "#":
                return
            self.map.set_cell(self.map.goal, ".")
            self.map.goal = p
            self.map.set_cell(p, "G")

        # khi chỉnh map, xóa kết quả cũ
        self.last_visited = set()
        self.last_path = []
        self.draw_grid()

    def run_astar(self) -> None:
        """Chạy A* và vẽ kết quả."""
        solver = AStarPathfinder()
        result = solver.find_path(self.map)

        self.last_visited = result.visited
        self.last_path = result.path

        if not result.path:
            self.info_label.config(
                text=f"Không tìm thấy đường đi! Ô đã duyệt: {len(result.visited)}",
                fg="red"
            )
            self.draw_grid()
            return

        steps = len(result.path) - 1
        self.info_label.config(
            text=f"Tìm thấy đường đi! Số bước: {steps} | Ô đã duyệt: {len(result.visited)}",
            fg="green"
        )
        print("PATH:", result.path)
        print("STEPS:", steps)
        print("VISITED:", len(result.visited))

        self.draw_grid()

    def draw_grid(self) -> None:
        """
        Quy ước màu hiển thị:
        - '#': đen
        - '.': trắng
        - visited: xanh nhạt
        - path: vàng
        - S: xanh lá
        - G: đỏ
        """
        self.canvas.delete("all")

        visited = self.last_visited
        path_set = set(self.last_path)

        for r in range(self.map.rows):
            for c in range(self.map.cols):
                p = (r, c)
                ch = self.map.grid[r][c]

                # màu mặc định
                fill = "white"

                # vật cản
                if ch == "#":
                    fill = "black"

                # visited (không tô lên tường)
                if p in visited and ch != "#":
                    fill = "#cfefff"

                # path (ưu tiên hơn visited)
                if p in path_set and ch != "#":
                    fill = "#ffe08a"

                # S/G ưu tiên cao nhất
                if p == self.map.start:
                    fill = "#8df58d"
                if p == self.map.goal:
                    fill = "#ff7f7f"

                x1 = c * self.cell
                y1 = r * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#dddddd")

                # vẽ chữ S/G
                if p == self.map.start:
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                            text="S", font=("Arial", 12, "bold"))
                elif p == self.map.goal:
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                            text="G", font=("Arial", 12, "bold"))



# 6) MAIN

def main():
    root = tk.Tk()
    app = SchoolPathfindingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
