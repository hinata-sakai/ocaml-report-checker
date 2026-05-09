\# Dockerでの使い方



このチェッカーは、Dockerを使って自分のPC上でWebアプリとして起動し、ブラウザからアクセスして使うことができます。



Dockerを使うことで、Python や OCaml の環境をPCに直接入れなくても、チェッカーを実行できます。



\---



\## 事前準備



Dockerで実行するには、PCに \*\*Docker Desktop\*\* がインストールされている必要があります。



コマンドプロンプトまたはPowerShellで、以下を実行してください。



```powershell

docker --version

```



次のように Docker のバージョンが表示されればOKです。



```text

Docker version xx.x.x, build xxxxx

```



続けて、Docker Compose も確認します。



```powershell

docker compose version

```



バージョンが表示されれば、Docker Compose も使用できます。



もし `docker` が認識されない場合は、Docker Desktopがインストールされていないか、起動していない可能性があります。



\---



\## 1. GitHubページを開く



まず、以下のGitHubページを開きます。



```text

https://github.com/hinata-sakai/ocaml-report-checker

```



\---



\## 2. 作業用フォルダを作成する



コマンドプロンプトまたはPowerShellを開き、以下を実行します。



```powershell

mkdir C:\\dev

cd C:\\dev

```



すでに `C:\\dev` がある場合は、`mkdir C:\\dev` でエラーが出ても問題ありません。  

その場合は、以下だけ実行してください。



```powershell

cd C:\\dev

```



\---



\## 3. GitHubからチェッカーを取得する



以下を実行します。



```powershell

git clone https://github.com/hinata-sakai/ocaml-report-checker.git

cd ocaml-report-checker

```



これで、自分のPC上にチェッカー一式がダウンロードされます。



\---



\## 4. 必要なファイルがあるか確認する



以下を実行します。



```powershell

dir

```



次のようなファイルが表示されていればOKです。



```text

Dockerfile

docker-compose.yml

```



\---



\## 5. DockerでWebアプリを起動する



Docker Desktopを起動した状態で、以下を実行します。



```powershell

docker compose up --build

```



初回は必要な環境を作成するため、少し時間がかかります。



次のように表示されれば、Webアプリの起動は成功です。



```text

OCaml課題チェッカー Web版を起動しました。

URL: http://0.0.0.0:8000

終了するには Ctrl + C を押してください。

```



このPowerShell画面は閉じずに、そのままにしておきます。



\---



\## 6. ブラウザでWebページを開く



ブラウザで、以下のURLを開きます。



```text

http://localhost:8000

```



OCaml課題チェッカーの画面が表示されれば成功です。





\---



\## 2回目以降の使い方



一度 `git clone` と `docker compose up --build` が終わっている場合、2回目以降は以下で起動できます。



```powershell

cd C:\\dev\\ocaml-report-checker

docker compose up

```



その後、ブラウザで以下を開きます。



```text

http://localhost:8000

```



\---



\## GitHubの最新版を取り込む場合



チェッカーが更新された場合は、以下を実行します。



```powershell

cd C:\\dev\\ocaml-report-checker

git pull

docker compose up --build

```



`Dockerfile` や `docker-compose.yml` が更新されている可能性もあるため、最新版を取り込んだ後は `--build` を付けて起動するのがおすすめです。



\---



\## 終了方法



Webアプリを終了したい場合は、`docker compose up` を実行している画面で以下を押します。



```text

Ctrl + C

```



完全に停止したい場合は、以下を実行します。



```powershell

docker compose down

```



\---



\## よくあるエラー



\### `docker` が認識されない場合



```text

'docker' は、内部コマンドまたは外部コマンド、

操作可能なプログラムまたはバッチ ファイルとして認識されていません。

```



この場合は、Docker Desktopがインストールされていないか、起動していない可能性があります。



Docker Desktopをインストールし、起動した状態で再度試してください。



\---



\### `no configuration file provided: not found` と表示される場合



```text

no configuration file provided: not found

```



この場合は、`docker-compose.yml` があるフォルダで実行できていません。



以下のように、チェッカーのフォルダへ移動してから実行してください。



```powershell

cd C:\\dev\\ocaml-report-checker

docker compose up --build

```



\---



\### `Dockerfile` が見つからない場合



Dockerで使うファイル名は、拡張子なしの以下です。



```text

Dockerfile

```



もし `Dockerfile.txt` になっている場合は、以下で名前を変更してください。



```powershell

ren Dockerfile.txt Dockerfile

```



その後、もう一度実行します。



```powershell

docker compose up --build

```



\---



\### `port is already allocated` と表示される場合



```text

port is already allocated

```



この場合は、すでに8000番ポートを別のアプリやDockerコンテナが使っている可能性があります。



まず、以下で停止します。



```powershell

docker compose down

```



その後、もう一度起動します。



```powershell

docker compose up

```



それでも解決しない場合は、他に8000番ポートを使っているアプリを終了してください。



\---



\## 注意



このチェッカーは、アップロードされた `.ml` ファイルを実行して採点します。



Dockerを使うことで実行環境を分けることはできますが、完全に安全になるわけではありません。



そのため、自分のPCや信頼できる環境で使用してください。  

不特定多数に公開するWebサービスとして運用する場合は、追加のセキュリティ対策が必要です。

