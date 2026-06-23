# -*- coding: utf-8 -*-

"""Second-period Week1 app scaffold.

This module provides dedicated UI entrypoints for 2期第1週 while reusing the
current 1期 page as an initial clone.
"""


WEEK1_TASK_GUIDE_HTML = """
  <p class="guide-intro">
    第2期 レポート課題 第1週では，2進数の1の個数，べき乗，コラッツ予想に関する
    OCamlプログラムを作成し，アルゴリズムの説明や考察をレポートにまとめる。
  </p>

  <h3 class="guide-section-title">課題 1：2進数の1の個数</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      与えられた正の整数 n を二進数で表記したとき，その中に現れる「1」の個数を求める
      関数 count_ones : int -&gt; int を作成しなさい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">1. 実装</p>
        <p class="guide-card-text">
          2で割った商 n / 2 とあまり n mod 2 を用いた再帰関数で実装しなさい。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2. アルゴリズムの動作説明</p>
        <p class="guide-card-text">
          自身の学籍番号の下二桁の数値（ただし，00の場合は100とする）を n としたとき，
          作成した count_ones 関数がどのように実行され，最終的な結果を導き出すのか，
          その過程を詳しく説明しなさい。また，商とあまりの役割についても考察しなさい。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 2：べき乗 n<sup>n</sup> の計算</h3>

  <div class="guide-card">
    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">1. n<sup>n</sup> の値を求める</p>
        <p class="guide-card-text">
          正の整数 n を引数に取り，n の n 乗（n<sup>n</sup>）を計算して返す関数
          power_val : int -&gt; int を作成しなさい。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2. 呼び出し回数を数える</p>
        <p class="guide-card-text">
          再帰関数の呼び出し回数を返す関数 power_steps : int -&gt; int を作成しなさい。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 3：コラッツ予想</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      任意の正の整数 n に対して，以下の操作を繰り返すと最終的に必ず 1 に到達するという
      「コラッツ予想」を題材に，2つの関数を作成しなさい。
    </p>

    <ul class="guide-submit-list">
      <li>n が偶数の場合：n を 2 で割る</li>
      <li>n が奇数の場合：n に 3 を掛けて 1 を足す</li>
    </ul>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">1. ステップ数を求める</p>
        <p class="guide-card-text">
          整数 n を引数に取り，コラッツ予想のルールに従って 1 になるまでの操作回数
          （再帰関数が呼び出される回数）を返す関数 collatz_steps : int -&gt; int を作成しなさい。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2. 推移のリストを求める</p>
        <p class="guide-card-text">
          整数 n を引数に取り，1 に到達するまでの初期値を含む全ての値の推移を順に並べた
          リストを返す関数 collatz_path : int -&gt; int list を作成しなさい。
        </p>
        <pre class="guide-card-code">collatz_path 3 -&gt; [3; 10; 5; 16; 8; 4; 2; 1]</pre>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 4：べき乗とコラッツ予想に関する考察</h3>

  <div class="guide-card">
    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">1. 「入力値の大きさ」と「ステップ数」の関係：べき乗 vs コラッツ予想</p>
        <p class="guide-card-text">
          作成したプログラムを用いて，n = 7, 8, 9, 10 の範囲における「入力値 n」と
          「ステップ数」をそれぞれ調査し，その関係を比較し，気づいた点について考察しなさい。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2. 数値の「合流」と収束の仕組み</p>
        <p class="guide-card-text">
          n = 1〜10 の範囲で collatz_path を実行し，得られたリストを比較し，
          気づいた点について考察しなさい。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">提出方法</h3>

  <div class="guide-card">
    <ul class="guide-submit-list">
      <li>提出方法：LETUS</li>
      <li>提出物：各課題のレポート（LaTeXで作成したPDF）と，作成したプログラムソース（拡張子mlのファイル）</li>
      <li>プログラムを実装する問題においては，「アルゴリズムの説明」と「プログラムの説明」をレポートに記載すること</li>
      <li>提出期限：第1週 2026/5/20（水）13:00</li>
    </ul>
  </div>

  <h3 class="guide-section-title">注意</h3>

  <div class="guide-card week1-guide-caution">
    <p class="guide-card-title">剽窃について</p>
    <p class="guide-card-text">
      すべてのプログラムはOCamlで作成すること。提出されたレポートやプログラムにおいて
      剽窃を発見した場合は，今期の点数は0点になるだけでなく，今期に開講されている
      他の科目の単位が無効になることもあるので注意すること。
    </p>
  </div>
"""

WEEK1_ANSWER_GUIDE_HTML = """
  <p class="guide-intro">
    第2期 第1週の解答例です。PDFの解答例の内容を，実際の課題番号に合わせて整理しています。
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

def add_week1_title_style(html):
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

.week1-guide-caution {
  background: rgba(255, 184, 77, 0.18);
  border-color: rgba(217, 139, 0, 0.24);
}

.week1-manual-check-note {
  display: block;
  margin-top: 14px;
  color: rgba(11, 11, 13, 0.76);
  font-size: inherit;
  font-weight: inherit;
  line-height: inherit;
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

    return html[:content_start] + WEEK1_TASK_GUIDE_HTML + html[end:]

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
        + WEEK1_ANSWER_GUIDE_HTML
        + "`;\n\n  const criteriaGuideHtml = `"
    )

    return html

def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
        html = html.replace("href='/period'>選択画面へ戻る</a>", "href='/period/2'>選択画面へ戻る</a>")
    html = html.replace("action='/check'", "action='/period/2/week1/check'")
    html = html.replace("Ocaml 1期", "Ocaml 2期")
    html = html.replace("OCaml 1期", "OCaml 2期")
    html = html.replace("1期", "2期")

    html = html.replace(
        "OCaml<br>2期",
        'OCaml<br><span class="period-with-week"><span class="period-main">2期</span><span class="period-week">第1週</span></span>'
    )

    html = replace_task_guide_html(html)
    html = add_answer_guide_menu(html)
    html = add_week1_title_style(html) 

    return html


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = html.replace("採点結果 - Ocaml 1期", "採点結果 - Ocaml 2期 第1週")
    html = html.replace("Ocaml 1期", "Ocaml 2期 第1週")
    html = html.replace("OCaml 1期", "OCaml 2期 第1週")
    html = html.replace("1期", "2期 第1週")

    html = html.replace(
        "採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。",
        "採点結果と確認が必要な問を、ファイルごとにまとめて表示しています。"
        "<span class='week1-manual-check-note'>"
        "課題1-2「アルゴリズムの動作説明」と課題4-1,4-2「べき乗とコラッツ予想に関する考察」は"
        "自動採点できないため、提出PDFで確認してください。"
        "</span>"
    )

    html = replace_task_guide_html(html)
    html = add_answer_guide_menu(html)
    html = add_week1_title_style(html)

    return html