# 來源與版本

## 指定來源（工作包釘的）
- upstream：`Aider-AI/aider`
- source commit：`5dc9490bb35f9729ef2c95d00a19ccd30c26339c`
- 取得方式：`git fetch --depth 1 origin 5dc9490bb35f9729ef2c95d00a19ccd30c26339c`，本地核對 `git rev-parse HEAD` 相符
- `aider/__init__.py` 的 `__version__` = **`0.86.3.dev`** —— 這是**開發中版本**，不是正式 release，本文件不以穩定版稱呼它
- LICENSE：`LICENSE.txt`，Apache License 2.0（開頭已核）
- `pyproject.toml`：`requires-python = ">=3.10,<3.15"`

## 實際安裝的版本，以及為什麼不同
本輪**實際執行**的是 PyPI 上的 **`aider-chat==0.86.1`**（`aider --version` 回報 `aider 0.86.1`），不是上面那個 dev commit。

理由，照工作包要求說明差異而不是悄悄換：
- 指定 source 是 `0.86.3.dev`，PyPI 上沒有這個版本可裝；要用它就得從原始碼安裝整套相依，本輪時限內做不完。
- 工作包寫「優先固定 release」，`0.86.1` 是可釘的正式 release。
- **差異未逐一比對。** 我沒有 diff `0.86.1` 與 `5dc9490` 之間的變更。所以：
  - 凡是我**讀原始碼**得到的結論，標的是 `5dc9490`。
  - 凡是我**實際執行**得到的觀察，標的是 `0.86.1`。
  - 兩者不互相背書。下面的 EVIDENCE.md 逐條標了是哪一種。

## 從指定 source 讀到的原生設定依據（非轉述，行號可查）
- `aider/args.py:77` 定義 `--openai-api-base`
- `aider/args.py:41` 設 `auto_env_var_prefix="AIDER_"` —— 所以**旗標對應的環境變數是 `AIDER_OPENAI_API_BASE`**，不是 `OPENAI_API_BASE`
- `aider/main.py:620-621`：
  ```python
  if args.openai_api_base:
      os.environ["OPENAI_API_BASE"] = args.openai_api_base
  ```
  也就是旗標最後是寫進 `OPENAI_API_BASE` 這個環境變數，底層再由 litellm 讀走。

**這一點值得單獨講**：`OPENAI_API_BASE` 與 `AIDER_OPENAI_API_BASE` 兩個都會生效，但走的是不同路徑。直接設 `OPENAI_API_BASE` 是給底層讀；設 `AIDER_OPENAI_API_BASE` 是餵給那個旗標，再由 `main.py` 轉寫成前者。文件裡若只寫其中一個而讀者設了另一個，兩邊都會「看起來沒錯但沒生效」。

## 相依與環境（本輪實際）
- OS：Linux
- Python：3.11.15（`/usr/bin/python3.11`）
- venv：`python3.11 -m venv`，`pip install "aider-chat==0.86.1"`
- 未使用任何 ATK endpoint、未使用任何真實供應商金鑰

## 未做
未簽署 CLA、未送任何 upstream issue 或 PR、未改 upstream 任何一行。CONTRIBUTING 要求顯著變更先討論，本輪只在自家 repo 備稿。
