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
    第2期 第3週の解答例です。単純ソート，分割統治法ソート，比較回数カウント版，
    実行実験，考察の書き方を課題番号に合わせて整理しています。
    実装方法は一例であり，同じ動作をする別の実装でも正解になります。
  </p>

  <h3 class="guide-section-title">1. 単純ソートアルゴリズムの実装</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      以下は，交換ソート，選択ソート，挿入ソートの実装例です。
      課題では1つ以上を選択して実装すればよいですが，ここでは参考として3つすべてを示します。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">交換ソート：exchange_pass / exchange_sort</p>
        <pre class="guide-card-code">let rec exchange_pass lst =
  match lst with
  | [] -&gt; ([], false)
  | [x] -&gt; ([x], false)
  | x :: y :: rest -&gt;
      if x &gt; y then
        let (tail, _) = exchange_pass (x :: rest) in
        (y :: tail, true)
      else
        let (tail, swapped) = exchange_pass (y :: rest) in
        (x :: tail, swapped)
;;

let rec exchange_sort lst =
  let (lst2, swapped) = exchange_pass lst in
  if swapped then
    exchange_sort lst2
  else
    lst2
;;</pre>
        <p class="guide-card-text">
          exchange_pass は，隣り合う要素を前から順に比較し，順序が逆なら入れ替えます。
          1回でも交換が起きた場合は true を返し，交換が起きなくなるまで exchange_sort が繰り返します。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">選択ソート：select_min / selection_sort</p>
        <pre class="guide-card-code">let rec select_min lst =
  match lst with
  | [] -&gt; failwith "empty"
  | [x] -&gt; (x, [])
  | x :: xs -&gt;
      let (m, rest) = select_min xs in
      if x &lt;= m then
        (x, xs)
      else
        (m, x :: rest)
;;

let rec selection_sort lst =
  match lst with
  | [] -&gt; []
  | _ -&gt;
      let (m, rest) = select_min lst in
      m :: selection_sort rest
;;</pre>
        <p class="guide-card-text">
          select_min は，リスト内の最小値と，その最小値を取り除いた残りのリストを返します。
          selection_sort は，最小値を1つずつ取り出して前から並べることでソートします。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">挿入ソート：insert / insertion_sort</p>
        <pre class="guide-card-code">let rec insert x lst =
  match lst with
  | [] -&gt; [x]
  | y :: ys -&gt;
      if x &lt;= y then
        x :: lst
      else
        y :: insert x ys
;;

let rec insertion_sort lst =
  match lst with
  | [] -&gt; []
  | x :: xs -&gt;
      insert x (insertion_sort xs)
;;</pre>
        <p class="guide-card-text">
          insert は，すでに整列済みのリストに対して，新しい要素 x を正しい位置に挿入します。
          insertion_sort は，残りのリストを先に整列し，そこへ先頭要素を挿入します。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">2. 分割統治法ソートアルゴリズムの実装</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      以下は，マージソートとクイックソートの実装例です。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">マージソート：split / merge / merge_sort</p>
        <pre class="guide-card-code">let rec split lst =
  match lst with
  | [] -&gt; ([], [])
  | [x] -&gt; ([x], [])
  | x :: y :: rest -&gt;
      let (xs, ys) = split rest in
      (x :: xs, y :: ys)
;;

let rec merge xs ys =
  match xs, ys with
  | [], _ -&gt; ys
  | _, [] -&gt; xs
  | x :: xs', y :: ys' -&gt;
      if x &lt;= y then
        x :: merge xs' ys
      else
        y :: merge xs ys'
;;

let rec merge_sort lst =
  match lst with
  | [] -&gt; []
  | [x] -&gt; [x]
  | _ -&gt;
      let (left, right) = split lst in
      merge (merge_sort left) (merge_sort right)
;;</pre>
        <p class="guide-card-text">
          マージソートは，リストを2つに分割し，それぞれを再帰的にソートした後，
          merge によって2つの整列済みリストを1つに統合します。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">クイックソート：partition / quick_sort</p>
        <pre class="guide-card-code">let rec partition pivot lst =
  match lst with
  | [] -&gt; ([], [])
  | x :: xs -&gt;
      let (small, large) = partition pivot xs in
      if x &lt; pivot then
        (x :: small, large)
      else
        (small, x :: large)
;;

