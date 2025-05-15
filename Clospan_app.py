import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict

class CloSpan:
    def __init__(self, min_support):
        self.min_support = min_support
        self.closed_patterns = []

    def is_subsequence(self, sequence, pattern):
        """Kiểm tra xem pattern có phải là chuỗi con của sequence hay không."""
        idx = 0
        for item in pattern:
            found = False
            while idx < len(sequence):
                if item in sequence[idx]:
                    found = True
                    idx += 1
                    break
                idx += 1
            if not found:
                return False
        return True

    def calculate_support(self, sequences, pattern):
        """Tính support của một mẫu trong tập chuỗi."""
        count = 0
        for seq in sequences:
            if self.is_subsequence(seq, pattern):
                count += 1
        return count

    def get_extensions(self, sequences, pattern):
        """Tìm tất cả các phần tử có thể mở rộng cho pattern."""
        extensions = set()
        
        for seq in sequences:
            if not self.is_subsequence(seq, pattern):
                continue
            current_idx = 0
            pattern_idx = 0
            while pattern_idx < len(pattern) and current_idx < len(seq):
                found = False
                while current_idx < len(seq):
                    if pattern[pattern_idx] in seq[current_idx]:
                        found = True
                        current_idx += 1
                        break
                    current_idx += 1
                
                if found:
                    pattern_idx += 1
                else:
                    break
            for i in range(current_idx, len(seq)):
                for item in seq[i]:
                    if item not in pattern:
                      
                        extended_pattern = pattern + [item]
                        extensions.add(tuple(extended_pattern))
            for i in range(len(seq)):
                for item in seq[i]:
                    if item not in pattern:
                        extended_pattern = pattern + [item]
                        extensions.add(tuple(extended_pattern))
        
        return [list(ext) for ext in extensions]

    def is_closed(self, sequences, pattern, pattern_support):
        """
        Kiểm tra xem một mẫu có phải là mẫu đóng hay không.
        Một mẫu được gọi là đóng nếu không tồn tại mẫu mở rộng nào có cùng support.
        """
       
        all_items = set()
        for seq in sequences:
            if self.is_subsequence(seq, pattern):
                for itemset in seq:
                    for item in itemset:
                        if item not in pattern:
                            all_items.add(item)
        for item in all_items:
            new_pattern = pattern + [item]
            new_support = self.calculate_support(sequences, new_pattern)
            
           
            if new_support == pattern_support:
                return False
        
        return True

    def recursive_clospan(self, pattern, sequences):
        """Đệ quy tìm tất cả các mẫu đóng."""
        support = self.calculate_support(sequences, pattern)
        
        if support < self.min_support:
            return
            
       
        if self.is_closed(sequences, pattern, support):
            pattern_tuple = tuple(pattern)
            pattern_exists = False
            for existing_pattern, _ in self.closed_patterns:
                if tuple(existing_pattern) == pattern_tuple:
                    pattern_exists = True
                    break
                    
            if not pattern_exists:
                self.closed_patterns.append((pattern.copy(), support))
        
      
        all_items = set()
        for seq in sequences:
            if self.is_subsequence(seq, pattern):
                for itemset in seq:
                    for item in itemset:
                        if item not in pattern:
                            all_items.add(item)
        
     
        for item in all_items:
            new_pattern = pattern + [item]
            new_support = self.calculate_support(sequences, new_pattern)
            if new_support >= self.min_support:
                self.recursive_clospan(new_pattern, sequences)

    def clospan(self, sequences):
        """Thuật toán CloSpan chính."""
       
        item_counts = defaultdict(int)
        for seq in sequences:
            seen_items = set()  
            for itemset in seq:
                for item in itemset:
                    if item not in seen_items:
                        item_counts[item] += 1
                        seen_items.add(item)
        
       
        for item, count in item_counts.items():
            if count >= self.min_support:
                self.recursive_clospan([item], sequences)
                
        
        unique_patterns = []
        seen = set()
        for pattern, support in self.closed_patterns:
            pattern_tuple = tuple(pattern)
            if pattern_tuple not in seen:
                seen.add(pattern_tuple)
                unique_patterns.append((pattern, support))
        
        self.closed_patterns = unique_patterns

class CloSpanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CloSpan - Khai Thác Mẫu Tuần Tự Đóng")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.sequences = []
        self.min_support = tk.IntVar(value=2)

        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Nhập Dữ Liệu", padding=10)
        input_frame.pack(padx=10, pady=10, fill="both")

        ttk.Label(input_frame, text="Nhập chuỗi (mỗi chuỗi trên 1 dòng, các mục cách nhau bởi dấu phẩy):").pack(anchor="w")
        self.input_text = tk.Text(input_frame, height=5, width=70)
        self.input_text.pack(pady=5)
        ttk.Label(input_frame, text="Ví dụ: a,b,c\n sữa, bánh_mỳ, trà").pack(anchor="w")

        ttk.Button(input_frame, text="Tải từ File", command=self.load_from_file).pack(pady=5)

        ttk.Label(input_frame, text="Ngưỡng hỗ trợ tối thiểu (min support):").pack(anchor="w")
        ttk.Entry(input_frame, textvariable=self.min_support, width=10).pack(anchor="w")

        ttk.Button(input_frame, text="Tìm Mẫu Đóng", command=self.run_clospan).pack(pady=10)

        result_frame = ttk.LabelFrame(self.root, text="Kết Quả", padding=10)
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.result_tree = ttk.Treeview(result_frame, columns=("Pattern", "Support"), show="headings")
        self.result_tree.heading("Pattern", text="Mẫu Tuần Tự Đóng")
        self.result_tree.heading("Support", text="Hỗ Trợ")
        self.result_tree.pack(fill="both", expand=True)

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.input_text.delete(1.0, tk.END)
                    self.input_text.insert(tk.END, file.read())
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")

    def parse_input(self, input_text):
        """Chuyển đổi input text thành định dạng chuỗi cho thuật toán."""
        sequences = []
        lines = input_text.strip().split('\n')
        for line in lines:
            if line.strip():
                sequence = []
                items = [item.strip() for item in line.split(',') if item.strip()]
                for item in items:
                    sequence.append([item])  
                if sequence:
                    sequences.append(sequence)
        return sequences

    def run_clospan(self):
        try:
            input_text = self.input_text.get(1.0, tk.END).strip()
            if not input_text:
                messagebox.showwarning("Cảnh Báo", "Vui lòng nhập dữ liệu hoặc tải từ file!")
                return

            sequences = self.parse_input(input_text)
            if not sequences:
                messagebox.showwarning("Cảnh Báo", "Dữ liệu không hợp lệ! Vui lòng kiểm tra định dạng.")
                return

            min_sup = self.min_support.get()
            if min_sup <= 0:
                messagebox.showwarning("Cảnh Báo", "Ngưỡng hỗ trợ phải lớn hơn 0!")
                return

            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

          
            clospan = CloSpan(min_sup)
            clospan.clospan(sequences)

           
            if not clospan.closed_patterns:
                messagebox.showinfo("Kết Quả", f"Không tìm thấy mẫu đóng nào với ngưỡng hỗ trợ {min_sup}!")
            else:
             
                sorted_patterns = sorted(clospan.closed_patterns, key=lambda x: (len(x[0]), -x[1]))
                for pattern, support in sorted_patterns:
                    self.result_tree.insert("", "end", values=(', '.join(pattern), support))
                messagebox.showinfo("Kết Quả", f"Đã tìm thấy {len(clospan.closed_patterns)} mẫu đóng!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    root = tk.Tk()
    app = CloSpanApp(root)
    root.mainloop()