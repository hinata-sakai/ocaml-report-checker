# -*- coding: utf-8 -*-

"""Second-period Week3 app scaffold.

This module provides dedicated UI entrypoints for 2期第3週 while reusing the
current 1期 page as an initial clone.
"""


WEEK3_TASK_GUIDE_HTML = """
  <p class="guide-intro">
    関数型言語 OCaml を用いて，基本的な単純ソートおよび分割統治法に基づく
    ソートアルゴリズムを実装します。さらに，プログラムを改造して
    「要素の比較回数」を計測・可視化することで，データの初期状態や要素数によって
    各アルゴリズムの処理効率がどのように変化するかを数値的に考察し，
    アルゴリズムの特性への理解を深めることを目的とします。
  </p>

  <h3 class="guide-section-title">1. 単純ソートアルゴリズムの実装</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      以下から1つ以上のソート関数を選択して実装しなさい。
      意欲のある方は，すべての関数を実装してもかまいません。
    </p>

    <ul class="guide-submit-list">
      <li>交換ソート（exchange_sort）</li>
      <li>選択ソート（selection_sort）</li>
      <li>挿入ソート（insertion_sort）</li>
    </ul>

    <p class="guide-card-text">
      これらの実装のために，以下のように補助関数を利用して実装しなさい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">交換ソート（exchange_sort）を選択した場合</p>
        <ol class="guide-submit-list">
          <li>
            リストの先頭から隣り合う要素を順に比較し，大小関係が逆であれば入れ替える操作を
            末尾まで行う関数 exchange_pass を作成しなさい。
            この関数は，1回の走査を行った後のリストと，
            「入れ替え（交換）が1回でも発生したか」を表す真偽値（bool）のペアを返すようにしなさい。
          </li>
          <li>
            上記の補助関数を利用して，走査中に入れ替えが発生しなくなるまで
            （真偽値が false になるまで）繰り返し処理を行う本体の exchange_sort を完成させなさい。
          </li>
        </ol>
        <pre class="guide-card-code">exchange_pass : int list -&gt; int list * bool
exchange_sort : int list -&gt; int list</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">選択ソート（selection_sort）を選択した場合</p>
        <ol class="guide-submit-list">
          <li>
            与えられたリスト内の最小値と，その最小値を除いた「残りのリスト」のペアを返す
            関数 select_min を作成しなさい。
          </li>
          <li>
            上記の補助関数を利用して，本体の selection_sort を完成させなさい。
          </li>
        </ol>
        <pre class="guide-card-code">select_min : 'a list -&gt; 'a * 'a list
selection_sort : int list -&gt; int list</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">挿入ソート（insertion_sort）を選択した場合</p>
        <ol class="guide-submit-list">
          <li>
            すでにソートが終わっているリストの正しい位置に，新しい要素を挿入する
            関数 insert を作成しなさい。
          </li>
          <li>
            上記の補助関数を利用して，本体の insertion_sort を完成させなさい。
          </li>
        </ol>
        <pre class="guide-card-code">insert : 'a -&gt; 'a list -&gt; 'a list
insertion_sort : int list -&gt; int list</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">2. 分割統治法ソートアルゴリズムの実装</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      以下から1つ以上のソート関数を選択して実装しなさい。
      意欲のある方は，すべての関数を実装してもかまいません。
    </p>

    <ul class="guide-submit-list">
      <li>マージソート（merge_sort）</li>
      <li>クイックソート（quick_sort）</li>
    </ul>

    <p class="guide-card-text">
      これらの実装のために，以下のように補助関数を利用して実装しなさい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">マージソート（merge_sort）を選択した場合</p>
        <ol class="guide-submit-list">
          <li>
            1つのリストを偶数番目と奇数番目の2つに分割する関数 split を作成しなさい。
          </li>
          <li>
            2つのソート済みリストを1つに綺麗に合流させる関数 merge を作成しなさい。
          </li>
          <li>
            上記の補助関数を利用して，本体の merge_sort を完成させなさい。
          </li>
        </ol>
        <pre class="guide-card-code">split : 'a list -&gt; 'a list * 'a list
merge : int list -&gt; int list -&gt; int list
merge_sort : int list -&gt; int list</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">クイックソート（quick_sort）を選択した場合</p>
        <ol class="guide-submit-list">
          <li>
            軸（ピボット）を元に，リストを「ピボットより小さい要素」と
            「それ以外の要素」の2つに分ける関数 partition を作成しなさい。
          </li>
          <li>
            上記の補助関数を利用して，本体の quick_sort を完成させなさい。
          </li>
        </ol>
        <pre class="guide-card-code">partition : 'a -&gt; 'a list -&gt; 'a list * 'a list
quick_sort : int list -&gt; int list</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">3. 全体の比較回数カウント版にアップデート</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      1. および 2. で実装したソート関数（本体）をベースに，
      要素の比較回数をカウントする機能を追加しなさい。
      すべての関数は，「これまでの比較回数の合計（int）」と
      「ソート済みのリスト（int list）」のペア（int * int list）を返す形式に改造しなさい。
    </p>

    <ul class="guide-submit-list">
      <li>関数名は，それぞれ末尾に _c をつけること。</li>
      <li>例：exchange_sort_c，merge_sort_c，quick_sort_c</li>
    </ul>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">3-1：単純法の比較回数カウント版</p>
        <p class="guide-card-text">
          課題1で実装した単純ソートアルゴリズムを，比較回数を返す形に改造しなさい。
        </p>
        <ul class="guide-submit-list">
          <li>交換ソートのカウント版：exchange_sort_c</li>
          <li>選択ソートのカウント版：selection_sort_c</li>
          <li>挿入ソートのカウント版：insertion_sort_c</li>
        </ul>
        <pre class="guide-card-code">exchange_sort_c : int list -&gt; int * int list
selection_sort_c : int list -&gt; int * int list
insertion_sort_c : int list -&gt; int * int list</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">3-2：分割統治法の比較回数カウント版</p>
        <p class="guide-card-text">
          課題2で実装した分割統治法ソートアルゴリズムを，比較回数を返す形に改造しなさい。
        </p>
        <ul class="guide-submit-list">
          <li>マージソートのカウント版：merge_sort_c</li>
          <li>クイックソートのカウント版：quick_sort_c</li>
        </ul>
        <pre class="guide-card-code">merge_sort_c : int list -&gt; int * int list
quick_sort_c : int list -&gt; int * int list</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">比較回数の定義に関する注意</p>
        <ul class="guide-submit-list">
          <li>
            カウント対象は，x &gt; y や x &lt;= y などの
            「要素の値同士を比較した回数」のみとします。
          </li>
          <li>
            リストが空かどうかを判定するパターンマッチ
            （match xs with [] -&gt; ... など）の回数はカウントに含めません。
          </li>
          <li>
            分割統治法のヒントとして，再帰呼び出しによって得られた
            「左半分のソートでかかったカウント」と
            「右半分のソートでかかったカウント」を次の処理
            （merge_c や partition_c）へ引き渡し，すべてのカウントが合算されるようにしてください。
          </li>
        </ul>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">4. 実行実験</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      3. で作成したプログラム（選択したすべての関数）を用いて，
      以下の2つの実行実験を行いなさい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">4-1：実験1：要素数による比較回数の変化</p>
        <ul class="guide-submit-list">
          <li>
            ランダムに並んだ要素数 10，50，100 のリストをそれぞれ用意し，
            実装したソート関数を実行して，それぞれの比較回数を計測しなさい。
          </li>
        </ul>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">4-2：実験2：データの初期状態による変化</p>
        <p class="guide-card-text">
          要素数 20 のデータについて，以下の3つのパターンを用意し，
          実装したソート関数を実行して比較回数を計測してください。
        </p>
        <ol class="guide-submit-list">
          <li>整列済みのデータ（例：[1; 2; 3; ... ; 20]）</li>
          <li>逆順に整列済みのデータ（例：[20; 19; 18; ... ; 1]）</li>
          <li>ランダムなデータ</li>
        </ol>
        <p class="guide-card-text">
          注意点：実験1・2で「ランダムなデータ」を比較する際は，各ソート関数に全く同じ並び順のリストを入力して回数を計測してください。
          関数ごとに異なるランダムデータを作ると正確な比較になりません。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">5. 考察（レポート）</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      実行実験の結果をもとに，以下についてレポートにまとめなさい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">5-1：問1（実験結果のまとめ）</p>
        <ul class="guide-submit-list">
          <li>
            実験1および実験2の計測結果を，それぞれ分かりやすい表にまとめなさい。
          </li>
        </ul>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">5-2：問2（データの初期状態とアルゴリズムの特性）</p>
        <ul class="guide-submit-list">
          <li>
            実験2において，データの初期状態（整列済み・逆順・ランダム）の違いによって，
            ご自身が選んだ単純ソートの比較回数はどのように変化したか，
            あるいは変化しなかったか。
            プログラムの構造（条件分岐や処理の打ち切り，データの走査方法など）に着目して，
            その結果になる理由を説明しなさい。
          </li>
        </ul>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">5-3：問3（分割統治法の効率性）</p>
        <ul class="guide-submit-list">
          <li>
            実験1において，要素数が 10 から 100 へと10倍に増えたとき，
            選んだ「単純ソート」の比較回数の増え方と，
            「分割統治法ソート」の比較回数の増え方にはどのような違いが見られますか。
            実験データから読み取れる事実を指摘し，
            なぜ分割統治法が大量のデータを扱う上で有利なのかを述べなさい。
          </li>
        </ul>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">提出方法</h3>

  <div class="guide-card">
    <ul class="guide-submit-list">
      <li>提出方法：LETUS</li>
      <li>提出物：各課題のレポート（LaTeXで作成したPDF）と，作成したプログラムソース（拡張子mlのファイル）</li>
      <li>プログラムを実装する問題においては，「アルゴリズムの説明」と「プログラムの説明」をレポートに記載すること</li>
      <li>提出期限：第3週 2026/6/3（水）13:00</li>
    </ul>
  </div>

  <h3 class="guide-section-title">注意</h3>

  <div class="guide-card week3-guide-caution">
    <p class="guide-card-title">剽窃について</p>
    <p class="guide-card-text">
      すべてのプログラムはOCamlで作成すること。提出されたレポートやプログラムにおいて
      剽窃を発見した場合は，今期の点数は0点になるだけでなく，今期に開講されている
      他の科目の単位が無効になることもあるので注意すること。
    </p>
  </div>
"""

