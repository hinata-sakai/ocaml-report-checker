# -*- coding: utf-8 -*-

"""Second-period Week2 app scaffold.

This module provides dedicated UI entrypoints for 2期第2週 while reusing the
current 1期 page as an initial clone.
"""


WEEK2_TASK_GUIDE_HTML = """
  <p class="guide-intro">
    第2期 レポート課題 第2週では，数値微分と数値積分を題材に，
    高階関数と再帰を用いたOCamlプログラムを作成し，
    アルゴリズムの説明や考察をレポートにまとめる。
  </p>

  <h3 class="guide-section-title">課題 1：微分</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      関数の微分（微分係数）を，極限をとる代わりに微小な変化量（差分）を用いた
      数値の計算によって近似的に求める手法を「数値微分」といいます。
      本課題では，関数の数値微分を行い，それを利用して関数の極値を再帰的に探索する
      プログラムを実装します。
    </p>

    <p class="guide-card-text">
      プログラムの実装にあたり，微小値 h（数値微分用）および収束の閾値 c（探索の終了判定用）は，
      プログラムの最初でグローバル変数として定義し，各関数の中からそれを参照する形にしなさい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">1-1：導関数の定義からの微分係数の計算</p>
        <p class="guide-card-text">
          関数 f と実数 x を受け取り，値 x における f の微分係数 f'(x) を，
          以下の導関数の定義式を用いて計算する関数 diff_forward を定義しなさい。
        </p>
        <div class="guide-formula-image-wrap">
          <img class="guide-formula-image" src="/week2_diff_forward_formula.png" alt="前方差分による微分係数の近似式">
        </div>
        <pre class="guide-card-code">diff_forward : (float -&gt; float) -&gt; float -&gt; float</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-2：中心差分による高精度化</p>
        <p class="guide-card-text">
          1-1の式は h の大きさによって誤差が生じやすい。
          より正確に微分係数を求めるために，以下の中心差分の式に変形した関数 diff_central を定義しなさい。
        </p>
        <div class="guide-formula-image-wrap">
          <img class="guide-formula-image" src="/week2_diff_central_formula.png" alt="中心差分による微分係数の近似式">
        </div>
        <pre class="guide-card-code">diff_central : (float -&gt; float) -&gt; float -&gt; float</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-3：ニュートン法の仕組みの調査（レポート課題）</p>
        <p class="guide-card-text">
          極値を自動で探索するためのアルゴリズムとして「ニュートン法」があります。
          ニュートン法，特に f'(x) = 0 を解くための更新式の仕組みについて調べ，
          どのような原理で近似値を更新していくのか，数式を用いて分かりやすく説明しなさい。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-4：再帰による極値の探索</p>
        <p class="guide-card-text">
          1-3で調べたニュートン法のアルゴリズムに基づき，関数 f と探索の初期値 x0 を受け取り，
          再帰を用いて f の極値を与える x の値と，その時の極値 f(x) をタプルで返す関数 ext を定義しなさい。
        </p>
        <pre class="guide-card-code">ext : (float -&gt; float) -&gt; float -&gt; (float * float)</pre>
        <ul class="guide-submit-list">
          <li>実数の絶対値を求める関数 abs_float を使ってもかまいません。</li>
          <li>終了条件は，極値に十分到達したと判断できる適切な条件を設定し，探索を終了させなさい。</li>
          <li>極値が存在しない関数や，初期値から極値が離れている場合などの例外的なケースは，本課題では考慮しなくて構いません。</li>
        </ul>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-5：精度と速度に関する考察（レポート課題）</p>
        <p class="guide-card-text">
          実装したプログラムや実行結果について，以下の2点について考察しなさい。
        </p>
        <ul class="guide-submit-list">
          <li>精度：前方差分と中心差分の精度差，およびグローバル変数として定義した h の大小が計算結果に与える影響について考察せよ。</li>
          <li>速度と収束性：ニュートン法の収束の速さ，初期値 x0 の選び方が探索結果や速度に与える影響について考察せよ。</li>
        </ul>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 2：積分</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      関数の積分を，細かく分割した数値の足し合わせによって近似的に計算する手法を
      「数値積分」といいます。
      本課題では，関数の定積分の値を近似計算するプログラムを実装します。
    </p>

    <p class="guide-card-text">
      プログラムの実装にあたり，微小区間の幅を表す実数 dx は，
      プログラムの最初でグローバル変数として定義し，各関数の中からそれを参照する形にしなさい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">2-1：長方形および台形の面積を求める関数の定義</p>
        <p class="guide-card-text">
          関数 f，現在の微小区間の左端の座標 x，および微小幅 dx を受け取り，
          その1区間分の面積を計算する以下の2つの関数を定義しなさい。
        </p>
        <ul class="guide-submit-list">
          <li>長方形として面積を計算する関数 area_rectangle</li>
          <li>台形として面積を計算する関数 area_trapezoid</li>
        </ul>
        <pre class="guide-card-code">area_rectangle : (float -&gt; float) -&gt; float -&gt; float -&gt; float
area_trapezoid : (float -&gt; float) -&gt; float -&gt; float -&gt; float</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-2：シンプソンの公式の仕組みの調査（レポート課題）</p>
        <p class="guide-card-text">
          数値積分の代表的な高精度近似手法として「シンプソンの公式」があります。
          シンプソンの公式，特に1区間分の面積を求める公式の仕組みについて調べ，
          どのような原理で面積を計算するのか，数式を用いて分かりやすく説明しなさい。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-3：シンプソンの面積を求める関数の定義</p>
        <p class="guide-card-text">
          2-2で調査したアルゴリズムに基づき，関数 f，現在の微小区間の左端の座標 x，
          および微小幅 dx を受け取り，その1区間分の面積をシンプソンの公式によって計算する
          関数 area_simpson を定義しなさい。
        </p>
        <p class="guide-card-text">
          （※シンプソンの公式では，区間の中点 x + dx / 2 における関数値が必要になる点に注意しなさい）
        </p>
        <pre class="guide-card-code">area_simpson : (float -&gt; float) -&gt; float -&gt; float -&gt; float</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-4：共通の積分関数（高階関数）の定義と実行</p>
        <p class="guide-card-text">
          1区間分の面積を求める関数，積分したい関数 f，積分の開始位置 a，終了位置 b を引数に取り，
          開始位置 a から座標を dx ずつ進めながら全体の面積の合計を再帰によって計算する
          共通の関数 integral を定義しなさい。
        </p>
        <pre class="guide-card-code">integral : ((float -&gt; float) -&gt; float -&gt; float -&gt; float) -&gt; (float -&gt; float) -&gt; float -&gt; float -&gt; float</pre>
        <p class="guide-card-text">
          また，作成した integral 関数に，これまで定義した3つの面積計算関数
          （長方形・台形・シンプソン）をそれぞれ組み合わせて適切なテスト関数を定義し，
          それぞれの計算結果を求めなさい。
        </p>
        <ul class="guide-submit-list">
          <li>注意点：関数が積分区間内で不連続である場合など，数学的に積分不可能である例外的なケースへの対策は本課題では考慮しなくて構いません。正常に積分可能な関数と区間が与えられるものとして実装しなさい。</li>
        </ul>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-5：精度に関する考察（レポート課題）</p>
        <p class="guide-card-text">
          実装したプログラムや実行結果について，以下の2点について考察しなさい。
        </p>
        <ul class="guide-submit-list">
          <li>高階関数を用いた設計の利点：面積の計算ロジックと，区間を分割して合計するループ処理を分離して高階関数化したことによる，プログラムの構造上・開発上のメリットについて述べよ。</li>
          <li>3つの近似手法による精度差：長方形近似，台形公式，シンプソンの公式の計算結果を，数学的な理論値と比較し，それぞれの手法の精度にどのような違いがあるか，dx の大小が与える影響も交えて考察せよ。</li>
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
      <li>提出期限：第2週 2026/5/27（水）13:00</li>
    </ul>
  </div>

  <h3 class="guide-section-title">注意</h3>

  <div class="guide-card week2-guide-caution">
    <p class="guide-card-title">剽窃について</p>
    <p class="guide-card-text">
      すべてのプログラムはOCamlで作成すること。提出されたレポートやプログラムにおいて
      剽窃を発見した場合は，今期の点数は0点になるだけでなく，今期に開講されている
      他の科目の単位が無効になることもあるので注意すること。
    </p>
  </div>
"""

