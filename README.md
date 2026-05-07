## 大学Linuxでの使い方

このチェッカーは、大学Linux上でWebアプリとして起動し、Windowsのブラウザからアクセスして使うことができます。

大学Linuxには Python と OCaml が入っているため、WindowsにOCamlを入れていない場合でも、この方法で実行できます。

---

### 1. GitHubページを開く

まず、以下のGitHubページを開きます。

```text
https://github.com/hinata-sakai/ocaml-report-checker
```

---

### 2. 大学LinuxにSSH接続する

PowerShellを開き、自分の学籍番号を使って大学Linuxに接続します。

```powershell
ssh 自分の学籍番号@linux.ed.tus.ac.jp
```

例：

```powershell
ssh 6326515@linux.ed.tus.ac.jp
```

パスワードを聞かれたら、大学Linuxのパスワードを入力します。

---

### 3. 大学Linux上でチェッカーを取得する

大学Linuxにログインできたら、以下を実行します。

```bash
git clone https://github.com/hinata-sakai/ocaml-report-checker.git
cd ocaml-report-checker
```

これで、大学Linux上にチェッカー一式がダウンロードされます。

---

### 4. Webアプリを起動する

大学Linux側で、以下を実行します。

```bash
python3 web_app.py
```

次のように表示されれば、Webアプリの起動は成功です。

```text
OCaml課題チェッカー Web版を起動しました。
URL: http://127.0.0.1:8000
終了するには Ctrl + C を押してください。
```

このPowerShell画面は閉じずに、そのままにしておきます。

---

### 5. 別のPowerShellでポート転送を行う

次に、別のPowerShellを新しく開きます。

そこで、自分の学籍番号を使って以下を実行します。

```powershell
ssh -L 8000:localhost:8000 自分の学籍番号@linux.ed.tus.ac.jp
```

例：

```powershell
ssh -L 8000:localhost:8000 6326515@linux.ed.tus.ac.jp
```

このPowerShellも閉じずに、そのままにしておきます。

---

### 6. ブラウザでWebページを開く

Windowsのブラウザで、以下のURLを開きます。

```text
http://localhost:8000
```

OCaml課題チェッカーの画面が表示されれば成功です。

`.ml` ファイルをアップロードして、「チェック実行」を押すと、各大問ごとに OK / NG が表示されます。

---

## 2回目以降の使い方

一度 `git clone` が終わっている場合は、2回目以降は再度 `git clone` する必要はありません。

大学LinuxにSSH接続した後、以下を実行します。

```bash
cd ocaml-report-checker
python3 web_app.py
```

その後、別のPowerShellでポート転送を行います。

```powershell
ssh -L 8000:localhost:8000 自分の学籍番号@linux.ed.tus.ac.jp
```

最後に、ブラウザで以下を開きます。

```text
http://localhost:8000
```

---

## 終了方法

Webアプリを終了したい場合は、`python3 web_app.py` を実行している画面で以下を押します。

```text
Ctrl + C
```

ポート転送をしているPowerShellも、使い終わったら閉じて大丈夫です。

---

## 注意

`自分の学籍番号` の部分は、各自の大学Linuxアカウントに置き換えてください。

例：

```powershell
ssh 6326515@linux.ed.tus.ac.jp
```

また、すでに `ocaml-report-checker` フォルダが存在する状態で再度 `git clone` を行うとエラーになることがあります。  
その場合は、2回目以降の使い方に従ってください。