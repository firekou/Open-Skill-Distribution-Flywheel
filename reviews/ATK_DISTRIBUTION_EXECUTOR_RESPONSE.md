
---

# ATK-AIDER-FIRST-USE-01 · revision 1

接單：`work_id: ATK-AIDER-FIRST-USE-01` · `revision: 1` · `source main: 251f9755ed5c1b4fd260b23b622e8ba5fad278eb`
開工時讀到的 live main（policy SHA）：`036b688b1a6824d52f33ca847579e5bac1350633`（state revision 30）
`dedup_key: firekou/Open-Skill-Distribution-Flywheel:ATK-AIDER-FIRST-USE-01:1:251f9755ed5c1b4fd260b23b622e8ba5fad278eb:executor`
session：`session_01RFeCsTYkVywjHvXk7od7Ab`
claim：2026-09-24T19:20Z 起，UTC 期限 **2026-09-25T18:30:00Z**（revision 1 我誤寫成 19:20Z，依 main 的固定期限更正，未自行延長）
分支：`claude/atk-aider-first-use-01`（自 `036b688` 開）
同 work_id 既有分支／PR／active claim：**查無**（`git ls-remote --heads origin` 無此分支；`state.json` 的 `research_program.active_claim` 為 null）

## 交付
`integrations/aider-atk/`：`SOURCE.md`、`QUICKSTART.md`、`TASK.md`、`sample/`（可改的檔案＋固定評分測試）、`check_config.py`＋`test_check_config.py`、`fake_openai_server.py`、`EVIDENCE.md`、`evidence/`、兩篇完整繁中草稿、`README.md`。

## 三件實際量到的事（不是讀文件推的）
1. **`OPENAI_API_BASE` 收根位址。** 設 `http://127.0.0.1:8801/v1`，錄到的實際請求路徑是 `/v1/chat/completions`。
2. **`openai/` 前綴不會送出。** 傳 `--model openai/local-test-model`，送出的 `model` 欄位是 `local-test-model`。
3. **關掉 analytics 不等於不連外。** 加了 `--no-analytics --no-check-update`，aider 啟動時仍嘗試連 `raw.githubusercontent.com` 抓 litellm 模型價格表；隔離環境下失敗，aider 印錯誤後繼續。

第 3 點正是工作包第 5 條要求區分的那件事，量到了。

## 控制
- baseline 任務測試：`exit=1`，1 failure（欄序對調讀反）＋1 error（`IndexError`，不是具名錯誤），情境 1/4/5 通過。刻意如此。
- 檢查器自身測試 8 項：`exit=0`。
- **變異控制三項**，各自 `unittest exit=1`：拿掉 prefix 檢查 → 對應測試紅；拿掉 endpoint-tail 檢查 → 對應測試紅；把金鑰改成直接印出 → 洩漏測試紅。未變異對照 `exit=0`。
- exit code 一律在指令後立刻 `rc=$?` 取，未被命令替換洗掉。

## 一項必須先講的偏離
工作包釘的 source 是 `Aider-AI/aider@5dc9490bb35f9729ef2c95d00a19ccd30c26339c`（`__version__` = `0.86.3.dev`）。我**讀原始碼**用的是這個 commit（`args.py:41,77`、`main.py:620-621` 行號可查）；但**實際執行**裝的是 PyPI release `aider-chat==0.86.1`，因為 PyPI 上沒有那個 dev 版本，時限內無法從原始碼裝完整相依。

**我沒有比對兩者差異。** 所以 SOURCE.md 與 EVIDENCE.md 逐條標了哪些結論來自讀碼（`5dc9490`）、哪些來自執行（`0.86.1`），兩者不互相背書。這是偏離，交給 reviewer 判。

## 五欄狀態
clean install **DONE**（但版本如上）· CLI／設定 **DONE** · 協定 **OFFLINE_PROTOCOL_ONLY** · 真模型 **NOT TESTED** · 外部使用 **NONE（0 位）**。

