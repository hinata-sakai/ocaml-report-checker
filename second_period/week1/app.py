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

.week1-guide-caution {
  background: rgba(255, 184, 77, 0.18);
  border-color: rgba(217, 139, 0, 0.24);
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


def build_index_html(message=""):
    import web_app

    html = web_app.build_index_html(message)
    html = html.replace("action='/check'", "action='/period/2/week1/check'")
    html = html.replace("Ocaml 1期", "Ocaml 2期")
    html = html.replace("OCaml 1期", "OCaml 2期")
    html = html.replace("1期", "2期")

    html = html.replace(
        "OCaml<br>2期",
        'OCaml<br><span class="period-with-week"><span class="period-main">2期</span><span class="period-week">第1週</span></span>'
    )

    html = replace_task_guide_html(html)
    html = add_week1_title_style(html)

    return html


def build_result_html(all_results, file_summaries):
    import web_app

    html = web_app.build_result_html(all_results, file_summaries)
    html = html.replace("採点結果 - Ocaml 1期", "採点結果 - Ocaml 2期 第1週")
    html = html.replace("Ocaml 1期", "Ocaml 2期 第1週")
    html = html.replace("OCaml 1期", "OCaml 2期 第1週")
    html = html.replace("1期", "2期 第1週")

    html = replace_task_guide_html(html)
    html = add_week1_title_style(html)

    return html