WEEK3_ANSWER_GUIDE_HTML = """
  <p class="guide-intro">
    第2期 第3週の解答例です。配布された解答をもとに掲載しています。
  </p>

  <h3 class="guide-section-title">課題1</h3>
  <div class="guide-card">
    <p class="guide-card-text">
      関数型言語 OCaml を用いて，基本的な単純ソートおよび分割統治法に基づくソートアルゴリズムを実装します。
      さらに，プログラムを改造して「要素の比較回数」を計測・可視化することで，
      データの初期状態や要素数によって各アルゴリズムの処理効率がどのように変化するかを数値的に考察し，
      アルゴリズムの特性への理解を深めることを目的とします。
    </p>
  </div>

  <h3 class="guide-section-title">課題1：単純ソートアルゴリズム</h3>

  <div class="guide-card">
    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">挿入ソート</p>
        <pre class="guide-card-code">let rec insert x = function
  | [] -&gt; [x]
  | y :: ys -&gt;
      if x &lt;= y then
        x :: y :: ys
      else
        y :: insert x ys
;;

let rec insertion_sort = function
  | [] -&gt; []
  | x :: xs -&gt; insert x (insertion_sort xs)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">挿入ソートのカウント版</p>
        <pre class="guide-card-code">let rec insert_c_aux c x = function
  | [] -&gt; (c, [x])
  | y :: ys -&gt;
      if x &lt;= y then
        (c + 1, x :: y :: ys)
      else
        let (c', rest) = insert_c_aux (c + 1) x ys in
        (c', y :: rest)
;;

let rec insertion_sort_c_aux c = function
  | [] -&gt; (c, [])
  | x :: xs -&gt;
      let (c', sorted_xs) = insertion_sort_c_aux c xs in
      insert_c_aux c' x sorted_xs
;;

let insertion_sort_c lst =
  insertion_sort_c_aux 0 lst
;;</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題2：分割統治法ソートアルゴリズム</h3>

  <div class="guide-card">
    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">マージソート</p>
        <pre class="guide-card-code">let split xs =
  let rec loop xs ys zs =
    match xs with
    | [] -&gt; (ys, zs)
    | [x] -&gt; (x :: ys, zs)
    | x :: y :: rest -&gt; loop rest (x :: ys) (y :: zs)
  in
  loop xs [] []
;;

let rec merge xs ys =
  match (xs, ys) with
  | ([], _) -&gt; ys
  | (_, []) -&gt; xs
  | (x :: xs', y :: ys') -&gt;
      if x &lt;= y then
        x :: merge xs' ys
      else
        y :: merge xs ys'
;;

let rec merge_sort = function
  | [] -&gt; []
  | [x] -&gt; [x]
  | xs -&gt;
      let (left, right) = split xs in
      merge (merge_sort left) (merge_sort right)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">マージソートのカウント版</p>
        <pre class="guide-card-code">let rec merge_c_aux c xs ys =
  match (xs, ys) with
  | ([], _) -&gt; (c, ys)
  | (_, []) -&gt; (c, xs)
  | (x :: xs', y :: ys') -&gt;
      if x &lt;= y then
        let (c', rest) = merge_c_aux (c + 1) xs' ys in
        (c', x :: rest)
      else
        let (c', rest) = merge_c_aux (c + 1) xs ys' in
        (c', y :: rest)
;;

let rec merge_sort_c_aux c = function
  | [] -&gt; (c, [])
  | [x] -&gt; (c, [x])
  | xs -&gt;
      let (left, right) = split xs in
      let (c', sorted_l) = merge_sort_c_aux c left in
      let (c'', sorted_r) = merge_sort_c_aux c' right in
      merge_c_aux c'' sorted_l sorted_r
;;

let merge_sort_c lst =
  merge_sort_c_aux 0 lst
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">クイックソート</p>
        <pre class="guide-card-code">let rec partition pivot = function
  | [] -&gt; ([], [])
  | x :: xs -&gt;
      let (small, big) = partition pivot xs in
      if x &lt; pivot then
        (x :: small, big)
      else
        (small, x :: big)
;;

let rec quick_sort = function
  | [] -&gt; []
  | x :: xs -&gt;
      let (small, big) = partition x xs in
      quick_sort small @ (x :: quick_sort big)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">クイックソートのカウント版</p>
        <pre class="guide-card-code">let rec partition_c_aux c pivot = function
  | [] -&gt; (c, [], [])
  | x :: xs -&gt;
      let (c', small, big) = partition_c_aux (c + 1) pivot xs in
      if x &lt; pivot then
        (c', x :: small, big)
      else
        (c', small, x :: big)
;;

let rec quick_sort_c_aux c = function
  | [] -&gt; (c, [])
  | x :: xs -&gt;
      let (c1, small, big) = partition_c_aux c x xs in
      let (c2, sorted_small) = quick_sort_c_aux c1 small in
      let (c3, sorted_big) = quick_sort_c_aux c2 big in
      (c3, sorted_small @ (x :: sorted_big))
;;

let quick_sort_c lst =
  quick_sort_c_aux 0 lst
;;</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題3</h3>
  <div class="guide-card">
    <p class="guide-card-text">
      各ソート関数について，要素同士の比較回数を数えるカウント版を作成する。
      返り値は，「これまでの比較回数の合計」と「ソート済みリスト」のペアとする。
    </p>
  </div>

  <h3 class="guide-section-title">課題4 実行実験1：要素数による比較回数の変化</h3>
  <div class="guide-card">
    <div class="guide-image-wrap">
      <img class="guide-image" src="/week3_answer_table1.png" alt="要素数による比較回数の変化の表">
    </div>
  </div>

  <h3 class="guide-section-title">課題4 実行実験2：初期状態による比較回数の変化</h3>
  <div class="guide-card">
    <div class="guide-image-wrap">
      <img class="guide-image" src="/week3_answer_table2.png" alt="初期状態による比較回数の変化の表">
    </div>
  </div>

  <h3 class="guide-section-title">課題5 考察</h3>
  <div class="guide-card">
    <p class="guide-card-text">
      単純ソートでは，要素数が増えると比較回数が急激に増加する。
      特に交換ソートと選択ソートは，要素数の2乗に比例して増加する。
      挿入ソートは比較回数がやや少ないが，同様に2乗オーダーで増加する。
    </p>
    <p class="guide-card-text">
      一方，マージソートやクイックソートなどの分割統治法ソートは，
      要素数が増えても比較回数の増加が緩やかであり，大量データに対して有利である。
    </p>
    <p class="guide-card-text">
      初期状態の違いに関しては，交換ソートと挿入ソートは整列済みデータに強く，
      選択ソートとマージソートは初期状態の影響をほとんど受けない。
      クイックソートはピボットの取り方によって，整列済みや逆順で最悪に近い挙動を示す。
    </p>
  </div>
"""