let rec quick_sort lst =
  match lst with
  | [] -&gt; []
  | pivot :: rest -&gt;
      let (small, large) = partition pivot rest in
      quick_sort small @ [pivot] @ quick_sort large
;;</pre>
        <p class="guide-card-text">
          クイックソートは，先頭要素をピボットとして選び，
          ピボットより小さい要素とそれ以外に分割してから，再帰的に整列します。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">3. 比較回数カウント版</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      比較回数カウント版では，ソート結果だけでなく，
      要素同士を比較した回数も返します。
      戻り値はすべて int * int list の形にします。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">交換ソートのカウント版</p>
        <pre class="guide-card-code">let rec exchange_pass_c lst =
  match lst with
  | [] -&gt; (0, [], false)
  | [x] -&gt; (0, [x], false)
  | x :: y :: rest -&gt;
      if x &gt; y then
        let (c, tail, _) = exchange_pass_c (x :: rest) in
        (c + 1, y :: tail, true)
      else
        let (c, tail, swapped) = exchange_pass_c (y :: rest) in
        (c + 1, x :: tail, swapped)
;;

let exchange_sort_c lst =
  let rec loop total lst =
    let (c, lst2, swapped) = exchange_pass_c lst in
    if swapped then
      loop (total + c) lst2
    else
      (total + c, lst2)
  in
  loop 0 lst
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">選択ソートのカウント版</p>
        <pre class="guide-card-code">let rec select_min_c lst =
  match lst with
  | [] -&gt; failwith "empty"
  | [x] -&gt; (0, x, [])
  | x :: xs -&gt;
      let (c, m, rest) = select_min_c xs in
      if x &lt;= m then
        (c + 1, x, xs)
      else
        (c + 1, m, x :: rest)
;;

let rec selection_sort_c lst =
  match lst with
  | [] -&gt; (0, [])
  | _ -&gt;
      let (c1, m, rest) = select_min_c lst in
      let (c2, sorted_rest) = selection_sort_c rest in
      (c1 + c2, m :: sorted_rest)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">挿入ソートのカウント版</p>
        <pre class="guide-card-code">let rec insert_c x lst =
  match lst with
  | [] -&gt; (0, [x])
  | y :: ys -&gt;
      if x &lt;= y then
        (1, x :: lst)
      else
        let (c, inserted) = insert_c x ys in
        (c + 1, y :: inserted)
;;

let rec insertion_sort_c lst =
  match lst with
  | [] -&gt; (0, [])
  | x :: xs -&gt;
      let (c1, sorted_xs) = insertion_sort_c xs in
      let (c2, result) = insert_c x sorted_xs in
      (c1 + c2, result)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">マージソートのカウント版</p>
        <pre class="guide-card-code">let rec merge_c xs ys =
  match xs, ys with
  | [], _ -&gt; (0, ys)
  | _, [] -&gt; (0, xs)
  | x :: xs', y :: ys' -&gt;
      if x &lt;= y then
        let (c, merged) = merge_c xs' ys in
        (c + 1, x :: merged)
      else
        let (c, merged) = merge_c xs ys' in
        (c + 1, y :: merged)
;;

let rec merge_sort_c lst =
  match lst with
  | [] -&gt; (0, [])
  | [x] -&gt; (0, [x])
  | _ -&gt;
      let (left, right) = split lst in
      let (c1, sorted_left) = merge_sort_c left in
      let (c2, sorted_right) = merge_sort_c right in
      let (c3, merged) = merge_c sorted_left sorted_right in
      (c1 + c2 + c3, merged)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">クイックソートのカウント版</p>
        <pre class="guide-card-code">let rec partition_c pivot lst =
  match lst with
  | [] -&gt; (0, [], [])
  | x :: xs -&gt;
      let (c, small, large) = partition_c pivot xs in
      if x &lt; pivot then
        (c + 1, x :: small, large)
      else
        (c + 1, small, x :: large)
;;

let rec quick_sort_c lst =
  match lst with
  | [] -&gt; (0, [])
  | pivot :: rest -&gt;
      let (c1, small, large) = partition_c pivot rest in
      let (c2, sorted_small) = quick_sort_c small in
      let (c3, sorted_large) = quick_sort_c large in
      (c1 + c2 + c3, sorted_small @ [pivot] @ sorted_large)
