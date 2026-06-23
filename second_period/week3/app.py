# -*- coding: utf-8 -*-

"""Second-period Week3 app scaffold.

This module provides dedicated UI entrypoints for 2期第3週 while reusing the
current 1期 page as an initial clone.
"""


WEEK3_TASK_GUIDE_HTML = """
  <p class="guide-intro">
    第2期 レポート課題 第3週では，ソートアルゴリズムを題材に，
    単純法と分割統治法によるソートをOCamlで実装し，
    比較回数の計測を通してアルゴリズムの性質を考察する。
  </p>

  <h3 class="guide-section-title">課題 1：単純ソートアルゴリズム</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      単純なソートアルゴリズムを1つ以上選択し，OCamlで実装しなさい。
      実装するソートは，以下の候補から選んでよい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">1：単純法によるソート</p>
        <p class="guide-card-text">
          以下のいずれか1つ以上のソートアルゴリズムを実装しなさい。
        </p>
        <ul class="guide-submit-list">
          <li>交換ソート：exchange_sort</li>
          <li>選択ソート：selection_sort</li>
          <li>挿入ソート：insertion_sort</li>
        </ul>
        <pre class="guide-card-code">exchange_sort : int list -&gt; int list
selection_sort : int list -&gt; int list
insertion_sort : int list -&gt; int list</pre>
        <p class="guide-card-text">
          すべてを実装する必要はありません。1つ以上を選択して実装してください。
          ただし，実装した関数については，整数リストを昇順に並べ替えるようにしてください。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 2：分割統治法ソートアルゴリズム</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      分割統治法を用いたソートアルゴリズムを1つ以上選択し，OCamlで実装しなさい。
      分割統治法では，問題を小さな部分問題に分割し，それぞれを解いた結果を統合して全体の解を得ます。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">2：分割統治法によるソート</p>
        <p class="guide-card-text">
          以下のいずれか1つ以上のソートアルゴリズムを実装しなさい。
        </p>
        <ul class="guide-submit-list">
          <li>マージソート：merge_sort</li>
          <li>クイックソート：quick_sort</li>
        </ul>
        <pre class="guide-card-code">merge_sort : int list -&gt; int list
quick_sort : int list -&gt; int list</pre>
        <p class="guide-card-text">
          すべてを実装する必要はありません。1つ以上を選択して実装してください。
          必要に応じて，split，merge，partition などの補助関数を定義してもかまいません。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 3：比較回数カウント版</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      課題1および課題2で実装したソートアルゴリズムについて，
      要素同士の比較回数を数えるように改造しなさい。
      比較回数は，x &gt; y や x &lt;= y など，リスト内の要素同士を比較した回数のみを数えるものとする。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">3-1：単純法の比較回数カウント版</p>
        <p class="guide-card-text">
          課題1で実装した単純ソートアルゴリズムを，比較回数を返す形に改造しなさい。
          返り値は，比較回数とソート済みリストのペアにしてください。
        </p>
        <ul class="guide-submit-list">
          <li>交換ソートのカウント版：exchange_sort_c</li>
          <li>選択ソートのカウント版：selection_sort_c</li>
          <li>挿入ソートのカウント版：insertion_sort_c</li>
        </ul>
        <pre class="guide-card-code">exchange_sort_c : int list -&gt; int * int list
selection_sort_c : int list -&gt; int * int list
insertion_sort_c : int list -&gt; int * int list</pre>
        <p class="guide-card-text">
          返り値は，(比較回数, ソート済みリスト) の順にしてください。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">3-2：分割統治法の比較回数カウント版</p>
        <p class="guide-card-text">
          課題2で実装した分割統治法ソートアルゴリズムを，
          比較回数を返す形に改造しなさい。
        </p>
        <ul class="guide-submit-list">
          <li>マージソートのカウント版：merge_sort_c</li>
          <li>クイックソートのカウント版：quick_sort_c</li>
        </ul>
        <pre class="guide-card-code">merge_sort_c : int list -&gt; int * int list
quick_sort_c : int list -&gt; int * int list</pre>
        <p class="guide-card-text">
          返り値は，(比較回数, ソート済みリスト) の順にしてください。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 4：実行実験</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      作成した比較回数カウント版のソート関数を用いて，実行実験を行いなさい。
      実験結果はレポートにまとめてください。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">4-1：実行実験1</p>
        <p class="guide-card-text">
          要素数を変化させたときに，比較回数がどのように変化するかを調べなさい。
          例えば，要素数 10，50，100 などのリストを用いて実験し，
          各ソートアルゴリズムの比較回数を確認してください。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">4-2：実行実験2</p>
        <p class="guide-card-text">
          リストの初期状態によって，比較回数がどのように変化するかを調べなさい。
          例えば，整列済みリスト，逆順リスト，ランダムなリストなどを用いて比較してください。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 5：実験結果と考察</h3>

  <div class="guide-card">
    <p class="guide-card-text">
      課題4の実験結果を表にまとめ，ソートアルゴリズムごとの特徴を考察しなさい。
    </p>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">5-1：実験結果の表</p>
        <p class="guide-card-text">
          実験で得られた比較回数を表にまとめなさい。
          要素数や初期状態ごとに，比較回数の違いが分かるように整理してください。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">5-2：初期状態による変化の考察</p>
        <p class="guide-card-text">
          整列済み，逆順，ランダムなど，リストの初期状態によって比較回数がどのように変化したかを考察しなさい。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">5-3：単純法と分割統治法の比較</p>
        <p class="guide-card-text">
          単純法と分割統治法を比較し，どのような場合に分割統治法が有利になるかを考察しなさい。
          実験結果とアルゴリズムの特徴を関連づけて説明してください。
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
    第2期 第3週の解答例です。PDFの解答例の内容を，実際の課題番号に合わせて整理しています。
    実装方法は一例であり，同じ動作をする別の実装でも正解になります。
  </p>

  <h3 class="guide-section-title">課題 1：微分</h3>

  <div class="guide-card">
    <p class="guide-card-title">共通で用いる値</p>
    <pre class="guide-card-code">let h = 0.0001;;
let c = 0.0001;;</pre>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">1-1：導関数の定義からの微分係数の計算</p>
        <pre class="guide-card-code">let diff_forward f x =
  (f (x +. h) -. f x) /. h
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-2：中心差分による高精度化</p>
        <pre class="guide-card-code">let diff_central f x =
  (f (x +. h) -. f (x -. h)) /. (2.0 *. h)
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-3：ニュートン法の仕組みの調査</p>
        <p class="guide-card-text">
          1-3はレポート課題のため，自動採点では確認しません。
          ニュートン法の更新式や，f'(x) = 0 を解くために近似値をどのように更新するかを
          提出PDFで確認してください。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-4：再帰による極値の探索</p>
        <pre class="guide-card-code">let rec ext f x =
  let d1 = diff_central f x in
  if abs_float d1 < c then
    (x, f x)
  else
    let d2 = diff_central (diff_central f) x in
    let next_x = x -. d1 /. d2 in
    ext f next_x
;;</pre>
        <p class="guide-card-text">
          この例では，f'(x) = 0 となる点をニュートン法で探索しています。
          diff_central f x で一階微分を近似し，diff_central (diff_central f) x で二階微分を近似しています。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">1-5：精度と速度に関する考察</p>
        <p class="guide-card-text">
          1-5はレポート課題のため，自動採点では確認しません。
          前方差分と中心差分の精度差，h の大きさによる影響，ニュートン法の収束性，
          初期値 x0 の選び方による違いを提出PDFで確認してください。
        </p>
      </div>
    </div>
  </div>

  <h3 class="guide-section-title">課題 2：積分</h3>

  <div class="guide-card">
    <p class="guide-card-title">共通で用いる値</p>
    <pre class="guide-card-code">let dx = 0.0001;;</pre>

    <div class="guide-subitems">
      <div class="guide-subitem">
        <p class="guide-card-title">2-1-1：長方形の面積</p>
        <pre class="guide-card-code">let area_rectangle f x dx =
  f x *. dx
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-1-2：台形の面積</p>
        <pre class="guide-card-code">let area_trapezoid f x dx =
  ((f x +. f (x +. dx)) *. dx) /. 2.0
;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-2：シンプソンの公式の仕組みの調査</p>
        <p class="guide-card-text">
          2-2はレポート課題のため，自動採点では確認しません。
          シンプソンの公式がどのように区間内の関数値を用いて面積を近似するかを
          提出PDFで確認してください。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-3：シンプソンの面積</p>
        <pre class="guide-card-code">let area_simpson f x dx =
  (f x +. 4.0 *. f (x +. dx /. 2.0) +. f (x +. dx)) *. dx /. 6.0
;;</pre>
        <p class="guide-card-text">
          シンプソンの公式では，区間の左端 x，右端 x + dx に加えて，
          中点 x + dx / 2 における関数値も用います。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-4：共通の積分関数</p>
        <pre class="guide-card-code">let rec integral area f a b =
  if a >= b then
    0.0
  else
    area f a dx +. integral area f (a +. dx) b
;;</pre>
        <p class="guide-card-text">
          area に area_rectangle，area_trapezoid，area_simpson のいずれかを渡すことで，
          同じ integral 関数を用いて複数の積分方法を切り替えることができます。
        </p>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-4：実行例</p>
        <pre class="guide-card-code">let f1 x = x;;
let f2 x = x *. x;;

integral area_rectangle f1 0.0 1.0;;
integral area_trapezoid f1 0.0 1.0;;
integral area_simpson f2 0.0 1.0;;</pre>
      </div>

      <div class="guide-subitem">
        <p class="guide-card-title">2-5：精度に関する考察</p>
        <p class="guide-card-text">
          2-5はレポート課題のため，自動採点では確認しません。
          高階関数を用いた設計の利点や，長方形・台形・シンプソンの公式による
          計算結果の精度差を提出PDFで確認してください。
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