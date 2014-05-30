import gspread

class STELLA_GSHEET:
    def __init__(self, username, passwd, key, wstitle=None, wsindex=None):
        self.gc = gspread.login(username, passwd)
        self.sheet = self.gc.open_by_key(key)
        if wstitle != None:
            self.wks = self.sheet.worksheet(wstitle)
        elif wsindex != None:
            self.wks = self.sheet.get_worksheet(index)
        else:
            self.wks = None

    def col_values(self, col_index=0, _wks=None):
        _wks = self.wks if _wks == None else _wks
        return _wks.col_values(col_index)

    def row_values(self, row_index=0, _wks=None):
        _wks = self.wks if _wks == None else _wks
        return _wks.row_values(row_index)

    def set_selfws_by_title(self, title, _sheet=None):
        _sheet = self.sheet if _sheet == None else _sheet
        self.wks = self.sheet.worksheet(title)

    def set_selfws_by_index(self, index, _sheet=None):
        _sheet = self.sheet if _sheet == None else _sheet
        self.wks = self.sheet.get_worksheet(index)

    def get_sheet_by_title(self, title, _sheet=None):
        _sheet = self.sheet if _sheet == None else _sheet
        return _sheet.worksheet(title)

    def get_sheet_by_index(self, index, _sheet=None):
        _sheet = self.sheet if _sheet == None else _sheet
        return _sheet.get_worksheet(index)

    def create_new_wks(self, title="", rows="20", cols="5", set_as_self_wks=False, _sheet=None):
        _sheet = self.sheet if _sheet == None else _sheet
        new_sheet = _sheet.add_worksheet(title=title, rows=rows, cols=cols)
        if set_as_self_wks:
            self.wks = new_sheet
        return new_sheet

    def set_self_wks(self, updated_wks):
        self.wks = updated_wks

    def update(self, cell_index, content, _wks=None):
        _wks = self.wks if _wks == None else _wks
        _wks.update_acell(cell_index, content)

    def update_rows(self, row_list, _wks=None, init_row=0):
        _wks = self.wks if _wks == None else _wks
        for row_idx in range(len(row_list)):
            for col_idx in range(len(row_list[row_idx])):
                index = self.get_cell_index(init_row + row_idx + 1, col_idx + 1)
                self.update(index, row_list[row_idx][col_idx], _wks=_wks)

    def get_cell_index(self, row_idx, col_idx):
        return ''.join([chr(col_idx+64), str(row_idx)])

    def add_row(self, row, _wks=None):
        _wks = self.wks if _wks == None else _wks
        _wks.append_row(row)

    def add_rows(self, row_list, _wks=None):
        _wks = self.wks if _wks == None else _wks
        for row in row_list:
            self.add_row(row, _wks=_wks)

    def find_col_index(self, keyword="", _wks=None):
        _wks = self.wks if _wks == None else _wks
        first_row = self.row_values(row_index=1, _wks=_wks)
        for i in range(len(first_row)):
            if first_row[i] == keyword:
                return i+1

    def find_row_index(self, keyword="", _wks=None):
        _wks = self.wks if _wks == None else _wks
        first_col = self.col_values(col_index=1, _wks=_wks)
        print first_col
        for i in range(len(first_col)):
            if first_col[i] == keyword:
                return i+1

    def copy_sheet(self, new_wks_name, orig_wks_name=None, sheet_key=None):
        sheet_to_copy = self.sheet if sheet_key == None else self.gc.open_by_key(sheet_key)
        orig_wks = self.wks if orig_wks_name == None else self.get_sheet_by_title(orig_wks_name, _sheet=sheet_to_copy)
        list_of_lists = orig_wks.get_all_values()
        num_rows = len(list_of_lists)
        num_cols = len(list_of_lists[0])
        cell_list = orig_wks.range(''.join(['A1:', self.get_cell_index(num_rows, num_cols)]))
        new_wks = self.create_new_wks(title=new_wks_name, rows=str(num_rows), cols=str(num_cols), _sheet=sheet_to_copy)
        self.update_rows(list_of_lists, _wks=new_wks)
        return new_wks