WEEK3_AUTO_POINTS = {
    "1": 8,
    "2": 8,
    "3-1": 7,
    "3-2": 7,
}

WEEK3_AUTO_TOTAL_POINTS = 30

def calculate_week3_auto_score(summary):
    score = 0

    for question in summary.get("questions", []):
        question_id = str(question.get("question", ""))
        status = question.get("status")

        if question_id not in WEEK3_AUTO_POINTS:
            continue

        if status == "OK":
            score += WEEK3_AUTO_POINTS[question_id]

    return score

def add_week3_score_badges(html, file_summaries):
    search_start = 0

    for summary in file_summaries:
        score = calculate_week3_auto_score(summary)

        warning_questions = [
            q for q in summary.get("questions", [])
            if q.get("status") == "WARNING"
        ]
        wrong_questions = [
            q for q in summary.get("questions", [])
            if q.get("status") == "NG"
        ]
        error_questions = [
            q for q in summary.get("questions", [])
            if q.get("status") == "ERROR"
        ]

        has_issues = bool(warning_questions or wrong_questions or error_questions)
        status_label = "確認が必要" if has_issues else "全問正解"

        card_top_start = html.find("<div class='card-top'>", search_start)
        if card_top_start == -1:
            break

        card_top_end = html.find("</div>", card_top_start)
        if card_top_end == -1:
            break

        marker = "<span class='status-pill'>{}</span>".format(status_label)

        replacement = (
            "<div class='week3-status-row'>"
            "{}"
            "<span class='week3-point-score'>{}点/{}点</span>"
            "</div>"
        ).format(marker, score, WEEK3_AUTO_TOTAL_POINTS)

        card_top_html = html[card_top_start:card_top_end]
        new_card_top_html = card_top_html.replace(marker, replacement, 1)

        html = (
            html[:card_top_start]
            + new_card_top_html
            + html[card_top_end:]
        )

        search_start = card_top_start + len(new_card_top_html)

    return html

