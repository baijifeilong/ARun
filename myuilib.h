//
// Created by Administrator on 2017/1/9.
//

#ifndef MYUILIB_H

#include <windows.h>
#include <cassert>
#include <map>

using namespace std;

struct CApp;
struct CWnd;

static CApp *pApp;

static CWnd *pWnd;

static CApp &GetApp() {
    return *pApp;
}

struct CApp {
    HINSTANCE m_hInstance;
    map<HWND, CWnd *> m_map;

    CApp();

    HINSTANCE GetInstance();

    int Run();

    BOOL PreTranslateMessage(MSG &Msg);
};

struct CWnd {
    HWND m_hwnd;

    static LRESULT CALLBACK StaticWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);

    LRESULT CALLBACK WndProcDefault(UINT Msg, WPARAM wParam, LPARAM lParam);

    virtual LRESULT WndProc(UINT Msg, WPARAM wParam, LPARAM lParam);

    HWND Create();

    void Destroy();

    virtual BOOL PreTranslateMessage(MSG &msg);
};

BOOL CApp::PreTranslateMessage(MSG &Msg) {
    for (HWND hwnd = Msg.hwnd; hwnd != NULL; hwnd = GetParent(hwnd)) {
        CWnd *pWnd = m_map[hwnd];
        if (pWnd) {
            if (pWnd->PreTranslateMessage(Msg)) {
                return TRUE;
            }
        }
    }
    return FALSE;
}

int CApp::Run() {
    MSG Msg;

    while (GetMessage(&Msg, NULL, 0, 0) > 0) {
        if (!PreTranslateMessage(Msg)) {
            TranslateMessage(&Msg);
            DispatchMessage(&Msg);
        }
    }
    return Msg.wParam;
}

CApp::CApp() {
    m_hInstance = GetModuleHandle(NULL);
    pApp = this;
}

HINSTANCE CApp::GetInstance() {
    return m_hInstance;
}


HWND CWnd::Create() {
    WNDCLASSEX wc;

    const char *szClassName = "DefaultClass";

    wc.cbSize = sizeof(WNDCLASSEX);
    wc.style = 0;
    wc.lpfnWndProc = StaticWndProc;
    wc.cbClsExtra = 0;
    wc.cbWndExtra = 0;
    wc.hInstance = GetApp().GetInstance();
    wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH) (COLOR_WINDOW + 1);
    wc.lpszMenuName = NULL;
    wc.lpszClassName = szClassName;
    wc.hIconSm = LoadIcon(NULL, IDI_APPLICATION);

    if (!RegisterClassEx(&wc)) {
        MessageBox(NULL, "Window Registration Failed!", "Error!",
                   MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    pWnd = this;
    m_hwnd = CreateWindowEx(
            0, szClassName, "App", WS_OVERLAPPEDWINDOW,
            CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,
            NULL, NULL, GetApp().GetInstance(), NULL);
    assert(m_hwnd);


    GetApp().m_map[m_hwnd] = this;

    ::SendMessage(m_hwnd, WM_CREATE, 0, 0);

    ShowWindow(m_hwnd, SW_SHOWDEFAULT);
    UpdateWindow(m_hwnd);

    return m_hwnd;
}

void CWnd::Destroy() {
    GetApp().m_map[m_hwnd] = NULL;
    m_hwnd = 0;
}

BOOL CWnd::PreTranslateMessage(MSG &msg) {
    return FALSE;
}

LRESULT CALLBACK CWnd::StaticWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    if (GetApp().m_map[hwnd]) {
        return GetApp().m_map[hwnd]->WndProc(msg, wParam, lParam);
    } else {
        return DefWindowProc(hwnd, msg, wParam, lParam);
    }
}


LRESULT CWnd::WndProc(UINT Msg, WPARAM wParam, LPARAM lParam) {
    return WndProcDefault(Msg, wParam, lParam);
}

LRESULT CALLBACK CWnd::WndProcDefault(UINT Msg, WPARAM wParam, LPARAM lParam) {

    switch (Msg) {
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;

        default:
            return DefWindowProc(m_hwnd, Msg, wParam, lParam);
    }
}

#define MYUILIB_H

#endif //MYUILIB_H
