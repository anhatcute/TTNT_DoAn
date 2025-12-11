import tkinter as tk
from tkinter import messagebox

#HẰNG SỐ QUY ƯỚC
EMPTY = 0
HUMAN = 1   #X
AI = -1     #O
INF = 10**9

#CLASS BÀN CỜ
class Board:
    def __init__(self, size: int, win_length: int):
        """
        size: kích thước bàn cờ (3, 5, 10)
        win_length: số quân liên tiếp để thắng (3 hoặc 5)
        """
        self.size = size
        self.win_length = win_length
        self.grid = [[EMPTY for _ in range(size)] for _ in range(size)]

    def reset(self):
        #Xóa bàn cờ, tạo lại ô trống
        self.grid = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]

    def in_bounds(self, row: int, col: int) -> bool:
        #Kiểm tra ô (row, col) có nằm trong bàn cờ không
        return 0 <= row < self.size and 0 <= col < self.size

    def place_move(self, row: int, col: int, player: int):
        #Đặt quân lên bàn cờ nếu ô trống
        if self.grid[row][col] == EMPTY:
            self.grid[row][col] = player

    def remove_move(self, row: int, col: int):
        #Hoàn tác nước đi (dùng trong Minimax)
        self.grid[row][col] = EMPTY

    def check_winner(self):
        #Kiểm tra xem có ai thắng chưa.
        #Trả về:HUMAN (1) nếu người thắng, AI (-1) nếu AI thắng, None nếu chưa có ai thắng
        directions = [
            (1, 0),   #dọc
            (0, 1),   #ngang
            (1, 1),   #chéo xuống phải
            (1, -1),  #chéo xuống trái
        ]

        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == EMPTY:
                    continue
                player = self.grid[row][col]
                for d_row, d_col in directions:
                    count = 1
                    r = row + d_row
                    c = col + d_col
                    while self.in_bounds(r, c) and self.grid[r][c] == player:
                        count += 1
                        r += d_row
                        c += d_col
                        if count == self.win_length:
                            return player
        return None

    def is_full(self) -> bool:
        #Kiểm tra bàn cờ đã đầy chưa
        return all(cell != EMPTY for row in self.grid for cell in row)

    def game_over(self) -> bool:
        #Trả về True nếu game kết thúc
        if self.check_winner() is not None:
            return True
        if self.is_full():
            return True
        return False

    def generate_moves(self):
        #Liệt kê tất cả các ô trống có thể đánh
        moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == EMPTY:
                    moves.append((row, col))
        return moves

    def get_size(self) -> int:
        return self.size

    def get_win_length(self) -> int:
        return self.win_length


#CLASS AI - MINIMAX
class AIPlayer:
    def __init__(self, board: Board, ai_player: int = AI, human_player: int = HUMAN):
        self.board = board
        self.ai_player = ai_player
        self.human_player = human_player

    def evaluate(self) -> int:
        """
        Hàm heuristic đơn giản:
        - AI thắng  -> +100000
        - HUMAN thắng -> -100000
        - Chưa ai thắng -> (số quân AI - số quân HUMAN)
        """
        winner = self.board.check_winner()
        if winner == self.ai_player:
            return 100000
        elif winner == self.human_player:
            return -100000

        ai_count = 0
        human_count = 0
        for row in self.board.grid:
            for cell in row:
                if cell == self.ai_player:
                    ai_count += 1
                elif cell == self.human_player:
                    human_count += 1

        return ai_count - human_count

    def minimax(self, depth: int, alpha: int, beta: int, is_max_player_turn: bool) -> int:
        """
        Thuật toán Minimax có cắt tỉa Alpha-Beta.
        depth: độ sâu còn lại
        alpha, beta: biên alpha-beta
        is_max_player_turn: True nếu đến lượt AI (MAX), False nếu lượt người (MIN)
        """
        if depth == 0 or self.board.game_over():
            return self.evaluate()

        if is_max_player_turn:
            best_value = -INF
            for (row, col) in self.board.generate_moves():
                self.board.place_move(row, col, self.ai_player)
                value = self.minimax(depth - 1, alpha, beta, False)
                self.board.remove_move(row, col)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break  #Cắt tỉa
            return best_value
        else:
            best_value = INF
            for (row, col) in self.board.generate_moves():
                self.board.place_move(row, col, self.human_player)
                value = self.minimax(depth - 1, alpha, beta, True)
                self.board.remove_move(row, col)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break  #Cắt tỉa
            return best_value

    def find_best_move(self):
        #Tìm nước đi tốt nhất cho AI dựa trên Minimax + Alpha-Beta
        size = self.board.get_size()

        #Chọn depth limit tùy kích thước bàn
        if size == 3:
            depth_limit = 9    
        elif size == 5:
            depth_limit = 3
        else:
            depth_limit = 2    # 10x10 để tránh lag

        best_value = -INF
        best_move = None

        for (row, col) in self.board.generate_moves():
            self.board.place_move(row, col, self.ai_player)
            value = self.minimax(depth_limit, -INF, INF, False)
            self.board.remove_move(row, col)

            if value > best_value:
                best_value = value
                best_move = (row, col)

        return best_move


