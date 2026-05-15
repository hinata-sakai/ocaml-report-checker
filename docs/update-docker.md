# Dockerで最新版に更新する方法

このページでは、DockerでOCaml課題チェッカーを使っている場合に、GitHubの最新版へ更新する手順を説明します。

---

## 1. 実行中のDockerを停止する

すでに `docker compose up` または `docker compose up --build` を実行している場合は、そのPowerShell画面で以下を押して停止します。

```text
Ctrl + C
```

完全に停止したい場合は、以下も実行します。

```powershell
docker compose down
```

---

## 2. チェッカーのフォルダへ移動する

PowerShellを開き、チェッカーを置いているフォルダへ移動します。

```powershell
cd C:\dev\ocaml-report-checker
```

別の場所に置いている場合は、自分の環境に合わせて移動してください。

---

## 3. GitHubの最新版を取り込む

`ocaml-report-checker` フォルダの中で、以下を実行します。

```powershell
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

## 4. 現在のバージョンを確認する

以下を実行します。

```powershell
type VERSION
```

次のように表示されれば、現在の最新バージョンです。

```text
v1.1.0
```

---

## 5. Dockerイメージを作り直して起動する

Webサイトの内容、Pythonファイル、Docker設定が更新されている可能性があるため、最新版を取り込んだ後は `--build` を付けて起動します。

```powershell
docker compose up --build
```

次のように表示されれば、起動は成功です。

```text
OCaml課題チェッカー Web版を起動しました。
URL: http://0.0.0.0:8000
終了するには Ctrl + C を押してください。
```

---

## 6. ブラウザで確認する

ブラウザで、以下のURLを開きます。

```text
http://localhost:8000
```

OCaml課題チェッカーの画面が表示されれば、最新版で使用できています。

---

## うまく反映されない場合

`git pull` 後に画面が古いままに見える場合は、以下を順番に試してください。

---

### 1. ブラウザを更新する

ブラウザの更新ボタンを押してください。

それでも変わらない場合は、以下のように強制更新を試してください。

```text
Ctrl + F5
```

---

### 2. Dockerを停止してから起動し直す

```powershell
docker compose down
docker compose up --build
```

---

### 3. Dockerのキャッシュを使わずに作り直す

それでも古い内容が残る場合は、以下を実行します。

```powershell
docker compose build --no-cache
docker compose up
```