## 未做
未 merge · 未部署 · 未讀寫 secret · 未送上游 · 未邀請 · 未呼叫任何真實供應商 · 未新增費用 · 未新增 polling／controller／eval 平台 · 未引入 PR4 程式 · 未改 PR5 · 未重開任何舊修復輪次 · Windows/macOS 未測。

`findings_closed_by_executor: []`。停在這裡等獨立覆核。


## ATK-AIDER-FIRST-USE-01 · revision 2

覆核：`reviews/PR14_R1_AIDER_e8289655.md` · `APPROVED_WITH_CONDITIONS` · `reviewed_head: e828965585a1b9ee0cf33a4c5a868f62d5942aa5` · `blocking_findings: []` · 三個 conditions。
本輪只處理那三個條件，未擴大範圍。三項我都同意，沒有一項寫 NOT REPRODUCED。

### 條件一（P1）模型前綴假通過 —— REPRODUCED，已修
重現：`anthropic/model` → exit 0（應為 3）。重現時**另外發現一個覆核沒點到的**：`openai/`（前綴對、模型名空）同樣 exit 0。

舊條件是 `if "/" not in model`——它問「有沒有斜線」，不是「是不是 openai/」。改成只接受 `openai/<非空>`，並保留含斜線的模型名（如 `openai/meta-llama/Llama-3`）通過，因為有些相容端點的模型名本來就長那樣。

修後：`anthropic/model`、`openai/`、`some-model` 皆 exit 3；`openai/good-model`、`openai/meta-llama/Llama-3` exit 0。
測試 8 → 11 項，`exit=0`。**負控制**：把條件改回舊寫法 → `unittest exit=1`、`FAILED (failures=4)`。

### 條件二（P2）結構測試主張過強 —— 已縮小
EVIDENCE.md 與本回覆一併改：目前 `check_config.py` 逐行檢視無連網行為；那個 import 測試只是**低成本回歸提示**，擋不住 `os.system("curl ...")` 這類走既有 import 的路徑，**不是網路隔離，也不是完整防護**。未為此新增 sandbox、攔截或框架。

### 條件三（P2）外部報告缺來源 —— 已補
`AIDER_WHAT_WE_LEARNED.md` 兩份第一手敘述補上直接 URL，「個人經驗、非受控比較」界線原樣保留，未新增效果主張。

### P3 期限
main 固定 `2026-09-25T18:30:00Z`，我 revision 1 寫成 `19:20Z`，是我寫錯，已在上面更正。revision 2 沿 main 期限。

### 未變
真模型 NOT TESTED · 外部使用 0 · 任務 fixture 未動（`import_contacts.py` md5 `da2b54d9…`、`test_import_contacts.py` md5 `2952746b…` 皆不變）· 未 merge／部署／上游／邀請／付費／改 secret · 未新增 adapter 或平台。

`findings_closed_by_executor: []`。停在這裡等 `PR14_R2_CLAIM_OR_RESULT`。


---

<!-- 以下為 PR20（claude/atk-aider-delivery-01 @ 16b7268e）的 executor response，合併時逐字保留。兩個分支各自新建了這個檔案，所以依時間先後串接，沒有改寫任何一方。 -->

# ATK distribution：executor response

本分支從 main `bbb85b39` 建立，當時 main 上沒有這個檔案。PR17、PR18、PR19 各自的 executor response 仍在它們自己的分支上，本檔不複製那些內容，只寫這一批。

---

## ATK-AIDER-DELIVERY-01 revision 1（2026-09-26）

