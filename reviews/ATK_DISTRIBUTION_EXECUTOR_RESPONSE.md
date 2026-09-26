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