;;</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">4. 実行実験</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      実験では，3で作成した比較回数カウント版の関数を使います。
      ランダムデータを比較する場合は，各ソート関数に同じリストを渡すことが重要です。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">実験1：要素数による比較回数の変化</p>
        <pre class="guide-card-code">let data10 = [7; 2; 9; 1; 5; 3; 8; 4; 10; 6];;

let data50 =
  [32; 7; 45; 12; 3; 28; 50; 19; 41; 6;
   24; 36; 1; 48; 14; 9; 30; 22; 44; 17;
   5; 39; 26; 11; 47; 34; 2; 20; 42; 15;
   8; 29; 37; 4; 49; 18; 31; 23; 46; 13;
   10; 35; 27; 16; 40; 21; 43; 25; 38; 33];;

let data100 =
  [53; 12; 87; 4; 66; 29; 95; 41; 8; 72;
   18; 99; 35; 60; 1; 76; 24; 83; 47; 10;
   91; 31; 68; 55; 14; 100; 37; 6; 80; 22;
   63; 49; 3; 74; 26; 89; 44; 16; 97; 33;
   58; 11; 70; 39; 2; 85; 51; 20; 93; 28;
   64; 7; 78; 45; 17; 96; 34; 59; 13; 82;
   30; 67; 5; 90; 42; 73; 25; 98; 36; 61;
   9; 84; 48; 15; 92; 32; 69; 54; 21; 79;
   40; 65; 19; 88; 46; 71; 27; 94; 38; 57;
   23; 81; 50; 75; 43; 62; 52; 77; 56; 86];;

exchange_sort_c data10;;
merge_sort_c data10;;
quick_sort_c data10;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">実験2：データの初期状態による変化</p>
        <pre class="guide-card-code">let sorted20 =
  [1; 2; 3; 4; 5; 6; 7; 8; 9; 10;
   11; 12; 13; 14; 15; 16; 17; 18; 19; 20];;

let reverse20 =
  [20; 19; 18; 17; 16; 15; 14; 13; 12; 11;
   10; 9; 8; 7; 6; 5; 4; 3; 2; 1];;

let random20 =
  [7; 19; 3; 12; 1; 16; 9; 20; 5; 14;
   2; 18; 11; 6; 15; 4; 17; 8; 13; 10];;

exchange_sort_c sorted20;;
exchange_sort_c reverse20;;
exchange_sort_c random20;;

merge_sort_c sorted20;;
merge_sort_c reverse20;;
merge_sort_c random20;;</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">5. 考察（レポート）</h3>

  <div class="guide-card">
    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">問1：実験結果のまとめ</p>
        <p class="guide-card-text">
          実験1では，要素数10，50，100のそれぞれについて，各ソート関数の比較回数を表にまとめます。
          実験2では，要素数20の整列済み，逆順，ランダムの3種類について比較回数を表にまとめます。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">問2：初期状態による比較回数の違い</p>
        <p class="guide-card-text">
          交換ソートでは，整列済みデータの場合，1回の走査で交換が発生しないため処理がすぐ終了します。
          そのため，比較回数は比較的少なくなります。
          一方，逆順データでは，隣り合う要素のほとんどが逆順であり，
          何度も交換と走査を繰り返すため，比較回数が多くなります。
        </p>
        <p class="guide-card-text">
          選択ソートでは，各段階で残りのリスト全体から最小値を探すため，
          整列済み・逆順・ランダムの違いによって比較回数が大きく変化しにくいです。
          挿入ソートでは，整列済みの場合は早い段階で挿入位置が見つかる一方，
          逆順の場合は奥まで比較が必要になり，比較回数が増えやすくなります。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">問3：分割統治法が大量データに有利な理由</p>
        <p class="guide-card-text">
          単純ソートは，要素数が増えると比較回数が急激に増えやすいです。
          特に交換ソートや選択ソートでは，要素数 n に対しておおよそ n² に近い回数の比較が必要になります。
        </p>
        <p class="guide-card-text">
          一方，マージソートや平均的なクイックソートは，リストを小さく分割してから処理するため，
          比較回数の増え方はおおよそ n log n に近くなります。
          そのため，要素数が10倍になった場合，単純ソートでは比較回数が約100倍に近く増える可能性があるのに対し，
          分割統治法ではそれより緩やかに増加します。
          この違いにより，大量のデータを扱う場合には分割統治法の方が有利であると考えられます。
        </p>
      </div>
    </div>
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