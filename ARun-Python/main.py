import os
from win32gui import *
from win32api import *
from win32con import *


class MyWindow:
    def __init__(self):
        self.hinst = GetModuleHandle(None)
        self.hwnd_list_box = None
        self.hwnd_edit = None
        self.file_name = 'commands.txt'
        self.commands = {}

        InitCommonControls()
        wc = WNDCLASS()
        wc.lpszClassName = 'MyWndClass'
        wc.style = CS_HREDRAW | CS_VREDRAW
        wc.hbrBackground = COLOR_WINDOW + 1
        wc.lpfnWndProc = self.wnd_proc

        self.hwnd = CreateWindow(
            RegisterClass(wc),
            "Hello",
            WS_OVERLAPPEDWINDOW,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            200,
            300,
            0,
            0,
            self.hinst,
            None
        )

        SendMessage(self.hwnd, WM_CREATE, 0, 0)
        UpdateWindow(self.hwnd)
        ShowWindow(self.hwnd, SW_SHOWNORMAL)

    def wnd_proc(self, hwnd, message, wparam, lparam):
        if message == WM_DESTROY:
            PostQuitMessage(0)
        elif message == WM_CREATE:
            self.init_data()
            self.init_layout()
            DragAcceptFiles(hwnd, True)
        elif message == WM_SIZE:
            self.update_layout()
        elif message == WM_COMMAND:
            if lparam == self.hwnd_list_box:
                if HIWORD(wparam) == LBN_DBLCLK:
                    print "Clicked"
                    self.exec_selected_command()
            elif lparam == self.hwnd_edit:
                if HIWORD(wparam) == EN_CHANGE:
                    print "Change"
                    self.update_list_box()
        elif message == WM_CHAR:
            print 'char'
            if wparam == VK_RETURN:
                self.exec_selected_command()
            elif wparam == VK_ESCAPE:
                PostQuitMessage(0)
        elif message == WM_DROPFILES:
            print DragQueryFile(wparam, 0)
        return DefWindowProc(hwnd, message, wparam, lparam)

    def init_data(self):
        if not os.path.exists(self.file_name):
            open(self.file_name, 'w').write('calc\nnotepad\nwrite')
        for line in open(self.file_name):
            entry = line.strip().split(None, 1)
            if len(entry) == 2:
                self.commands[entry[1]] = entry[0]
            elif len(entry) == 1:
                self.commands[entry[0]] = entry[0]

        print self.commands

    def update_layout(self):
        rect = GetClientRect(self.hwnd)
        edit_height = 20
        MoveWindow(self.hwnd_edit, 0, 0, rect[2], edit_height, True)
        MoveWindow(self.hwnd_list_box, 0, edit_height, rect[2], rect[3] - edit_height, True)

    def center_window(self):
        rect = GetWindowRect(self.hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        desktop_rect = GetWindowRect(GetDesktopWindow())
        MoveWindow(self.hwnd, (desktop_rect[2] - width) / 2, (desktop_rect[3] - height) / 2, width, height, True)

    def init_layout(self):
        self.hwnd_edit = CreateWindow(
            'EDIT', None, WS_CHILD | WS_VISIBLE | WS_BORDER,
            0, 0, 0, 0,
            self.hwnd, 0, self.hinst, None
        )
        self.hwnd_list_box = CreateWindow(
            'LISTBOX', None, WS_CHILD | WS_VISIBLE | WS_VSCROLL | LBS_NOTIFY,
            0, 0, 0, 0,
            self.hwnd, 0, self.hinst, None)

        self.update_layout()
        self.center_window()
        self.update_list_box()

    def update_list_box(self):
        SetFocus(self.hwnd_edit)
        SendMessage(self.hwnd_list_box, LB_RESETCONTENT)

        commands = self.commands.items()
        commands.sort()
        count = 0
        for path, name in sorted(self.commands.items(), key=lambda item: item[1]):
            if self.match(GetWindowText(self.hwnd_edit), name):
                SendMessage(self.hwnd_list_box, LB_ADDSTRING, 0, name)
                SendMessage(self.hwnd_list_box, LB_SETITEMDATA, count, sorted(self.commands.keys()).index(path))
                count += 1
        SendMessage(self.hwnd_list_box, LB_SETCURSEL)

    def exec_selected_command(self):
        index = SendMessage(self.hwnd_list_box, LB_GETITEMDATA, SendMessage(self.hwnd_list_box, LB_GETCURSEL))
        command = sorted(self.commands.keys())[index]
        print command
        WinExec(command)

    @staticmethod
    def match(x, string):
        for char in x:
            if char in string:
                string = string[string.index(char) + 1:]
            else:
                return False
        return True


wnd = MyWindow()
while True:
    _, msg = GetMessage(None, 0, 0)
    if _:
        if msg[1] == WM_CHAR:
            print "WM_CHAR: ", msg
            msg = list(msg)
            if msg[2] in (VK_RETURN, VK_ESCAPE):
                msg[0] = wnd.hwnd
            else:
                msg[0] = wnd.hwnd_edit
            msg = tuple(msg)
        TranslateMessage(msg)
        DispatchMessage(msg)
    else:
        break