WEEK2_ANSWER_GUIDE_HTML = """
  <p class="guide-intro">
    第2期 第2週の解答例です。
    数値微分・数値積分の実装例と，配布された解答例PDFのレポート・考察内容を課題番号に合わせて掲載しています。
    実装方法は一例であり，同じ動作をする別の実装でも正解になります。
  </p>

  <h3 class="guide-section-title">課題 1：数値微分</h3>

  <div class="guide-card">
    <p class="guide-card-title">共通で用いる値</p>
    <pre class="guide-card-code">let h = 1e-5;;
let c = 1e-6;;</pre>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">1-1：前方差分による微分係数の計算</p>
        <pre class="guide-card-code">let diff_forward f x =
  (f (x +. h) -. f x) /. h
;;</pre>
        <p class="guide-card-text">
          diff_forward は，x から少しだけ進めた x + h における関数値と f(x) の差を h で割ることで，
          x における微分係数を近似的に求める関数です。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-2：中心差分による微分係数の計算</p>
        <pre class="guide-card-code">let diff_central f x =
  (f (x +. h) -. f (x -. h)) /. (2.0 *. h)
;;</pre>
        <p class="guide-card-text">
          diff_central は，x + h と x - h の両側の関数値を用いて微分係数を近似します。
          前方差分よりも左右対称に近似するため，より高い精度が期待できます。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-3：ニュートン法の仕組み</p>
        <p class="guide-card-text">
          ニュートン法は，方程式 g(x) = 0 の解を近似的に求めるための反復計算アルゴリズムです。
          現在地 x_n における接線が x 軸と交わる点を次の近似値 x_{n+1} として更新します。
        </p>
        <div class="guide-formula">
          <span class="guide-formula-text">x_{n+1} = x_n - g(x_n) / g'(x_n)</span>
        </div>
        <p class="guide-card-text">
          本課題の目的は，関数 f(x) の極値，すなわち f'(x) = 0 となる点を求めることです。
          そのため，g(x) = f'(x) と置き換えることで，極値探索のための更新式は次のようになります。
        </p>
        <div class="guide-formula">
          <span class="guide-formula-text">x_{n+1} = x_n - f'(x_n) / f''(x_n)</span>
        </div>
        <p class="guide-card-text">
          実際のプログラムでは，1階微分 f'(x) を diff_central f x で近似し，
          2階微分 f''(x) を diff_central をさらに適用することで近似します。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-4：再帰による極値の探索</p>
        <pre class="guide-card-code">let rec ext f x0 =
  let f' = diff_central f in
  let f'' = diff_central f' in

  let df = f' x0 in
  if abs_float df &lt; c then
    (x0, f x0)
  else
    let d2f = f'' x0 in
    if abs_float d2f &lt; c then
      failwith "ext failed"
    else
      let next_x = x0 -. df /. d2f in
      ext f next_x
;;</pre>
        <p class="guide-card-text">
          ext は，現在の x0 における傾き f'(x0) が十分に 0 に近くなるまで，
          ニュートン法の更新式に従って再帰的に x を更新します。
          最終的に，極値を与える x とそのときの f(x) をペアで返します。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-4：実行例</p>
        <pre class="guide-card-code">let test_func x =
  x *. x -. 4.0 *. x +. 4.0
;;

ext test_func 0.0;;</pre>
        <p class="guide-card-text">
          この例では，f(x) = x^2 - 4x + 4 を対象にしています。
          この関数は x = 2 で極小値 0 をとるため，初期値 0.0 から探索すると，
          x が 2.0 に近づくことが期待されます。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-5：精度と速度に関する考察</p>
        <p class="guide-card-text">
          テイラー展開を用いた理論上の誤差を比較すると，前方差分の誤差は O(h) であるのに対し，
          中心差分の誤差は O(h^2) となります。
          そのため，中心差分を用いた方がより高い精度で微分係数を近似できます。
        </p>
        <p class="guide-card-text">
          また，数学的には h を 0 に近づけるほど正確になりますが，
          計算機上では h を小さくしすぎると，極めて近い値同士の引き算によって桁落ちが発生し，
          精度が著しく悪化する場合があります。
          そのため，実験的にバランスのよい 1e-5 などの値が選ばれます。
        </p>
        <p class="guide-card-text">
          ニュートン法は，解の近傍では2次収束するため，非常に高速に極値へ近づく特徴があります。
          一方で，初期値 x0 の選び方に強く依存し，極値から遠すぎる初期値を与えた場合や，
          途中で f''(x) が 0 に近くなる場合には，収束しない，または意図しない別の極値へ収束する可能性があります。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 2：数値積分</h3>

  <div class="guide-card">
    <p class="guide-card-title">共通で用いる値</p>
    <pre class="guide-card-code">let dx = 1e-3;;</pre>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">2-1-1：長方形の面積</p>
        <pre class="guide-card-code">let area_rectangle f x dx =
  f x *. dx
;;</pre>
        <p class="guide-card-text">
          長方形近似では，微小区間 [x, x + dx] において，左端 x の関数値 f(x) を高さとみなし，
          幅 dx の長方形の面積として近似します。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-1-2：台形の面積</p>
        <pre class="guide-card-code">let area_trapezoid f x dx =
  (f x +. f (x +. dx)) *. 0.5 *. dx
;;</pre>
        <p class="guide-card-text">
          台形公式では，左端 x と右端 x + dx の関数値を用いて，
          微小区間を台形として近似します。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-2：シンプソンの公式の仕組み</p>
        <p class="guide-card-text">
          長方形近似が関数を定数，台形公式が関数を直線で近似するのに対し，
          シンプソンの公式は関数を放物線，つまり2次式で近似して面積を求める手法です。
        </p>
        <p class="guide-card-text">
          微小区間 [x, x + dx] において，左端 x，中点 x + dx / 2，右端 x + dx の3点を通る
          2次関数を構築し，それを積分することで，1区間あたりの面積を求めます。
        </p>
        <div class="guide-formula">
          <span class="guide-formula-text">I ≈ dx / 6 [ f(x) + 4f(x + dx / 2) + f(x + dx) ]</span>
        </div>
        <p class="guide-card-text">
          区間内を放物線で滑らかに近似するため，長方形近似や台形公式に比べて，
          元の関数のカーブに高い精度で追従できるという特徴があります。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-3：シンプソンの面積</p>
        <pre class="guide-card-code">let area_simpson f x dx =
  let mid = x +. dx *. 0.5 in
  (dx /. 6.0) *. (f x +. 4.0 *. f mid +. f (x +. dx))
;;</pre>
        <p class="guide-card-text">
          area_simpson は，区間の左端，中央，右端における関数値を用いて，
          シンプソンの公式に基づく1区間分の面積を返します。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-4：共通の積分関数</p>
        <pre class="guide-card-code">let integral area_method f a b =
  let rec iter x acc =
    if x &gt;= b then
      acc
    else
      let current_area = area_method f x dx in
      iter (x +. dx) (acc +. current_area)
  in
  iter a 0.0
;;</pre>
        <p class="guide-card-text">
          integral は，1区間分の面積を求める関数 area_method を引数として受け取ります。
          そのため，area_rectangle，area_trapezoid，area_simpson を渡し替えるだけで，
          同じ再帰処理を使って異なる数値積分手法を実行できます。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-4：実行例</p>
        <pre class="guide-card-code">let test_func x =
  x *. x
;;

let res_rect =
  integral area_rectangle test_func 0.0 1.0
;;

let res_trap =
  integral area_trapezoid test_func 0.0 1.0
;;

let res_simp =
  integral area_simpson test_func 0.0 1.0
;;</pre>
        <p class="guide-card-text">
          f(x) = x^2 を区間 [0, 1] で積分した場合，理論値は 1 / 3 ≒ 0.333333 です。
          この値と各近似手法の結果を比較することで，精度の違いを確認できます。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-5：高階関数を用いた設計の利点</p>
        <p class="guide-card-text">
          今回の設計では，「積分を行うための共通の枠組み」と，
          「具体的な面積の計算手法」を分離しています。
          前者を integral として抽象化し，後者を area_rectangle，area_trapezoid，area_simpson として定義しています。
        </p>
        <p class="guide-card-text">
          この設計の最大のメリットは，コードの再利用性と拡張性が高いことです。
          新しい数値積分アルゴリズムを追加する場合でも，再帰の部分を書き直す必要はありません。
          1区間分の面積を求める関数を新しく定義し，それを integral に渡すだけで対応できます。
          そのため，バグが混入しにくく，保守しやすいプログラムになります。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-5：3つの近似手法による精度差</p>
        <p class="guide-card-text">
          関数 f(x) = x^2 を区間 [0, 1] で定積分した場合，手計算による理論値は 1 / 3 ≒ 0.333333 です。
          dx = 1e-3 で実験すると，長方形近似では誤差が最も大きく，
          台形公式では理論値にかなり近い値が得られます。
          シンプソンの公式では，理論値とほぼ一致する，あるいは計算機誤差レベルの非常に小さな差に収まります。
        </p>
        <p class="guide-card-text">
          理論上の誤差は，長方形近似が O(dx)，台形公式が O(dx^2)，
          シンプソンの公式が O(dx^4) となります。
          そのため，シンプソンの公式は dx が比較的大きくても高精度な値を得やすい手法です。
        </p>
        <p class="guide-card-text">
          ただし，dx を小さくしすぎると，再帰回数が増えて処理時間が伸びます。
          また，非常に小さな実数を大量に足し合わせることで丸め誤差が蓄積し，
          逆に全体の精度を損なう恐れもあります。
        </p>
      </div>
    </div>
  </div>
"""