def add_week3_title_style(html):
    extra_css = """
.period-with-week {
  display: inline-flex;
  align-items: flex-end;
  gap: 0;
  letter-spacing: -0.08em;
}

.period-main {
  display: inline-block;
}

.period-week {
  display: inline-block;
  font-size: 0.63em;
  font-weight: 950;
  line-height: 1;
  margin-bottom: 0.10em;
  letter-spacing: -0.06em;
  transform: translateX(-0.04em);
}

.guide-card > .guide-subitems:first-child {
  margin-top: 0;
}

.guide-card-code + .guide-card-title {
  margin-top: 22px;
}

.week3-guide-caution {
  background: rgba(255, 184, 77, 0.18);
  border-color: rgba(217, 139, 0, 0.24);
}

.week3-manual-check-note {
  display: block;
  margin-top: 14px;
  color: rgba(11, 11, 13, 0.76);
  font-size: inherit;
  font-weight: inherit;
  line-height: inherit;
}

.guide-formula {
  margin: 14px 0 16px 0;
  text-align: center;
}

.guide-formula-text {
  display: inline-block;
  padding: 10px 18px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 14px;
  font-family: "Times New Roman", serif;
  font-style: italic;
  font-size: 1.6rem;
  line-height: 1.4;
}

.guide-formula-image-wrap {
  margin: 14px 0 16px;
  text-align: center;
}

.guide-formula-image {
  display: inline-block;
  max-width: min(100%, 360px);
  height: auto;
}

.week3-status-row {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.week3-status-row .status-pill,
.week3-point-score {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 950;
  letter-spacing: 0.04em;
  line-height: 1;
  white-space: nowrap;
}

.week3-point-score {
  background: rgba(11, 11, 13, 0.06);
  color: rgba(11, 11, 13, 0.78);
}

.week3-answer-table-image {
  width: min(100%, 900px);
  max-width: 100%;
}
"""

    return html.replace("</style>", extra_css + "\n</style>")


