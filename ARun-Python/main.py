# coding=utf-8

import os
import pywintypes
from win32gui import *
from win32api import *
from win32con import *


class Command:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __str__(self):
        return self.name + ':' + self.path


class MyWindow:
    WMU_TRAY = WM_USER + 20

    def __init__(self):
        self.app_name = 'ARun'
        self.hinst = GetModuleHandle(None)
        self.hwnd_list_box = None
        self.hwnd_command = None
        self.hwnd_desc = None
        self.hwnd_add = None
        self.hwnd_delete = None
        self.hwnd_edit = None
        self.hmenu = None
        self.file_name = os.path.dirname(os.path.realpath(__file__)) + '/' + 'commands.txt'
        self.commands = []

        InitCommonControls()
        wc = WNDCLASS()
        wc.lpszClassName = self.app_name
        wc.style = CS_HREDRAW | CS_VREDRAW
        wc.hbrBackground = COLOR_WINDOW + 1
        wc.lpfnWndProc = self.wnd_proc

        self.hwnd = CreateWindow(
            RegisterClass(wc), self.app_name, WS_OVERLAPPEDWINDOW,
            CW_USEDEFAULT, CW_USEDEFAULT, 333, 555,
            0, 0, self.hinst, None
        )

        SendMessage(self.hwnd, WM_CREATE, 0, 0)
        ShowWindow(self.hwnd, SW_SHOWNORMAL)
        UpdateWindow(self.hwnd)

    def wnd_proc(self, hwnd, message, wparam, lparam):
        if message == WM_DESTROY:
            PostQuitMessage(0)
        elif message == WM_CREATE:
            self.on_create()
        elif message == WM_SIZE:
            self.update_layout()
        elif message == WM_COMMAND:
            print 'command'
            if lparam == self.hwnd_list_box:
                if HIWORD(wparam) == LBN_DBLCLK:
                    print "Clicked"
                    self.exec_selected_command()
                elif HIWORD(wparam) == LBN_SELCHANGE:
                    self.update_desc()
            elif lparam == self.hwnd_command:
                if HIWORD(wparam) == EN_CHANGE:
                    print "Change"
                    self.update_list_box()
            elif lparam == self.hwnd_add:
                self.do_add()
            elif lparam == self.hwnd_edit:
                self.do_edit()
            elif lparam == self.hwnd_delete:
                self.do_delete()
            elif lparam == 0:
                if wparam == 1:
                    self.toggle()
                elif wparam == 2:
                    PostQuitMessage(0)
                elif LOWORD(wparam) == 1001:
                    cur = SendMessage(self.hwnd_list_box, LB_GETCURSEL)
                    if cur > 0:
                        SendMessage(self.hwnd_list_box, LB_SETCURSEL, cur - 1)
                elif LOWORD(wparam) == 1002:
                    cur = SendMessage(self.hwnd_list_box, LB_GETCURSEL)
                    SendMessage(self.hwnd_list_box, LB_SETCURSEL, cur + 1)
                elif LOWORD(wparam) == 1003:
                    self.do_add()
                elif LOWORD(wparam) == 1004:
                    self.do_delete()
                elif LOWORD(wparam) == 1005:
                    self.do_edit()

        elif message == WM_HOTKEY:
            print 'hotkey'
            self.toggle()
        elif message == WM_CHAR:
            print 'char'
            if wparam == VK_RETURN:
                self.exec_selected_command()
            elif wparam == VK_ESCAPE:
                self.toggle()
        elif message == self.WMU_TRAY:
            if lparam == WM_LBUTTONUP:
                self.toggle()
            elif lparam == WM_RBUTTONDOWN:
                point = GetCursorPos()
                SetForegroundWindow(self.hwnd)
                if IsWindowVisible(self.hwnd):
                    txt = 'Hide'
                else:
                    txt = 'Show'
                ModifyMenu(self.hmenu, 1, MF_BYCOMMAND, 1, txt)
                TrackPopupMenu(self.hmenu, TPM_RIGHTBUTTON, point[0], point[1], 0, hwnd, None)
        elif message == WM_SYSCOMMAND:
            print 'syscommand'
            if wparam == SC_MINIMIZE:
                self.toggle()
                return 0
            elif wparam == SC_CLOSE:
                self.toggle()
                return 0
        return DefWindowProc(hwnd, message, wparam, lparam)

    def on_create(self):
        self.init_data()
        self.init_layout()
        SetWindowPos(self.hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        try:
            RegisterHotKey(self.hwnd, 22222, MOD_ALT, ord('R'))
        except pywintypes.error, e:
            MessageBox(self.hwnd, e.strerror)

        Shell_NotifyIcon(NIM_ADD, (
            self.hwnd, 0, NIF_ICON | NIF_MESSAGE | NIF_TIP, self.WMU_TRAY,
            LoadIcon(None, IDI_ERROR), 'You see see'
        ))

        self.hmenu = CreatePopupMenu()
        AppendMenu(self.hmenu, MF_STRING, 1, 'Show')
        AppendMenu(self.hmenu, MF_STRING, 2, 'Exit')

    def init_data(self):
        if not os.path.exists(self.file_name):
            MessageBox(None, "Not Exist")
            with open(self.file_name, 'w') as f:
                f.write('calc\nnotepad\nwrite')
        with open(self.file_name) as f:
            for line in f:
                arr = line.strip().split(None, 1)
                if len(arr) == 1:
                    self.commands.append(Command(arr[0], arr[0]))
                elif len(arr) == 2:
                    self.commands.append(Command(arr[0], arr[1]))

    def update_layout(self):
        rect = GetClientRect(self.hwnd)
        edit_height = 20
        desc_height = 20
        button_size = 20
        MoveWindow(self.hwnd_command, 0, 0, rect[2] - button_size * 3, edit_height, True)
        MoveWindow(self.hwnd_list_box, 0, edit_height, rect[2], rect[3] - edit_height - desc_height, True)
        MoveWindow(self.hwnd_desc, 0, rect[3] - desc_height, rect[2], desc_height, True)
        MoveWindow(self.hwnd_add, rect[2] - button_size * 3, 0, edit_height, edit_height, True)
        MoveWindow(self.hwnd_delete, rect[2] - button_size * 2, 0, edit_height, edit_height, True)
        MoveWindow(self.hwnd_edit, rect[2] - button_size * 1, 0, edit_height, edit_height, True)

    def center_window(self):
        rect = GetWindowRect(self.hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        desktop_rect = GetWindowRect(GetDesktopWindow())
        MoveWindow(self.hwnd, (desktop_rect[2] - width) / 2, (desktop_rect[3] - height) / 2, width, height, True)

    def init_layout(self):
        self.hwnd_command = CreateWindow(
            'EDIT', None, WS_CHILD | WS_VISIBLE | WS_BORDER,
            0, 0, 0, 0,
            self.hwnd, 0, self.hinst, None
        )
        self.hwnd_list_box = CreateWindow(
            'LISTBOX', None, WS_CHILD | WS_VISIBLE | WS_VSCROLL | LBS_NOTIFY,
            0, 0, 0, 0,
            self.hwnd, 0, self.hinst, None)
        self.hwnd_desc = CreateWindow(
            'STATIC', 'Ready.', WS_CHILD | WS_VISIBLE | WS_BORDER,
            0, 0, 0, 0,
            self.hwnd, 0, self.hinst, None)
        self.hwnd_add = CreateWindow(
            'BUTTON', '+', WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,
            self.hwnd, 0, self.hinst, None
        )
        self.hwnd_delete = CreateWindow(
            'BUTTON', '-', WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,
            self.hwnd, 0, self.hinst, None
        )
        self.hwnd_edit = CreateWindow(
            'BUTTON', 'E', WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,
            self.hwnd, 0, self.hinst, None
        )

        self.update_layout()
        self.center_window()
        self.update_list_box()

    def update_list_box(self):
        SetFocus(self.hwnd_command)
        SendMessage(self.hwnd_list_box, LB_RESETCONTENT)

        input_str = GetWindowText(self.hwnd_command)

        self.commands.sort(key=lambda x: x.name.lower())
        self.commands.sort(lambda x, y: self.match(input_str, y.name) - self.match(input_str, x.name))

        for idx, command in enumerate(self.commands):
            if self.match(GetWindowText(self.hwnd_command), command.name) > 0:
                # print command.name, ':', self.match(input_str, command.name)
                SendMessage(self.hwnd_list_box, LB_ADDSTRING, 0, command.name)
                count = SendMessage(self.hwnd_list_box, LB_GETCOUNT)
                SendMessage(self.hwnd_list_box, LB_SETITEMDATA, count - 1, idx)
        SendMessage(self.hwnd_list_box, LB_SETCURSEL)
        self.update_desc()

    def update_desc(self):
        if SendMessage(self.hwnd_list_box, LB_GETCOUNT) > 0:
            sel = SendMessage(self.hwnd_list_box, LB_GETCURSEL)
            index = SendMessage(self.hwnd_list_box, LB_GETITEMDATA, sel)
            SetWindowText(self.hwnd_desc, self.commands[index].path)
        else:
            SetWindowText(self.hwnd_desc, 'Ready.')

    def exec_selected_command(self):
        index = SendMessage(self.hwnd_list_box, LB_GETITEMDATA, SendMessage(self.hwnd_list_box, LB_GETCURSEL))
        command = self.commands[index].path
        print command
        try:
            # WinExec(command)
            arr = command.split(None, 1)
            exe = arr[0]
            param = None
            if len(arr) > 1:
                param = arr[1]
            ShellExecute(self.hwnd, 'open', exe, param, None, SW_SHOW)

            self.toggle()
        except pywintypes.error, e:
            print 'exception'
            MessageBox(self.hwnd, e.strerror.decode('gbk'))

    @staticmethod
    def match(src='', dst=''):
        if src.strip() == '':
            return 1
        elif dst.strip() == '':
            return 0
        src = src.lower()
        dst_old = dst
        dst = dst[0].upper() + dst[1:]
        ret = 0
        if src == dst.lower():
            ret += 10000  # Total match
        if src[0] == dst[0].lower():
            ret += 1000  # First letter match
        for i, char in enumerate(src):
            if char.upper() in dst:
                dst = dst[dst.index(char.upper()) + 1:]
                ret += 100  # A upper letter match
            elif char in dst:
                dst = dst[dst.index(char) + 1:]
                ret += 1  # A lower letter match
                if i > 0 and src[i - 1:i + 1] in dst_old.lower():
                    ret += 10  # A continuous match
            else:
                ret = 0  # Not match
                break
        return ret

    def do_add(self):
        dialog = MyDialog(self.hwnd)
        if dialog.do_modal() == IDOK:
            self.commands.append(dialog.command)
            self.save()
            self.update_list_box()

    def do_edit(self):
        curr = SendMessage(self.hwnd_list_box, LB_GETCURSEL)
        index = SendMessage(self.hwnd_list_box, LB_GETITEMDATA, curr)
        dialog = MyDialog(self.hwnd)
        dialog.command = self.commands[index]
        if dialog.do_modal(True) == IDOK:
            self.commands[index] = dialog.command
            self.save()
            self.update_list_box()

    def do_delete(self):
        if MessageBox(self.hwnd, 'Are you sure to delete it?', 'Warning', MB_OKCANCEL | MB_ICONEXCLAMATION) == IDOK:
            curr = SendMessage(self.hwnd_list_box, LB_GETCURSEL)
            index = SendMessage(self.hwnd_list_box, LB_GETITEMDATA, curr)
            self.commands.pop(index)
            self.save()
            self.update_list_box()

    def save(self):
        with open(self.file_name, 'w') as f:
            for command in self.commands:
                f.write(command.name + '\t' + command.path + '\n')

    def toggle(self):
        if IsWindowVisible(self.hwnd):
            SetWindowText(self.hwnd_command, "")
            ShowWindow(self.hwnd, SW_HIDE)
        else:
            ShowWindow(self.hwnd, SW_SHOW)
            SetForegroundWindow(self.hwnd)
            SetFocus(self.hwnd_command)


class MyDialog:
    def __init__(self, hwnd):
        self.hwnd_parent = hwnd
        self.command = None

    def do_modal(self, edit=False):
        dt = [('Add new command', (0, 0, 120, 60), WS_OVERLAPPEDWINDOW),
              ['STATIC', 'Name:', -1, (5, 5, 45, 9), WS_CHILD | WS_VISIBLE],
              ['EDIT', None, 1, (50, 5, 65, 9), WS_CHILD | WS_VISIBLE],
              ['STATIC', 'Path:', -1, (5, 25, 50, 9), WS_CHILD | WS_VISIBLE],
              ['EDIT', None, 2, (50, 25, 65, 9), WS_CHILD | WS_VISIBLE],
              ['BUTTON', 'OK', 0, (45, 44, 30, 10), WS_CHILD | WS_VISIBLE]]
        return DialogBoxIndirectParam(None, dt, self.hwnd_parent, self.dlg_proc, edit)

    def dlg_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_INITDIALOG:
            print 'init'
            DragAcceptFiles(hwnd, True)
            if lparam:
                SetDlgItemText(hwnd, 1, self.command.name)
                SetDlgItemText(hwnd, 2, self.command.path)
        elif msg == WM_CLOSE:
            EndDialog(hwnd, IDCANCEL)
        elif msg == WM_COMMAND:
            if HIWORD(wparam) == BN_CLICKED:
                name = GetDlgItemText(hwnd, 1)
                path = GetDlgItemText(hwnd, 2)
                if not (bool(name) and bool(path)):
                    MessageBox(hwnd, 'Please input name and path')
                elif self.command is not None and name == self.command.name and path == self.command.path:
                    EndDialog(hwnd, IDCANCEL)
                else:
                    self.command = Command(name, path)
                    EndDialog(hwnd, IDOK)

            print 'click'
        elif msg == WM_DROPFILES:
            path = DragQueryFile(wparam, 0)
            name = MyDialog.path_to_name(path)
            if os.path.isdir(path):
                path = 'explorer ' + path
            SetDlgItemText(hwnd, 1, name)
            SetDlgItemText(hwnd, 2, path)

    @staticmethod
    def path_to_name(s):

        if os.path.isdir(s):
            ret = s[s.rfind('\\') + 1:]
        else:
            ret = s[s.rfind('\\') + 1:s.rfind('.')]
        return ret


wnd = MyWindow()
haccel = CreateAcceleratorTable([
    (FSHIFT | FVIRTKEY, ord('M'), SC_MINIMIZE),
    (FCONTROL | FVIRTKEY, ord('P'), 1001),
    (FCONTROL | FVIRTKEY, ord('N'), 1002),
    (FCONTROL | FVIRTKEY, ord('A'), 1003),
    (FCONTROL | FVIRTKEY, ord('D'), 1004),
    (FCONTROL | FVIRTKEY, ord('E'), 1005),
    (FSHIFT | FVIRTKEY, ord('\t'), 1001),
    (FVIRTKEY, ord('\t'), 1002),
])
print haccel
while True:
    _, msg = GetMessage(None, 0, 0)
    if _:
        if not TranslateAccelerator(wnd.hwnd, haccel, msg):
            if msg[1] == WM_CHAR:
                print "WM_CHAR: ", msg
                msg = list(msg)
                if msg[2] in (VK_RETURN, VK_ESCAPE):
                    msg[0] = wnd.hwnd
                else:
                    msg[0] = wnd.hwnd_command
                msg = tuple(msg)
            elif msg[1] in (WM_KEYUP, WM_KEYDOWN):
                if msg[2] in (VK_DOWN, VK_UP):
                    print 'fds'
                    print msg
                    print wnd.hwnd_list_box
                    msg = list(msg)
                    msg[0] = wnd.hwnd_list_box
                    msg = tuple(msg)
            TranslateMessage(msg)
            DispatchMessage(msg)
    else:
        break
DestroyAcceleratorTable(haccel)