| 欄位 | 值 |
|---|---|
| executor | Claude，session `session_01RFeCsTYkVywjHvXk7od7Ab` |
| reviewer | GPT，須由不同的 run 從 GitHub 取證；executor 不自評 |
| packet | `reviews/ATK_AIDER_DELIVERY_01.md`，main `8e40827a9205d1243049b0a7f2e0299d78256d79` |
| dedup_key | `firekou/Open-Skill-Distribution-Flywheel:ATK-AIDER-DELIVERY-01:1:bbb85b39001ece19a8f19e3f186c1c3eeb1805cb:executor` |
| source_main | `bbb85b39001ece19a8f19e3f186c1c3eeb1805cb` |
| source_head | `a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41` |
| branch | `claude/atk-aider-delivery-01` |
| 內容 head | `4497e19de8c30effbf3b9b0aecd08463400e96aa`（本檔之前的最後一個 commit）。本檔 commit 後的最終 head 寫在 PR 與 PR19 的結果留言 |
| claim | [PR19 留言](https://github.com/firekou/Open-Skill-Distribution-Flywheel/pull/19#issuecomment-5842461371)，2026-09-26T02:42Z |
| 期限 | 2026-09-27T02:32:50Z；本批完成於期限前 |
| 新增 API 費用 | 0；沒有呼叫任何模型供應商 |
| 修復輪次 | 0/2 |

### 一、成果

| 步驟 | 檔案 | 狀態 |
|---|---|---|
| 1 | `integrations/aider-atk/delivery/README.md`：單一入口，8 步，每步都有 cwd、命令與預期 exit | 完成，實跑兩次 |
| 2 | `delivery/SOURCE_MANIFEST.json`（12 個檔案，含來源 commit、路徑、SHA-256、用途）＋ `delivery/get_assets.py`（只用標準庫，只做 `git show`，比對 hash 後才寫入） | 完成 |
| 3 | `research/adoption/aider/first-use/delivery/validate_feedback.py`，依賴列在 `requirements.txt`（6 個套件全部固定版本） | 完成 |
| 4 | 同目錄的 `fixtures/`（2 個合法、6 個不合法）與 `test_validate_feedback.py`（11 個測試） | 完成 |
| 5 | `delivery/REHEARSAL.md` ＋ `delivery/evidence/`（run 1、2、3 的命令與 log，外加人工參考修正） | 完成 |
| 6 | `delivery/LIVE_HANDOFF.md`（12 個待填欄位，逐欄標 READY／NOT_RUN／BLOCKED_ACCESS） | 完成；live 本身 NOT RUN |
| 7 | `delivery/RELEASE_CANDIDATE.md`（固定入口、兩篇文案、5 個渠道的格式、首發建議 R、帳號能力、回饋處理、關卡現況） | 完成；判定 NOT RELEASABLE |
| 8 | 本檔、Draft PR、PR19 結果留言 | 本檔完成；PR 與留言見下方連結 |

### 二、來源（只讀取，沒有改動）

| 來源 | commit | 用到的東西 |
|---|---|---|
| PR14 | `d1474670db12934c80caa05674c8e4320cbad312` | QUICKSTART、TASK、check_config.py、sample 兩個檔案 |
| PR16 | `1dcd625df3bde48b13b91abb3b03eb7e19371558` | TRIAL_RUNBOOK、repo metadata（渠道能力） |
| PR17 | `6ea3cec9937e74de8ce77f47c5e92d3d1617c506` | LIVE_EXECUTION_PLAN 的命令、停止程序、費用公式；LIVE_OWNER_APPROVAL_MATRIX |
| PR18 | `1abd74a4b7f14d8b5e397d33afa2ace212841099` | UPSTREAM_DEDUP_REPORT、兩份上游草稿的路徑 |
| PR19 | `a77d1e8e4d4d545bf8d4c5c7a803aa6b944c1a41` | FEEDBACK_SCHEMA v1.1.0（`b3531cc4…`）、兩篇文案、RELEASE_GATE、TARGET_CHANNEL_MATRIX |

五個來源分支都沒有被合併；作者原始證據沒有改動；也沒有任何 Draft PR 被標成 merged。

### 三、result commits

| commit | 內容 |
|---|---|
| `b6ed8ad5d9e60fb772159399d8ced07c27220a0f` | README、manifest、get_assets、validator、fixtures、tests |
| `a2f173d293a389d6c7dd6cbe5b2dd3b17ac51b34` | 修正 run 1 發現的阻礙：step 5 建 git baseline；依賴全部固定版本 |
| `2a7bf8e82c3c545f257b105b064d3fd5a1a6ac31` | REHEARSAL 與 run 1、run 2 的證據 |
| `33fb96000f52cb54299a766bcc0da249bfb7ef5a` | LIVE_HANDOFF、run 3 對照、README step 7 列出 Aider 會產生的 untracked 檔案 |
| `4497e19de8c30effbf3b9b0aecd08463400e96aa` | RELEASE_CANDIDATE |

`4497e19` 上 27 個交付檔案的 SHA-256：

```
896a24338ad94f77e1ac6bff442eea0ce244d28b42e5e884da61c1c23a13d7b8  integrations/aider-atk/delivery/LIVE_HANDOFF.md
b43c942b8ef94841e29fa26b8cdfad04666bdcf7d1e6347dbda1e31edfe3887c  integrations/aider-atk/delivery/README.md
b7454062a1ad9feba2440123a08fda84c69e61aa61c309ec9970084c2039196a  integrations/aider-atk/delivery/REHEARSAL.md
78b91019dd5509491560ac582a94b80cba23808cc5cfcac98fc7a49359f021c9  integrations/aider-atk/delivery/RELEASE_CANDIDATE.md
4f2a1bb6ef928d85900f8a52e3e2a2123ae04c277160caee567b27b97f6ada32  integrations/aider-atk/delivery/SOURCE_MANIFEST.json
a0f5000a61912ed51b22f9f4da4360352301b3653adec41a3492a70b034738f5  integrations/aider-atk/delivery/evidence/drive.sh
4fead3cf6c3337f50453e1f61b4e98ac6ddc6baf7b3dee8a0f65c08d71ef3a5f  integrations/aider-atk/delivery/evidence/human_reference_fix/import_contacts.py
18ca8713ebf41f3c4d6cfe0b86cfbc005bf895dc0e456a4fc5c9cc7c5ff2d14e  integrations/aider-atk/delivery/evidence/run1_commands.txt
f01e3b7ea5775a27d9d40d4d1565b83b5b8c634a7940c66bb1bcc34200a3e02c  integrations/aider-atk/delivery/evidence/run1_readme_b6ed8ad.log
a925bc7469a53e02d489937f459db8c0ba485a00ecf355c58aaa0bb0933360d4  integrations/aider-atk/delivery/evidence/run2_commands.txt
6b47e6ddb63b7d0c1195bb9808bd86e11df72b56d8d01adcbef556c522bf419a  integrations/aider-atk/delivery/evidence/run2_readme_a2f173d.log
d8cd91c132122719bfa06bc805b75c02abd5cc01951f594262a357d3f52010e0  integrations/aider-atk/delivery/evidence/run3_aider_output.log
394e40d76bd5ee4cd5e134913415d1835e5d05ebb619cbb9d7f2eb86bf45d763  integrations/aider-atk/delivery/evidence/run3_closed_port_control.log
16a600d9dca2c837b2f2e5306c661d7e703ebd5eac8a84fe653644ec79cee619  integrations/aider-atk/delivery/evidence/run3_commands.txt
08e613b6b7495d810fe5fef35281de925ac613e30be11ae9deea8c94ba6565cf  integrations/aider-atk/delivery/get_assets.py
a500003f7c7473a79b5cd8aac9c112a8339659315cd413724137cd742b571ccd  research/adoption/aider/first-use/delivery/fixtures/README.md
66bfeb47b0edca02665bf64867110e1d87689357535212386327b86ab1852e0e  research/adoption/aider/first-use/delivery/fixtures/invalid_bad_source_url.json
6fe0e2c4f446dba7b6bbab7079070ef1d19c021392f4d2772b38bff7aee7c37e  research/adoption/aider/first-use/delivery/fixtures/invalid_failed_exceeds_total.json
40248fc3fa6e7d173026f10edac007cf8abcd214954d5aff2874ea247f4fb0fd  research/adoption/aider/first-use/delivery/fixtures/invalid_false_pass.json
ff27ebb28813f5ed22097b8df307bbf620e0a4347be3573cd24b0788ab57eaf1  research/adoption/aider/first-use/delivery/fixtures/invalid_internal_as_external.json
5851acb3514571276372aa78c127bf04aae438e940c3e0bbfcd11620a5bd6183  research/adoption/aider/first-use/delivery/fixtures/invalid_malformed.json
9d097e3032e7be7dae072ea388c2e292cbd40e6ad45952c6b4c1574262fe8893  research/adoption/aider/first-use/delivery/fixtures/invalid_secret_not_echoed.json
ec9051241bcd988337c2e7ed7633ba6a365f6dad032394d262e50527311c0b05  research/adoption/aider/first-use/delivery/fixtures/valid_fail.json
53bffe22ede5c07afa811c22a1d36b6d929a347d20cb37c0f68cceedabf2dd80  research/adoption/aider/first-use/delivery/fixtures/valid_pass.json
228f979834470fc89c85371a9ea0c6e3625fe156771629fc5ae927cfd4aca0ad  research/adoption/aider/first-use/delivery/requirements.txt
b867936dc75d92c5925f1fb92bb48ccdd33d4695fa3132d67750dffeeb257a2c  research/adoption/aider/first-use/delivery/test_validate_feedback.py
b14abb0e5c64c988ba7e70ec6a8650c02fa303d99261036ace0f5fc85c70cd5c  research/adoption/aider/first-use/delivery/validate_feedback.py
```

### 四、實跑的命令與 exit

以下都是從 GitHub 全新 clone 後，在乾淨目錄照 README 跑的；完整紀錄在 `evidence/`。

| 項目 | 結果 |
|---|---|
| run 1（README `b6ed8ad`） | 第 1–5、8 步都照預期；**第 7 步 `git diff` exit 129**，因為取出的目錄不是 git repo。這是阻礙 B1，已在 `a2f173d` 修正 |
| run 2（README `a2f173d`），第 1–5、7、8 步 | 全部符合預期：取出 12 個檔案 exit 0；`aider 0.86.1`（litellm 1.75.0、openai 1.99.1）；check_config 分別 exit 0 與 4；**baseline exit 1，`FAILED (failures=1, errors=1)`**；validator exit 0 |
| 人工參考修正（副本） | 5/5 OK，`git diff --stat` 只有 `import_contacts.py`。**這是人寫的，不是模型結果** |
| 竄改測試檔（副本） | hash 變成 `06ebaa1f…`，被第 7 步抓出 |
| validator 跑全部 8 個 fixtures | 2 個 VALID、6 個 INVALID，exit 1；合成秘密標記的回顯次數為 0；單元測試 11/11 OK |
| get_assets 負控制 | `--out` 不是空目錄 → exit 2；manifest hash 被改 → exit 1，沒有寫出任何檔案；shallow clone → exit 2 並印出 fetch 指令，照做之後 exit 0 |
| run 3（對照） | 用 PR17 L2 的同一組旗標跑 Aider，對象是 `127.0.0.1:9`（沒有東西在聽）。沒有連到任何模型；**exit 0，68 秒，嘗試 9 次**；第 7 步正確判定為未解決 |
| 本機既有檢查（`b6ed8ad` 之前） | 11/11 OK；把 cross-field 規則停掉的突變對照會 FAILED |

### 五、離線已測，live 沒做

- **已測（AUTHOR_TESTED）**：README 第 1–5、7、8 步；validator 與 fixtures；get_assets 的完整性檢查與缺 commit 的處理；Aider 對關閉 port 的行為與事後判定。
- **沒做（NOT RUN）**：README 第 6 步（真模型）；LIVE_HANDOFF 的 L1–L4；任何發布或聯絡；任何上游送出。
- **沒測到的範圍**：
  - Windows 與 macOS 沒跑。
  - pip cache 不是空的，所以沒有量到下載量。
  - 沒有外部使用者跑過。
  - 網路：套件安裝經過 PyPI 與 GitHub，但沒有呼叫任何模型供應商。**這不代表完整的網路隔離。**

### 六、偏離與說明

- **run 3** 超出第 5 步的字面範圍：多跑了一次 Aider，對象是關閉的 loopback port。
  - 這次沒有模型、沒有供應商、沒有花費，用的是佔位金鑰。
  - 目的：確認第 7 步在 Aider 真的執行過之後仍然能正確判定。
  - 發現：Aider 會自動新增 `.gitignore`；README 已據此補上說明。
  - 如果 reviewer 認為這超出範圍，可以只看 run 1、run 2。
- **本檔是新建的**，不是追加：分支建立時 main 上沒有這個檔案。

### 七、下一批可直接使用的輸入

| 對象 | 需要的輸入 | 用在哪裡 |
|---|---|---|
| GPT | 本 PR 的最終 head；照 README 從乾淨目錄跟做，重點看 run 2 的負控制和 validator | 交付驗收；最多修 2 輪 |
| 負責人 | `OWNER_ATK_AIDER_LIVE_DECISION`：只勾一個 A／B／C／D，並填總費用上限、執行環境、金鑰注入與輪替確認 | LIVE_HANDOFF 第一節第 1–6、9、10 項 → `ATK-AIDER-LIVE-01` |
| 負責人 | `OWNER_FIRST_USE_RELEASE_CHANNEL_AND_SENDER_DECISION`：是否採用首發 R、由哪個帳號發、是否授權 merge | RELEASE_CANDIDATE 第三、四、六節 → `ATK-FIRST-USE-01` |
| ATK 營運端 | 價格，以及「超限時拒絕請求」的書面說明 | 沒有這兩樣，選項 A 仍然不能選 |

### 八、邊界

- 沒有 merge、部署、發布、聯絡，也沒有送上游或社群。
- 沒有操作任何憑證，也沒有新增支出。
- 沒有讀取、印出或搬運任何秘密；測試只用合成資料和佔位值。
- 沒有修改 `governance/state.json`；五個來源分支都沒有動。
- `findings_closed_by_executor: []`

---

## ATK-AIDER-DELIVERY-01 revision 2：修復 PR20 R1 ATK-D1-01（repair 1/2，2026-09-26）

| 欄位 | 值 |
|---|---|
| 依據 | [PR20 R1 review](https://github.com/firekou/Open-Skill-Distribution-Flywheel/blob/main/reviews/PR20_R1_DELIVERY_0ff12e4b.md)（main `3c19ee2`）BLOCKED，P1 ATK-D1-01 |
| reviewed head | `0ff12e4bfa7d18c742ce81276d62bfac19962103` |
| 修復 commit | `4f39d3430b78dac46d03f91296af3d1299cee8bb` |
| 修復輪次 | 1/2 |
| 新增 API 費用 | 0；沒有呼叫任何模型供應商 |

### 一、先重現（REPRODUCED）

在 `0ff12e4` 的 validator 上，把合成標記 `SYNTHETIC_IDENTITY_ALICE_KEYTAG_77` 同時放進目錄名與檔名，得到：
```
INVALID <S>/SYNTHETIC_IDENTITY_ALICE_KEYTAG_77_dir/SYNTHETIC_IDENTITY_ALICE_KEYTAG_77.json: /entry additionalProperties
INVALID <S>/SYNTHETIC_IDENTITY_ALICE_KEYTAG_77_dir/SYNTHETIC_IDENTITY_ALICE_KEYTAG_77.json: /environment/os enum
VALID   <S>/SYNTHETIC_IDENTITY_ALICE_KEYTAG_77_dir/ok_ALICE.json
exit=1
ERROR cannot read record file: <S>/SYNTHETIC_IDENTITY_ALICE_KEYTAG_77_dir/missing_ALICE.json   (exit=2)
```
另外找到兩處同類外洩，一併修正：
- 讀不到 schema 時，錯誤訊息會印出 `--schema` 的路徑；
- 參數錯誤時，argparse 會把收到的參數原樣印回（`unrecognized arguments: --bogus_ALICE`）。

### 二、修正（只改 review 允許的範圍）

- `validate_feedback.py`：
  - 紀錄一律用命令列順序稱呼：`record 1`、`record 2`…。VALID、INVALID、malformed JSON、讀不到檔案，全都不印路徑或檔名。
  - schema 相關錯誤只寫 `--schema` 這個選項名稱。
  - usage 錯誤只印固定的一行用法，不重複收到的參數。
- `test_validate_feedback.py`：新增 `PathRedaction` 9 個測試。
  - 合成標記同時放在目錄名與檔名；逐一斷言 stdout 與 stderr 都不含 `SYNTHETIC_IDENTITY_ALICE_KEYTAG_77`、`ALICE`、`KEYTAG`。
  - 涵蓋：合法、不合法、malformed、檔案不存在、傳入目錄、schema 讀不到、schema 不符、參數錯誤，以及多筆紀錄的編號順序。
- `integrations/aider-atk/delivery/README.md` 第 8 步：預期輸出從 `VALID   fixtures/valid_fail.json` 改為 `VALID   record 1`，並補一句「紀錄以順序稱呼，不印檔名或路徑」。
  - **這一處不在 review 列的三項內**，但輸出格式改了，入口上寫的預期輸出如果不跟著改就會錯，所以改了，並在此註明。
- 沒有改動：來源資產、`REHEARSAL.md` 與 `evidence/` 的原始演練紀錄、`LIVE_HANDOFF.md`、`RELEASE_CANDIDATE.md`。
  - 因此 `REHEARSAL.md` 裡記錄的 `VALID   fixtures/valid_fail.json` 是 `a2f173d` 當時的真實輸出，保留不改。

### 三、正／負控制

| 控制 | 命令 | 結果 |
|---|---|---|
| 新測試對新 validator | `ATK_FEEDBACK_SCHEMA=… python -m unittest test_validate_feedback` | `Ran 20 tests` · `OK` · exit 0（原 11 個加新 9 個） |
| **負控制**：新測試對舊 validator（`0ff12e4`） | 同上，只把 validator 換成 `0ff12e4` 版本 | `FAILED (failures=8)`，exit 1。9 個新測試中 8 個抓到外洩；`test_wrong_schema` 在舊版也通過，因為舊版的 SHA 不符訊息本來就沒印路徑，保留作為防護 |
| reviewer 的原始控制 | 標記在目錄名與檔名，跑 `invalid_secret_not_echoed` | `INVALID record 1: /entry additionalProperties`、`INVALID record 1: /environment/os enum`，exit 1；標記命中次數 0 |

### 四、從 GitHub 全新 clone 驗證（`4f39d34`，2026-09-26T03:11:37Z–03:11:49Z）

| 步驟 | 結果 |
|---|---|
| `git checkout --detach 4f39d34…` | HEAD `4f39d3430b78dac46d03f91296af3d1299cee8bb` |
| README 第 2 步 `get_assets.py --out "$RUN"` | exit 0，12 個檔案全部驗證通過 |
| README 第 8 步 `validate_feedback.py … fixtures/valid_fail.json` | `VALID   record 1`，exit 0 |
| `unittest test_validate_feedback` | `Ran 20 tests` · `OK` · exit 0 |
| 8 個 fixtures 一起跑 | 2 VALID／6 INVALID，exit 1。每行只有 `record N`、JSON Pointer 與錯誤類型 |
| reviewer 控制 | exit 1，標記命中 0 |

新檔案的 SHA-256：
```
052eae4de11d322c4112ee152cb9d04703c50a4a685cb91cdbf8168d359070a6  research/adoption/aider/first-use/delivery/validate_feedback.py
a7b900a41993a926d942a6014c1a73a5544e976100c5272c852d296177ad0f59  research/adoption/aider/first-use/delivery/test_validate_feedback.py
d69e62f3af819ab5f4faf75d2c7034e5d17ac56f15509cc03c8b3c609ed60a5a  integrations/aider-atk/delivery/README.md
```
`4497e19` 列出的其他 24 個檔案都沒有改動。

### 五、邊界

- 沒有 live 呼叫、花費、發布、聯絡、merge、送上游，也沒有操作任何憑證。
- 最終 result head 是本段 commit 之後的那個，寫在 PR20 的結果留言。
- `findings_closed_by_executor: []`：ATK-D1-01 是否關閉，由 GPT 判定。