WEEK2_AUTO_POINTS = {
    "1-1": 3,
    "1-2": 3,
    "1-4": 6,
    "2-1-1": 2,
    "2-1-2": 2,
    "2-3": 6,
    "2-4": 6,
}

WEEK2_AUTO_TOTAL_POINTS = sum(WEEK2_AUTO_POINTS.values())

def calculate_week2_auto_score(summary):
    score = 0

    for question in summary.get("questions", []):
        question_id = str(question.get("question", ""))
        status = question.get("status")

        if question_id not in WEEK2_AUTO_POINTS:
            continue

        if status == "OK":
            score += WEEK2_AUTO_POINTS[question_id]

    return score

def add_week2_score_badges(html, file_summaries):
    search_start = 0

    for summary in file_summaries:
        score = calculate_week2_auto_score(summary)

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
            "<div class='week2-status-row'>"
            "{}"
            "<span class='week2-point-score'>{}点/{}点</span>"
            "</div>"
        ).format(marker, score, WEEK2_AUTO_TOTAL_POINTS)

        card_top_html = html[card_top_start:card_top_end]
        new_card_top_html = card_top_html.replace(marker, replacement, 1)

        html = (
            html[:card_top_start]
            + new_card_top_html
            + html[card_top_end:]
        )

        search_start = card_top_start + len(new_card_top_html)

    return html