def replace_task_guide_html(html):
    start_marker = "const taskGuideHtml = `"
    end_marker = "`;\n\n  const criteriaGuideHtml"

    start = html.find(start_marker)

    if start == -1:
        return html

    content_start = start + len(start_marker)
    end = html.find(end_marker, content_start)

    if end == -1:
        return html

    return html[:content_start] + WEEK3_TASK_GUIDE_HTML + html[end:]

def add_answer_guide_menu(html):
    html = html.replace(
        "<button class='guide-menu-item' type='button' data-guide='criteria'>採点基準</button>",
        "<button class='guide-menu-item' type='button' data-guide='criteria'>採点基準</button>"
        "<button class='guide-menu-item' type='button' data-guide='answers'>解答</button>"
    )

    html = html.replace(
        "if (type === 'tasks') {\n"
        "      guideModalTitle.textContent = '課題内容';\n"
        "      guideModalContent.innerHTML = taskGuideHtml;\n"
        "    } else {\n"
        "      guideModalTitle.textContent = '採点基準';\n"
        "      guideModalContent.innerHTML = criteriaGuideHtml;\n"
        "    }",
        "if (type === 'tasks') {\n"
        "      guideModalTitle.textContent = '課題内容';\n"
        "      guideModalContent.innerHTML = taskGuideHtml;\n"
        "    } else if (type === 'answers') {\n"
        "      guideModalTitle.textContent = '解答';\n"
        "      guideModalContent.innerHTML = answerGuideHtml;\n"
        "    } else {\n"
        "      guideModalTitle.textContent = '採点基準';\n"
        "      guideModalContent.innerHTML = criteriaGuideHtml;\n"
        "    }"
    )

    html = html.replace(
        "const criteriaGuideHtml = `",
        "const answerGuideHtml = `"
        + WEEK3_ANSWER_GUIDE_HTML
        + "`;\n\n  const criteriaGuideHtml = `"
    )

    return html

