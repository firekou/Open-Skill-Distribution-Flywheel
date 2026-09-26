# 最小任務：把固定欄序的 CSV 匯入改成依欄名讀取

這是一個**教學用的合成任務**，不是哪個外部使用者驗證過的需求，也不是任何既有遷移案例的重現。

## 檔案
- `sample/import_contacts.py` —— 要改的就是這一支
- `sample/test_import_contacts.py` —— **評分測試，固定不可改**

測試是評分標準。**不要讓 agent 改測試**，改了就沒有標準了。跑之前先把它加到 read-only，或至少改完後 `git diff` 確認它沒被動過。

## 現在的行為
依**位置**讀：第一欄當 name，第二欄當 email。

## 要達成的行為
依**欄名**讀，並且：
1. 原本 `name,email` 的順序要繼續可用
2. 欄序對調（`email,name`）也要讀對
3. 沒有 email 欄時，丟 `MissingColumnError`，訊息裡要有 `email` 這個字
4. 空字串要保留成空字串，不要變成 `None`
5. 非 ASCII（中文等）要原樣保留

## baseline：改之前跑一次，結果是可查的
```
$ cd sample && python3.11 -m unittest test_import_contacts -v
Ran 5 tests
FAILED (failures=1, errors=1)     exit=1
```
- 情境 1、4、5 **通過**
- 情境 2 **failure**：`[{'name': 'ada@example.com', 'email': 'Ada'}]` —— 欄序對調時整個讀反
- 情境 3 **error**：`IndexError: list index out of range` —— 不是一個講得清楚的錯誤

改完之後五項要全過，而且是**改 `import_contacts.py` 改到過**，不是改測試改到過。

## 給 executor 的硬規則
不可以拿參考答案或假回應當成 aider 的成果。要留原始檔與 diff，讓人看得出哪些字是模型寫的。