def add_week2_title_style(html):
    extra_css = """
.period-with-week {
  display: inline-flex;
  align-items: flex-end;
  gap: 0.04em;
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
  transform: none;
}

.guide-card > .guide-subitems:first-child {
  margin-top: 0;
}

.guide-card-code + .guide-card-title {
  margin-top: 22px;
}

.week2-guide-caution {
  background: rgba(255, 184, 77, 0.18);
  border-color: rgba(217, 139, 0, 0.24);
}

.week2-manual-check-note {
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

.week2-status-row {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.week2-status-row .status-pill,
.week2-point-score {
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

.week2-point-score {
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

    return html[:content_start] + WEEK2_TASK_GUIDE_HTML + html[end:]

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
        + WEEK2_ANSWER_GUIDE_HTML
        + "`;\n\n  const criteriaGuideHtml = `"
    )

    return html

def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace("href='/period'>選択画面へ戻る</a>", "href='/period/2'>選択画面へ戻る</a>")
    html = html.replace("action='/check'", "action='/period/2/week2/check'")
    html = html.replace("Ocaml 1期", "Ocaml 2期")
    html = html.replace("OCaml 1期", "OCaml 2期")
    html = html.replace("1期", "2期")

    html = html.replace(
        "OCaml<br>2期",
        'OCaml<br><span class="period-with-week"><span class="period-main">2期</span><span class="period-week">第2週</span></span>'
    )

    html = replace_task_guide_html(html)
    html = add_answer_guide_menu(html)
    html = add_week2_title_style(html) 

    return html


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = html.replace("採点結果 - Ocaml 1期", "採点結果 - Ocaml 2期 第2週")
    html = html.replace("Ocaml 1期", "Ocaml 2期 第2週")
    html = html.replace("OCaml 1期", "OCaml 2期 第2週")
    html = html.replace("1期", "2期 第2週")

    html = html.replace(
        "採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。",
        "採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。"
        "<span class='week2-manual-check-note'>"
        "課題1-3, 1-5-1, 1-5-2, 2-2, 2-5-1, 2-5-2は"
        "自動採点できないため、提出PDFで確認してください。"
        "</span>"
    )

    html = replace_task_guide_html(html)
    html = add_answer_guide_menu(html)
    html = add_week2_score_badges(html, file_summaries)
    html = add_week2_title_style(html)

    return html