def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace("href='/period'>選択画面へ戻る</a>", "href='/period/2'>選択画面へ戻る</a>")
    html = html.replace("action='/check'", "action='/period/2/week3/check'")
    html = html.replace("Ocaml 1期", "Ocaml 2期")
    html = html.replace("OCaml 1期", "OCaml 2期")
    html = html.replace("1期", "2期")

    html = html.replace(
        "OCaml<br>2期",
        'OCaml<br><span class="period-with-week"><span class="period-main">2期</span><span class="period-week">第3週</span></span>'
    )

    html = replace_task_guide_html(html)
    html = add_answer_guide_menu(html)
    html = add_week3_title_style(html) 

    return html


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = html.replace("採点結果 - Ocaml 1期", "採点結果 - Ocaml 2期 第3週")
    html = html.replace("Ocaml 1期", "Ocaml 2期 第3週")
    html = html.replace("OCaml 1期", "OCaml 2期 第3週")
    html = html.replace("1期", "2期 第3週")

    html = html.replace(
        "採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。",
        "採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。"
        "<span class='week3-manual-check-note'>"
        "課題4-1, 4-2, 5-1, 5-2, 5-3は"
        "自動採点できないため、提出PDFで確認してください。"
        "</span>"
    )

    html = replace_task_guide_html(html)
    html = add_answer_guide_menu(html)
    html = add_week3_score_badges(html, file_summaries)
    html = add_week3_title_style(html)

    return html