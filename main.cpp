#include <windows.h>
#include <assert.h>
#include <iostream>
#include <list>

using namespace std;

class CMainWindow {
private:
    const char *m_szAppName = "ARun";
    static CMainWindow *s_pInstance;
    HINSTANCE m_hInstance;
    HWND m_hwnd;
    HWND m_hwndListBox;
    list <string> m_commands = {"notepad", "calc", "mspaint"};

public:
    CMainWindow() {
        s_pInstance = this;
        m_hInstance = GetModuleHandle(NULL);

        WNDCLASS wc;
        RtlZeroMemory(&wc, sizeof(wc));
        wc.hbrBackground = (HBRUSH) (COLOR_WINDOW + 1);
        wc.hCursor = LoadCursor(NULL, IDC_ARROW);
        wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
        wc.lpfnWndProc = (WNDPROC) WndProcStatic;
        wc.lpszClassName = "MyWindow";
        ATOM atom = RegisterClass(&wc);
        assert(atom);

        HWND hwnd = CreateWindow(
                (LPCSTR) (int) atom, m_szAppName, WS_OVERLAPPEDWINDOW | WS_VISIBLE,
                CW_USEDEFAULT, CW_USEDEFAULT, 300, 444,
                NULL, NULL, m_hInstance, NULL
        );
        assert(hwnd);
    }

private:
    LRESULT static CALLBACK WndProcStatic(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
        if (s_pInstance->m_hwnd == NULL) {
            s_pInstance->m_hwnd = hwnd;
        }
        return s_pInstance->WndProc(msg, wParam, lParam);
    }

    LRESULT CALLBACK WndProc(UINT msg, WPARAM wParam, LPARAM lParam) {
        switch (msg) {
            case WM_DESTROY:
                PostQuitMessage(0);
                break;
            case WM_CREATE:
                OnCreate();
                break;
            case WM_COMMAND:
                if (lParam == (int) m_hwndListBox && HIWORD(wParam) == LBN_DBLCLK) {
                    OnExecute();
                }
                break;

            default:
                break;
        }
        return DefWindowProc(m_hwnd, msg, wParam, lParam);
    }

    void OnCreate() {
        RECT rect;
        GetClientRect(m_hwnd, &rect);
        m_hwndListBox = CreateWindow(
                "ListBox", NULL, WS_CHILD | WS_VISIBLE | WS_BORDER | LBS_STANDARD,
                0, 0, rect.right, rect.bottom,
                m_hwnd, NULL, m_hInstance, NULL);

        for (string command: m_commands) {
            SendMessage(m_hwndListBox, LB_ADDSTRING, 0, (LPARAM) command.c_str());
        }
    }

    void OnExecute() {
        char s[100];
        int index = SendMessage(m_hwndListBox, LB_GETCURSEL, 0, 0);
        SendMessage(m_hwndListBox, LB_GETTEXT, (WPARAM) index, (LPARAM) s);
        cout << s << endl;
        WinExec(s, SW_SHOW);
    }
};

CMainWindow *CMainWindow::s_pInstance = nullptr;

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {
    new CMainWindow;
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}
