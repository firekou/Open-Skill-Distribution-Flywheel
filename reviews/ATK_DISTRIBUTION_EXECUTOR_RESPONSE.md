# ATK distribution executor response

> 合併注意：本分支從 main `efe20e67` 開，main 上還沒有這個檔案（PR14、PR16、PR17 各自新增了同名檔案）。合併時各段都要保留、不互相覆蓋。本分支只放本 work 的段落。

---

# ATK-UPSTREAM-01 · revision 1

| | |
|---|---|
| work_id / revision | `ATK-UPSTREAM-01` / 1 |
| 派工 | https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/17#issuecomment-5838137130（依 `reviews/PR17_R1_LIVE_PREP_6ea3cec9.md`） |
| claim | https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/17#issuecomment-5838315225，2026-09-25T19:27Z |
| session | `session_01RFeCsTYkVywjHvXk7od7Ab`（沿用既有 session，不能證明有常駐 launcher） |
| source main | `efe20e67d1f96092b00e2154f3ff2712e256fab7` |
| source result | PR17 `6ea3cec9937e74de8ce77f47c5e92d3d1617c506` |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:ATK-UPSTREAM-01:1:efe20e67d1f96092b00e2154f3ff2712e256fab7:executor` |
| deadline | 2026-09-26T19:30:00Z |
| repair | 0/2 |
| branch | `claude/atk-aider-upstream-01` |

## 這份工作幫誰做什麼
Aider 和 LiteLLM 的維護者與使用者都會用到這些結果：我們在自己的真實呼叫準備過程中，發現兩個上游行為會讓使用者白白等待、多送請求。本批先查上游是否已有人回報，再把真正沒人回報的部分寫成可以直接提交的 issue 草稿。**全部沒有送出。**

## 交付
| 檔案 | 內容 |
|---|---|
| `research/adoption/aider/upstream/UPSTREAM_DEDUP_REPORT.md` | 查重結論、逐筆比對、版本矩陣、實測表、限制、建議 |
| `research/adoption/aider/upstream/DRAFT_AIDER_ISSUE.md` | Aider issue 草稿（402／403 被重試 9 次、credits 字串判斷在這條路徑不會命中） |
| `research/adoption/aider/upstream/DRAFT_LITELLM_ISSUE.md` | LiteLLM issue 草稿（OpenAI 分支把 403 轉成 APIError，而不是 PermissionDeniedError） |
| `research/adoption/aider/upstream/evidence/upstream_repro.py` ＋ `repro/`（manifest、43 個檔） | Aider 端到端 loopback 測試，兩個版本，共 14 個 case |
| `research/adoption/aider/upstream/evidence/litellm_direct_mapping.py` ＋ `direct/`（index 與原始輸出） | 直接呼叫 LiteLLM 的對照測試，涵蓋三個版本 |

兩支 `.py` 是測試程式，不是純文字證據，比照 PR16、PR17 的前例保留在 evidence 目錄。

## 結論（逐項分開）
| 行為 | Aider | LiteLLM |
|---|---|---|
| 402／403 被重試 9 次 | **需要新 issue**（草稿已備） | **需要新 issue**（草稿已備；403 的根因在這裡） |
| 失敗後 exit code 仍是 0 | **已有 #5552 與 PR #5553**，跟進即可，不另開 | 不適用 |
| `max_retries: 0` 與重試的交互 | **不需要貢獻**（最多在 #4659 補一個資料點，未送） | 不需要貢獻 |

## 本批新增、可回查的事實（AUTHOR_TESTED，全部 loopback）
1. LiteLLM 1.75.0、1.81.10、1.102.1 走 OpenAI 相容路徑時，402 和 403 都被轉成 `APIError`（帶著原本的 status_code）；400、401、404、429、500 都有對應的專屬錯誤類別。證據：`direct/index.json`，sha256 `7580934706bf1a2bde476850ea420558623aeb488b6e3a8b27f811beb3857921`。
2. Aider 0.86.1 與 0.86.2 表現完全一樣：
   - 402（三種 body 格式）與 403：各 9 個請求
   - 401：1 個請求
   - 429：27 個請求；加上 `max_retries: 0` 後降為 9 個
   - exit code 全部是 0

   證據：`repro/manifest.json`，sha256 `2c0f9f45cec46c3bb5d98799a60b6252ff301c93b0b1f88664009fe7fa28a49f`。
3. Aider 既有的「insufficient credits 不重試」判斷（commit `e0b42d5`）要求錯誤文字裡出現 `'"code":402'`。但 LiteLLM 的 OpenAI 分支只保留 `error.message`，所以不論 body 怎麼寫，這個判斷都不會命中。
4. 上游預設分支：Aider `main` 停在 `5dc9490`（2026-05-22），PR #5553 未合併；LiteLLM `main@636eb4c`（2026-09-25）仍沒有 402／403 的分支。
5. **關於 PR17 的補充說明（不是更正）**：PR17 寫「402 會被重試 9 次」，在它使用的路徑（`openai/<model>` 加 `OPENAI_API_BASE`）上成立，而且與 OpenRouter 實際回傳的 body 格式無關。

## 命令與結束碼
| 命令 | exit |
|---|---|
| `pip download --no-deps litellm==1.102.1 aider-chat==0.86.2` | 0 |
| `git clone --depth 1 --filter=blob:none --sparse` Aider-AI/aider、BerriAI/litellm（唯讀） | 0 |
| `python3.11 -m venv v0862 && pip install aider-chat==0.86.2`（scratch） | 0 |
| `python3.11 -m venv vlatest && pip install litellm==1.102.1`（scratch） | 0 |
| `python3 upstream_repro.py`（14 個 case，aider 本身的 exit 都是 0） | 0 |
| `python litellm_direct_mapping.py <port> <out>` × 3 個版本 | 0 |
| Exa `web_search_exa` × 6、`web_fetch_exa` × 2（查詢內容見 dedup report §2） | 成功 |

## 證據等級與限制
- 本機測試屬 **AUTHOR_TESTED**，還沒有 reviewer 重跑。上游 issue／PR 的狀態是本批讀取當下 **OBSERVED** 的結果，之後可能改變。
- 假端點回的 body 是自己設計的，**不是**任何真實 provider 的原文。
- 請求數是本機假端點收到的 HTTP 請求數。**被拒絕的請求會不會計費：UNKNOWN**，本批不主張。
- 沒有測 `openrouter/` provider 路徑，也沒有測互動模式。

## 全程進度（S0–S7）
| 階段 | 狀態 |
|---|---|
| S1、S2 | completed（PR16 r2、PR14） |
| S3 準備 | completed（PR17，APPROVED_WITH_CONDITIONS） |
| S3 真實呼叫 | gated：`OWNER_ATK_AIDER_LIVE_DECISION` |
| S4、S5、S7 | gated／not started |
| S6 上游 | **ATK-UPSTREAM-01 本批 delivered，待 review**；送出上游需負責人另外授權 |

**下一步**：GPT 覆核本批 → 由負責人決定要不要送出兩份草稿，以及要不要在 #5552 補資料點。

## 邊界
本批未做以下任何事：
- live 呼叫、讀或改 secrets、登入帳務、建立 key 或 project、付費 API
- 送上游 issue、留言或 PR，或任何對外聯絡
- merge、部署、改 settings 或權限、polling
- 修改 PR14、PR16、PR17

`findings_closed_by_executor: []`。停在 Draft PR，等獨立覆核。