#  CLASS GIAO DIỆN
class CaroGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Caro AI - Minimax + Alpha-Beta")
      
        #Chọn kích thước bàn cờ
        self.size_var = tk.StringVar(value="3x3")
        size_frame = tk.Frame(root)
        size_frame.pack(pady=5)

        tk.Label(size_frame, text="Board size:").pack(side=tk.LEFT, padx=5)
        tk.OptionMenu(size_frame, self.size_var, "3x3", "5x5", "10x10").pack(side=tk.LEFT)

        tk.Button(size_frame, text="New Game", command=self.new_game).pack(side=tk.LEFT, padx=10)

        #Label trạng thái
        self.status_label = tk.Label(root, text="Chọn New Game để bắt đầu", fg="blue")
        self.status_label.pack(pady=5)

        #Frame chứa bàn cờ
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        #Thuộc tính game
        self.board: Board | None = None
        self.ai_player: AIPlayer | None = None
        self.buttons = []
        self.human_turn = True

        #Khởi tạo game lần đầu
        self.new_game()

    def _create_board_and_ai(self):
        #Tạo lại Board 
        choice = self.size_var.get()
        if choice == "3x3":
            size = 3
            win_length = 3
        elif choice == "5x5":
            size = 5
            win_length = 5
        else:
            size = 10
            win_length = 5

        self.board = Board(size, win_length)
        self.ai_player = AIPlayer(self.board)

    def _get_button_style_for_size(self, size: int):
        
        #Tự scale kích thước nút + font theo size bàn cờ.
        if size == 3:
            return 3, 1, 20  
        elif size == 5:
            return 2, 1, 16 
        else:  
            return 2, 1, 12 

    def new_game(self):
        """Reset game: tạo lại Board, AI và lưới button."""
        #Xóa các nút cũ
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        #Tạo lại 
        self._create_board_and_ai()
        size = self.board.get_size()

        self.buttons = []
        self.human_turn = True
        self.status_label.config(text="Lượt bạn (X)")

        btn_width, btn_height, font_size = self._get_button_style_for_size(size)

        #Tạo lưới button mới
        for row in range(size):
            row_buttons = []
            for col in range(size):
                btn = tk.Button(
                    self.board_frame,
                    text=" ",
                    width=btn_width,
                    height=btn_height,
                    font=("Arial", font_size),
                    command=lambda r=row, c=col: self.handle_click(r, c)
                )
                btn.grid(row=row, column=col, padx=1, pady=1)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def handle_click(self, row: int, col: int):
        #Xử lý khi người chơi click vào ô 
        if not self.human_turn:
            return

        if self.board.grid[row][col] != EMPTY:
            return

        #X
        self.board.place_move(row, col, HUMAN)
        self.buttons[row][col].config(text="X", state="disabled")

        if self.board.game_over():
            self.show_result()
            return

        self.human_turn = False
        self.status_label.config(text="Lượt AI (O)...")
        # Cho AI đánh sau 100ms để UI kịp cập nhật
        self.root.after(100, self.ai_move)

    def ai_move(self):
        #Lượt AI: tìm nước đi tốt nhất và đánh
        best_move = self.ai_player.find_best_move()
        if best_move is None:
            # Không còn nước đi
            self.show_result()
            return

        row, col = best_move
        self.board.place_move(row, col, AI)
        self.buttons[row][col].config(text="O", state="disabled")

        if self.board.game_over():
            self.show_result()
            return

        self.human_turn = True
        self.status_label.config(text="Lượt bạn (X)")

    def show_result(self):
        #Hiển thị kết quả 
        winner = self.board.check_winner()
        if winner == HUMAN:
            msg = "Bạn thắng!"
        elif winner == AI:
            msg = "AI thắng!"
        else:
            msg = "Hòa!"

        self.status_label.config(text=msg)

        # Khóa hết các ô lại
        for row_buttons in self.buttons:
            for btn in row_buttons:
                btn.config(state="disabled")

        messagebox.showinfo("Kết quả", msg)

#  HÀM MAIN
if __name__ == "__main__":
    root = tk.Tk()
    app = CaroGUI(root)
    root.mainloop()
