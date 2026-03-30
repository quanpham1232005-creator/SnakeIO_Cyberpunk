import random
from assets import CONFIG

class Snake:
    def __init__(self):
        self.grid_size = CONFIG["grid_size"]
        # Khởi tạo rắn với 3 đốt, nằm giữa phần màn hình hiển thị game
        start_x = (CONFIG["play_area_width"] // 2) // self.grid_size * self.grid_size
        start_y = (CONFIG["play_area_height"] // 2) // self.grid_size * self.grid_size
        # Chọn hướng ngẫu nhiên khi xuất phát (Lên, Xuống, Trái, Phải)
        directions = [
            (self.grid_size, 0),   # Phải
            (-self.grid_size, 0),  # Trái
            (0, self.grid_size),   # Xuống
            (0, -self.grid_size)   # Lên
        ]
        self.direction = random.choice(directions)
        dx, dy = self.direction
        
        # Khởi tạo thân rắn (3 đốt) lùi dần theo hướng ngược lại với hướng di chuyển
        self.body = [
            (start_x, start_y), 
            (start_x - dx, start_y - dy), 
            (start_x - 2 * dx, start_y - 2 * dy)
        ]
        self.grow = False
        
    def get_head_pos(self):
        return self.body[0]

    def update(self, is_endless=False):
        self.prev_body = list(self.body) # Lưu lại vị trí cũ trước khi di chuyển
        cur_head = self.get_head_pos()
        dx, dy = self.direction
        
        if is_endless:
            # Xuyên tường (Wrap around)
            new_x = (cur_head[0] + dx) % CONFIG["play_area_width"]
            new_y = (cur_head[1] + dy) % CONFIG["play_area_height"]
        else:
            new_x = cur_head[0] + dx
            new_y = cur_head[1] + dy
            
        new_head = (new_x, new_y)
        
        # Thêm đầu mới
        self.body.insert(0, new_head)
        
        # Xóa đuôi nếu không lớn lên
        if self.grow:
            self.grow = False
        else:
            self.body.pop()

    def change_direction(self, dir_x, dir_y):
        # Tránh tự quay đầu 180 độ
        if (dir_x * -1, dir_y * -1) != self.direction:
            self.direction = (dir_x, dir_y)

    def check_collision(self, is_endless=False):
        head = self.get_head_pos()
        
        # Chạm tường (Chỉ check nếu KHÔNG phải chế độ Vô tận)
        if not is_endless:
            if head[0] < 0 or head[0] >= CONFIG["play_area_width"] or head[1] < 0 or head[1] >= CONFIG["play_area_height"]:
                return True
            
        # Chạm thân
        if head in self.body[1:]:
            return True
            
        return False

class Food:
    def __init__(self):
        self.position = (0, 0)

    def randomize_position(self, snake_body, other_food_pos=None):
        grid_size = CONFIG["grid_size"]
        max_x = (CONFIG["play_area_width"] // grid_size) - 1
        max_y = (CONFIG["play_area_height"] // grid_size) - 1
        
        while True:
            new_pos = (random.randint(1, max_x - 1) * grid_size, random.randint(1, max_y - 1) * grid_size)
            if new_pos not in snake_body and new_pos != other_food_pos:
                self.position = new_pos
                break

class BonusFood(Food):
    def __init__(self):
        super().__init__()
        self.active = False
        self.timer = 0 # Thời gian tồn tại (giây)
        
    def spawn(self, snake_body, normal_food_pos):
        self.randomize_position(snake_body, normal_food_pos)
        self.active = True
        self.timer = 5.0 # Mặc định 5 giây
