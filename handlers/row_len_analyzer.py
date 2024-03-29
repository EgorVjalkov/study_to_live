class RowLenAnalyzer:
    def __init__(self, buttons: list):
        self.buttons = buttons
        self.rows = []
    # по 6 букв 4 кнопки

    def button_gen(self):
        for bnt in self.buttons:
            yield bnt

    @staticmethod
    def fit_in(row: list, btn: str) -> bool:
        new_row = row.copy()
        new_row.append(btn)
        if len(new_row) >=7 or len(''.join(new_row)) > 20:
            return False
        return True

    def create_row_container(self) -> list:
        row = []
        bnt_gen = self.button_gen()
        for btn in bnt_gen:
            if self.fit_in(row, btn):
                row.append(btn)
            else:
                self.rows.append(row.copy())
                row.clear()
                row.append(btn)
        self.rows.append(row)
        return self.rows


ke = [str(i) for i in list(range(0, 20))]
c = RowLenAnalyzer(ke).create_row_container()
print(c)


