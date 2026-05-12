# 大学Linuxで最新版に更新する方法

このページでは、大学Linux上でOCaml課題チェッカーを使っている場合に、GitHubの最新版へ更新する手順を説明します。

---

## 1. 実行中のWebアプリを停止する

すでに `python3 web_app.py` を実行している場合は、そのPowerShell画面またはターミナルで以下を押して停止します。

```text
Ctrl + C
```

ポート転送用に開いている別のPowerShellも、必要であれば閉じて大丈夫です。

---

## 2. 大学LinuxにSSH接続する

PowerShellを開き、自分の学籍番号を使って大学Linuxに接続します。

```powershell
ssh 自分の学籍番号@linux.ed.tus.ac.jp
```

例：

```powershell
ssh 6326515@linux.ed.tus.ac.jp
```

---

## 3. チェッカーのフォルダへ移動する

大学Linuxにログインできたら、以下を実行します。

```bash
cd ocaml-report-checker
```

もし以下のようなエラーが出る場合は、まだチェッカーを取得していない可能性があります。

```text
No such file or directory
```

その場合は、[大学Linuxでの使い方](./university-linux.md) の手順に従って、先に `git clone` を行ってください。

---

## 4. GitHubの最新版を取り込む

`ocaml-report-checker` フォルダの中で、以下を実行します。

```bash
git pull origin main
```

次のような内容が表示されれば、最新版の取り込みは成功です。

```text
Updating ...
Fast-forward
```

すでに最新版の場合は、以下のように表示されることがあります。

```text
Already up to date.
```

この場合も問題ありません。

---

## 5. 現在のバージョンを確認する

以下を実行します。

```bash
cat VERSION
```

次のように表示されれば、現在の最新バージョンです。

```text
v1.1.0
```

---

## 6. Webアプリを起動し直す

更新が終わったら、もう一度Webアプリを起動します。

```bash
python3 web_app.py
```

次のように表示されれば、起動は成功です。

```text
OCaml課題チェッカー Web版を起動しました。
URL: http://127.0.0.1:8000
終了するには Ctrl + C を押してください。
```

---

## 7. ポート転送を行う

別のPowerShellを開き、自分の学籍番号を使って以下を実行します。

```powershell
ssh -L 8000:localhost:8000 自分の学籍番号@linux.ed.tus.ac.jp
```

例：

```powershell
ssh -L 8000:localhost:8000 6326515@linux.ed.tus.ac.jp
```

---

## 8. ブラウザで確認する

Windowsのブラウザで、以下のURLを開きます。

```text
http://localhost:8000
```

OCaml課題チェッカーの画面が表示されれば、最新版で使用できています。
