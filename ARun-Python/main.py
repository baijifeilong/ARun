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
    def __init__(self):
        self.hinst = GetModuleHandle(None)
        self.hwnd_list_box = None
        self.hwnd_command = None
        self.hwnd_add = None
        self.hwnd_delete = None
        self.hwnd_edit = None
        self.file_name = 'commands.txt'
        self.commands = []

        InitCommonControls()
        wc = WNDCLASS()
        wc.lpszClassName = 'MyWndClass'
        wc.style = CS_HREDRAW | CS_VREDRAW
        wc.hbrBackground = COLOR_WINDOW + 1
        wc.lpfnWndProc = self.wnd_proc

        self.hwnd = CreateWindow(
            RegisterClass(wc), "Hello", WS_OVERLAPPEDWINDOW,
            CW_USEDEFAULT, CW_USEDEFAULT, 200, 300,
            0, 0, self.hinst, None
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
            SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
            RegisterHotKey(hwnd, 22222, MOD_ALT, 0x52)
        elif message == WM_SIZE:
            self.update_layout()
        elif message == WM_COMMAND:
            if lparam == self.hwnd_list_box:
                if HIWORD(wparam) == LBN_DBLCLK:
                    print "Clicked"
                    self.exec_selected_command()
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
        elif message == WM_HOTKEY:
            print 'hotkey'
            self.toggle()
        elif message == WM_CHAR:
            print 'char'
            if wparam == VK_RETURN:
                self.exec_selected_command()
            elif wparam == VK_ESCAPE:
                self.toggle()

        return DefWindowProc(hwnd, message, wparam, lparam)

    def init_data(self):
        if not os.path.exists(self.file_name):
            open(self.file_name, 'w').write('calc\nnotepad\nwrite')
        for line in open(self.file_name):
            arr = line.strip().split(None, 1)
            if len(arr) == 1:
                self.commands.append(Command(arr[0], arr[0]))
            elif len(arr) == 2:
                self.commands.append(Command(arr[0], arr[1]))

        print self.commands

    def update_layout(self):
        rect = GetClientRect(self.hwnd)
        edit_height = 20
        button_size = 20
        MoveWindow(self.hwnd_command, 0, 0, rect[2] - button_size * 3, edit_height, True)
        MoveWindow(self.hwnd_list_box, 0, edit_height, rect[2], rect[3] - edit_height, True)
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

        self.commands.sort(key=lambda command: command.name.lower())
        for idx, command in enumerate(self.commands):
            if self.match(GetWindowText(self.hwnd_command), command.name):
                SendMessage(self.hwnd_list_box, LB_ADDSTRING, 0, command.name)
                count = SendMessage(self.hwnd_list_box, LB_GETCOUNT)
                SendMessage(self.hwnd_list_box, LB_SETITEMDATA, count - 1, idx)
        SendMessage(self.hwnd_list_box, LB_SETCURSEL)

    def exec_selected_command(self):
        index = SendMessage(self.hwnd_list_box, LB_GETITEMDATA, SendMessage(self.hwnd_list_box, LB_GETCURSEL))
        command = self.commands[index].path
        print command
        try:
            WinExec(command)
            self.toggle()
        except pywintypes.error, e:
            print 'exception'
            MessageBox(self.hwnd, e.strerror.decode('gbk'))

    @staticmethod
    def match(x, string):
        x = x.lower()
        string = string.lower()
        for char in x:
            if char in string:
                string = string[string.index(char) + 1:]
            else:
                return False
        return True

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
while True:
    _, msg = GetMessage(None, 0, 0)
    if _:
        if msg[1] == WM_CHAR:
            print "WM_CHAR: ", msg
            msg = list(msg)
            if msg[2] in (VK_RETURN, VK_ESCAPE):
                msg[0] = wnd.hwnd
            else:
                msg[0] = wnd.hwnd_command
            msg = tuple(msg)
        TranslateMessage(msg)
        DispatchMessage(msg)
    else:
        break
