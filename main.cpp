#include "myuilib.h"
#include <string>
#include <list>
#include <iostream>
#include <sstream>

using namespace std;

#define IDC_LISTBOX 10000

struct CMainWnd : CWnd {

    HWND m_hwndListBox;
    list <string> commands;

    LRESULT WndProc(UINT Msg, WPARAM wParam, LPARAM lParam) {
        switch (Msg) {
            case WM_CREATE:
                OnCreate(Msg, wParam, lParam);
                break;
            case WM_COMMAND:
                if (LOWORD(wParam) == IDC_LISTBOX && HIWORD(wParam) == LBN_DBLCLK) {
                    OnExec();
                }
                break;
            default:
                break;
        }
        return CWnd::WndProc(Msg, wParam, lParam);
    }

    void OnCreate(UINT Msg, WPARAM wParam, LPARAM lParam) {
        RECT rect;
        GetWindowRect(m_hwnd, &rect);
        MoveWindow(m_hwnd, rect.left, rect.top, 300, 500, TRUE);

        GetClientRect(m_hwnd, &rect);
        m_hwndListBox = CreateWindow(
                "LISTBOX", NULL, WS_CHILD | WS_VISIBLE | WS_BORDER | WS_VSCROLL | LBS_STANDARD,
                rect.left, rect.top, rect.right, rect.bottom,
                m_hwnd, (HMENU) IDC_LISTBOX, GetApp().m_hInstance, NULL);

        commands.push_back("notepad");
        commands.push_back("apple");
        commands.push_back("banana");
        for (int j = 0; j < 33; ++j) {
            stringstream ss;
            ss << "calc" << j;
            commands.push_back(ss.str());
        }
        for (list<string>::iterator i = commands.begin(); i != commands.end(); ++i) {
            SendMessage(m_hwndListBox, LB_ADDSTRING, 0, (LPARAM) (*i).c_str());
        }
    }

    void OnExec() {
        char s[100];
        SendMessage(m_hwndListBox, LB_GETTEXT, (WPARAM) SendMessage(m_hwndListBox, LB_GETCURSEL, 0, 0), (LPARAM) s);
        cout << s << endl;
        WinExec(s, SW_SHOWDEFAULT);
    }

    BOOL PreTranslateMessage(MSG &msg) {
        switch (msg.message) {
            case WM_CHAR:
                return FALSE;

            default:
                break;
        }
        return CWnd::PreTranslateMessage(msg);
    }
};

int WINAPI WinMain( HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nShowCmd ) {
    static CApp app;
    CMainWnd wnd;
    wnd.Create();
    return app.Run();
}