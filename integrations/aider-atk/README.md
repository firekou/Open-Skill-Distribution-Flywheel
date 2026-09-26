# aider-atk

用 **Aider 原生設定**連上 OpenAI 相容端點的可跟做資產，外加一個離線設定檢查器與一個最小任務。

沒有轉接層，沒有我們的程式跑在請求路徑上。

| 檔案 | 用途 |
|---|---|
| `SOURCE.md` | 釘住的上游來源、授權、實際安裝版本與兩者的差異 |
| `QUICKSTART.md` | Linux + Python 3.11 的單一路徑 |
| `TASK.md` | 最小任務與可查的 baseline |
| `sample/` | 要改的檔案與**固定不可改**的評分測試 |
| `check_config.py` | 離線設定檢查，不連網、不印金鑰 |
| `fake_openai_server.py` | 本機 loopback 假端點，用來錄協定 |
| `EVIDENCE.md` | 命令、exit code、原始輸出、變異控制、限制 |
| `AIDER_WHAT_WE_LEARNED.md` | 草稿：原作值得學什麼（未發布） |
| `ATK_OPTIONAL_SETUP_DRAFT.md` | 草稿：可選設定與未知（未發布） |

**狀態**：真實模型 NOT TESTED · 外部使用者 0 · 未發布 · 無費用。
