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
    第2期 第2週の解答例です。PDFの解答例の内容を，実際の課題番号に合わせて整理しています。
    実装方法は一例であり，同じ動作をする別の実装でも正解になります。
  </p>

  <h3 class="guide-section-title">課題 1：2進数の1の個数</h3>

  <div class="guide-card">
    <p class="guide-card-title">【問1：プログラムの作成】</p>
    <pre class="guide-card-code">let rec count_ones n =
  if n = 0 then
    0
  else
    (n mod 2) + count_ones (n / 2)
;;</pre>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">【問2：アルゴリズムの動作説明】</p>
        <p class="guide-card-text">
          私の学籍番号の下二桁は「00」であるため，数値 100 を用いて count_ones 100 の動作を説明する。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1. 計算の過程（再帰呼び出しの展開）</p>
        <p class="guide-card-text">
          count_ones 100 は，以下のように順次展開され計算される。
        </p>
        <ul class="guide-submit-list">
          <li>count_ones 100 = (100 mod 2) + count_ones 50 = 0 + count_ones 50</li>
          <li>count_ones 50 = (50 mod 2) + count_ones 25 = 0 + count_ones 25</li>
          <li>count_ones 25 = (25 mod 2) + count_ones 12 = 1 + count_ones 12</li>
          <li>count_ones 12 = (12 mod 2) + count_ones 6 = 0 + count_ones 6</li>
          <li>count_ones 6 = (6 mod 2) + count_ones 3 = 0 + count_ones 3</li>
          <li>count_ones 3 = (3 mod 2) + count_ones 1 = 1 + count_ones 1</li>
          <li>count_ones 1 = (1 mod 2) + count_ones 0 = 1 + count_ones 0</li>
          <li>count_ones 0 = 0（ベースケース：再帰の終了）</li>
        </ul>
        <p class="guide-card-text">
          これらを合計すると，0 + 0 + 1 + 0 + 0 + 1 + 1 + 0 = 3 となり，
          最終的な結果として 3 が得られる。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2. 操作の意味</p>
        <p class="guide-card-text">
          n mod 2 の操作は，各ステップにおいて，その時点の数値が奇数（最下位桁が1）か，
          偶数（最下位桁が0）かを判定している。
          100の二進数表記は 1100100 であるが，計算過程の n mod 2 の結果を逆順
          （最後に出たものから順）に並べると 1, 1, 0, 0, 1, 0, 0 となり，
          正しく各桁の値を抽出して「1」である場合のみをカウントに加えていることがわかる。
        </p>
        <p class="guide-card-text">
          n / 2 の操作は，二進数表記における「右シフト」に相当する。
          一の位を n mod 2 で確認した後，n / 2 を行うことでその桁を切り捨て，
          それまで「二の位」だったものを新たな「一の位」として次の再帰に渡している。
          この操作を繰り返すことで，全ての桁を順番に一の位に持ってきて調べることが可能となっている。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 2：べき乗 n<sup>n</sup> の計算</h3>

  <div class="guide-card">
    <p class="guide-card-title">べき乗の2つの関数</p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">値を求める</p>
        <pre class="guide-card-code">let rec power_val n k =
  if k = 0 then 1
  else n * power_val n (k - 1)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">回数を数える</p>
        <pre class="guide-card-code">let rec power_steps n k =
  if k = 0 then 0
  else 1 + power_steps n (k - 1)
;;</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 3：コラッツ予想</h3>

  <div class="guide-card">
    <p class="guide-card-title">コラッツの2つの関数</p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">回数を求める</p>
        <pre class="guide-card-code">let rec collatz_steps n =
  if n = 1 then 0
  else 1 + collatz_steps (if n mod 2 = 0 then n / 2 else 3 * n + 1)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">推移のリストを求める</p>
        <pre class="guide-card-code">let rec collatz_path n =
  if n = 1 then
    [1]
  else
    let next_n = if n mod 2 = 0 then n / 2 else 3 * n + 1 in
    n :: (collatz_path next_n)
;;</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 4：べき乗とコラッツ予想に関する考察</h3>

  <div class="guide-card">
    <p class="guide-card-title">1. 「入力値の大きさ」と「ステップ数」の関係</p>
    <p class="guide-card-text">【調査結果の例】</p>

    <pre class="guide-card-code">n   power_steps   collatz_steps
7   7             16
8   8             3
9   9             19
10  10            6</pre>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">【考察のポイント】</p>
        <p class="guide-card-text">
          べき乗のステップ数は，n の増加に伴って 7, 8, 9, 10 と完全に規則的に増加している。
          これは，再帰の構造が「引数を1ずつ減らす」という単純な形であるため，
          入力値がそのまま計算の手間に比例しているからである。
        </p>
        <p class="guide-card-text">
          一方でコラッツ予想では，n=8 のステップ数が 3 であるのに対し，
          より小さい n=7 が 16 ステップかかるという「逆転現象」が見られた。
          これは，コラッツ予想の再帰構造には偶奇による条件分岐が含まれており，
          値が減少（n/2）したり増大（3n+1）したりするためである。
          この分岐によって，入力値の大小と計算コストが非線形な関係になり，
          実行するまで手間を予測できないという特徴があることがわかった。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2. 数値の「合流」と収束の仕組み</p>
        <p class="guide-card-text">【調査結果の例】</p>

        <pre class="guide-card-code">collatz_path 6 :
[6; 3; 10; 5; 16; 8; 4; 2; 1]

collatz_path 3 :
[3; 10; 5; 16; 8; 4; 2; 1]

collatz_path 9 :
[9; 28; 14; 7; 22; 11; 34; 17; 52; 26; 13; 40; 20;
 10; 5; 16; 8; 4; 2; 1]

collatz_path 7 :
[7; 22; 11; 34; 17; 52; 26; 13; 40; 20; 10; 5; 16;
 8; 4; 2; 1]</pre>

        <p class="guide-card-title">【考察のポイント】</p>
        <p class="guide-card-text">
          各リストを比較すると，collatz_path 6 の2番目の要素以降は collatz_path 3 と完全に一致し，
          collatz_path 9 の4番目以降は collatz_path 7 と完全に一致していることが確認できた。
        </p>
        <p class="guide-card-text">
          これは，コラッツ予想が「現在の値のみによって次の値が決まる」という決定論的なルールであるため，
          一度過去に計算したことがある数値に到達すれば，それ以降は全く同じルート（軌跡）を辿るためである。
          この「合流」という性質があることで，いかに巨大な初期値であっても，
          計算の過程で自分より小さな「既に1へ収束することがわかっている数値」に一度でもぶつかれば，
          連鎖的に1へと吸い込まれていく仕組みになっていると考えられる。
        </p>
      </div>
    </div>
  </div>
"""

def add_week2_title_style(html):
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
    html = add_week2_title_style(html)

    return html