"""「GSD に方法論を載せる方法の比べ」を台本で描く。

使い方:
  python3 build_compare_ways.py 元.xlsx 出力.xlsx

- 元.xlsx は「GSDに独自処理を挟む3つの方法」の v4（セルの大きさを測るのと、白紙の土台に使う）。
  v4 の図（目印 v4*）は外し、このファイルの図（目印 cw*）だけを描く。
- 描き方は v4 と同じ部品（build_3ways_v4.py の box・doc・legend など）を使う。
- 4 つの届け方を、同じ骨組み（上にメインの帯、下に GSD のサブエージェント 3 つ、その下に方法論の物）で縦に並べ、
  横の位置をそろえる。並べて見たときに「方法論がどこに入るか」の違いが目で分かるようにする。
- 下に比べの表を 2 つ（届け方 4 案・UI フェーズを使うか）と、今の方針の枠を置く。
"""
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "excel-figure", "scripts"))
from xdraw import Drawing, measure_grid, write_into  # noqa: E402
import build_3ways_v4 as v4  # noqa: E402
from build_3ways_v4 import (GREEN, GREEN_LINE, BLUE, BLUE_LINE, RED, GOLD, OK_GREEN, INK, SUB, UD,  # noqa: E402
                            box, doc, stack, auto_check, need_h)

# 線の種類（凡例と実際の線を同じ表から引く）。v4 の LINES に「文を依頼文に足す」を足し、「読む」の言い方を広げる。
v4.LINES["inject"] = ("2F6DB5", v4.AW, None, "部品（Capability）の文を、メインが受け取って依頼文に足す", "文を渡す")
v4.LINES["read"] = (("tx1", 50, 50), 1.25, "dash", "読んで従う・呼んで使う・見張る（矢印の先の物を読む・流す・見る）", "読む")
line = v4.line
PURPLE_TXT = "7030A0"
MAIN_FILL = ("accent6", 40, 60)   # メインの帯（GSD の物の濃いめ）

# ---- 図の骨組みの位置（4 つの形で同じ） -------------------------------------------------
LX, LW = 34, 300                  # 左の見出しの列
BX, BW = 360, 780                 # メインの帯
AW_, AH = 160, 46                 # サブエージェントの箱
AX = {"planner": 440, "executor": 680, "verifier": 920}   # 箱の左端
ROW_H = 230
KIT_DY = 150                      # 方法論の物の段（行の頭から）
AG_DY = 72                        # サブエージェントの段
BAR_DY = 14
NOTE_X = BX + BW + 24


def paras(text):
    """文を「。」で段落に分ける（1 段落を短く保つ）。"""
    out, cur = [], ""
    for ch in text:
        cur += ch
        if ch == "。":
            out.append(cur)
            cur = ""
    if cur.strip():
        out.append(cur)
    return "\n".join(out)


def cx_of(key):
    return AX[key] + AW_ / 2


def status_tag(d, x, y, text, color):
    d.shape(x, y, 140, 22, "roundRect", fill=None, line=color, lw=1.25, adj=30000,
            text=[[(text, {"bold": True, "color": color})]], size=10, font=UD, ins=(2, 0, 2, 0), name="位置づけ")


def row_head(d, Y, name, how, status, color):
    with d.group("見出し"):
        d.text(LX, Y + 6, LW, 40, [[(p, {"bold": True})] for p in name.split("\n")], size=12.5, font=UD, color="000000", name="形の名前")
        status_tag(d, LX, Y + 50, status, color)
        d.text(LX, Y + 80, LW - 10, ROW_H - 90, paras(how), size=10, font=UD, color=INK, name="一言")


def skeleton(d, Y, agents_text):
    """メインの帯と、サブエージェント 3 つ（起こす矢印つき）。箱を返す。"""
    d.shape(BX, Y + BAR_DY, BW, 26, "rect", fill=MAIN_FILL, line=GREEN_LINE, lw=0.75,
            text=[[("メイン", {"bold": True}), ("：人のコマンドを受け、GSD の手順書を読み、サブエージェントを起こす", {})]],
            size=10, font=UD, color=INK, align="l", ins=(8, 0, 4, 0), name="メインの帯")
    boxes = {}
    for k in ("planner", "executor", "verifier"):
        kind, runs = agents_text[k]
        fill, ln = (v4.BLUE, BLUE_LINE) if kind == "kit" else (GREEN, GREEN_LINE)
        boxes[k] = box(d, AX[k], Y + AG_DY, AW_, AH, runs, fill=fill, line=ln, size=10, name=f"サブエージェント {k}")
        line(d, "spawn", (cx_of(k), Y + BAR_DY + 26), (boxes[k], 0))
    return boxes


def gsd_agent(name, extra=None):
    runs = [[("GSD のサブエージェント", {"size": 8, "color": SUB})], [(name, {"bold": True})]]
    if extra:
        runs.append([(extra, {"size": 9, "color": BLUE_LINE, "bold": True})])
    return ("gsd", runs)


def side_note(d, Y, text):
    d.text(NOTE_X, Y + AG_DY - 4, 330, ROW_H - AG_DY - 8, paras(text), size=10, font=UD, color=INK, name="この形の要点")


# ---- 4 つの形 ------------------------------------------------------------------------
def fig_a(d, Y):
    row_head(d, Y, "A　独自のサブエージェントに差し替える\n（agent_hint）",
             "計画書の agent_hint（起こすサブエージェントの名前を書く欄）に、キットのサブエージェントの名前を書く。"
             "GSD は gsd-executor の代わりにそれを起こす。決まりは、そのサブエージェントの定義に書く。",
             "今のキット v2", SUB)
    b = skeleton(d, Y, {
        "planner": gsd_agent("gsd-planner"),
        "executor": ("kit", [[("キットのサブエージェント", {"size": 8, "color": SUB})], [("sdd-relay-build など", {"bold": True})],
                             [("gsd-executor の代わりに起きる", {"size": 8, "color": SUB})]]),
        "verifier": gsd_agent("gsd-verifier"),
    })
    d.text(AX["executor"] + AW_ / 2 + 6, Y + BAR_DY + 30, 120, 18, [[("agent_hint で選ぶ", {"color": PURPLE_TXT, "bold": True})]],
           size=9, font=UD, wrap="none", name="紫の字")
    child = stack(d, AX["executor"], Y + KIT_DY, AW_, 44,
                  [[("子のサブエージェント", {"bold": True})], [("読み取る・点検する・作る", {"size": 9})]],
                  fill=v4.BLUE, line=BLUE_LINE, size=10, name="子のサブエージェント")
    line(d, "spawn", (b["executor"], 2), (child, 0))
    hook = auto_check(d, AX["verifier"] - 10, Y + KIT_DY, 180, 44, [[("hook", {"bold": True})], [("役ごとに見張る", {"size": 9})]],
                      name="hook")
    line(d, "read", (hook, 1), (child, 3))
    man = doc(d, AX["planner"], Y + KIT_DY, AW_, 50, [[("手引き（skill）", {"bold": True})], "「agent_hint を書け」"],
              name="手引き")
    line(d, "read", (b["planner"], 2), (man, 0))
    side_note(d, Y, "役ごとに道具・見張り・点検役を組める。代わりに、キットの物（サブエージェント 38 体・hook・状態のファイル）が多く、"
                    "GSD の版上げのたびに直す手間がかかる。")
    return man


def fig_b(d, Y):
    row_head(d, Y, "B　役ごとの skill を設定で渡す\n（agent_skills）",
             "設定（.planning/config.json の agent_skills）に、GSD の役ごとに skill のファイルを書く。"
             "GSD の手順書が、サブエージェントの依頼文に skill を入れる。",
             "前の案・補いに使う", SUB)
    b = skeleton(d, Y, {"planner": gsd_agent("gsd-planner"), "executor": gsd_agent("gsd-executor"),
                        "verifier": gsd_agent("gsd-verifier")})
    for k, t in (("planner", "プランの決まり"), ("executor", "作業の決まり"), ("verifier", "確かめの決まり")):
        dd = doc(d, AX[k], Y + KIT_DY, AW_, 46, [[("skill", {"bold": True})], t], name=f"skill {k}")
        line(d, "read", (b[k], 2), (dd, 0))
    cfg = doc(d, BX, Y + KIT_DY, 66, 46, [[("設定", {"bold": True})], "役→skill"], name="設定 agent_skills")
    line(d, "read", (BX + 33, Y + BAR_DY + 26), (cfg, 0))
    side_note(d, Y, "GSD の手順書が skill を必ず入れる作りなので、届き方は確か。確かめの段の中・UI フェーズ・点検役にも入る。"
                    "メインには届かない（メインへは PROJECT.md の 1 行で届ける）。")


def fig_c(d, Y):
    row_head(d, Y, "C　Capability の文を依頼文に足す\n（contributions）",
             "Capability（GSD に部品を足す正式な仕組み）に、役ごとの文を入れておく。拡張点でメインがそれを受け取り、"
             "その役を起こす時に依頼文へ足す。gsd-executor は、作業の前に Capability のスクリプトも必ず呼ぶ。",
             "今の方針", OK_GREEN)
    b = skeleton(d, Y, {"planner": gsd_agent("gsd-planner", "＋足された文"),
                        "executor": gsd_agent("gsd-executor", "＋足された文"),
                        "verifier": gsd_agent("gsd-verifier", "＋足された文")})
    cap = box(d, BX, Y + KIT_DY, 66, 50, [[("Capability", {"bold": True, "size": 9})], [("文・スクリプト", {"size": 8})]],
              fill=v4.BLUE, line=BLUE_LINE, name="Capability")
    line(d, "inject", (cap, 0), (BX + 33, Y + BAR_DY + 26))
    d.text(BX + 72, Y + KIT_DY + 4, 200, 46, [[("拡張点でメインへ渡り、", {"color": BLUE_LINE})],
                                              [("メインが各役の依頼文に足す", {"color": BLUE_LINE})]],
           size=9, font=UD, name="文を渡す道の説明")
    sc = doc(d, AX["executor"] - 10, Y + KIT_DY, AW_ + 20, 58, [[("作業の中身のスクリプト", {"bold": True})], "executor が自分で必ず呼ぶ。失敗で止まる"],
             name="作業の中身のスクリプト")
    line(d, "read", (b["executor"], 2), (sc, 0))
    side_note(d, Y, "決まりを Capability 1 か所に持てる。届くかはメインの読み方しだい（gsd-plan-checker を含む 4 役には毎回届いた）。"
                    "GSD が文を渡す作りになっていない所（確かめの段の中・点検役・UI フェーズ）は、メイン宛ての文か B で補う。")


def fig_d(d, Y):
    row_head(d, Y, "D　Capability の手順で、拡張点に処理を挟む\n（steps）",
             "Capability の steps に skill かサブエージェントの名前を書く。拡張点でメインがそれを流す・起こす。"
             "GSD の役とは別の処理が、決まった所に 1 つ増える。",
             "1 回試した・候補", GOLD)
    skeleton(d, Y, {"planner": gsd_agent("gsd-planner"), "executor": gsd_agent("gsd-executor"),
                    "verifier": gsd_agent("gsd-verifier")})
    gx = (AX["executor"] + AW_ + AX["verifier"]) / 2
    d.text(gx - 110, Y - 6, 220, 18, [[("拡張点（例 execute:post＝作業の後）", {"color": PURPLE_TXT, "bold": True})]], size=9, font=UD,
           align="ctr", wrap="none", name="紫の字")
    step = box(d, gx - 85, Y + KIT_DY, 170, 50,
               [[("挟んだ処理", {"bold": True})], [("skill か独自のサブエージェント", {"size": 9})]],
               fill=v4.BLUE, line=BLUE_LINE, name="挟んだ処理")
    line(d, "spawn", (gx, Y + BAR_DY + 26), (step, 0))
    side_note(d, Y, "挟んだ手順で作業をコミットまでやり切ると、後の gsd-executor はやり直さず、確かめと記録だけをした（1 回）。"
                    "ただし手順の報告は gsd-executor に渡らない。手順は止めない扱いで、流れるかはメインしだい。")


def figure(Y0):
    d = Drawing(tag="cwfig", name="4 つの届け方の図")
    d.text(26, Y0, 1500, 34, "図　方法論が GSD のどこに入るか（4 つの届け方。横の位置をそろえてある）", size=20, font=None,
           color="000000", wrap="none", name="見出し")
    Y = Y0 + 50
    for k, f in enumerate((fig_a, fig_b, fig_c, fig_d)):
        with d.group(f.__name__):
            f(d, Y)
        Y += ROW_H
        if k < 3:
            d.connector((LX, Y - 14), (NOTE_X + 330, Y - 14), color=("tx1", 25, 75), lw=0.75, tail=False, name="区切り線")
    d.text(LX, Y + 4, 1200, 36, "緑の箱 = GSD の物　青の箱 = 方法論（キット）の物　書類の形 = 読む物（skill・設定・スクリプト）\n"
                                "紫の字 = GSD の流れを曲げる設定・拡張点", size=10, font=UD, color="000000",
           name="箱の凡例")
    v4.legend(d, LX, Y + 44, ["spawn", "inject", "read"], [])
    return d, Y + 134


# ---- 比べの表 ----------------------------------------------------------------------------
MARK = {"○": OK_GREEN, "△": GOLD, "✕": RED, "―": SUB}


def cell(t):
    """先頭の ○△✕ を色付きの太字にする。"""
    ps = paras(t).split("\n")
    out = [[(p, {})] for p in ps]
    if t[:1] in MARK:
        out[0] = [(t[0], {"bold": True, "color": MARK[t[0]], "size": 12}), (ps[0][1:], {})]
    return out


def table(d, x0, y, cols, rows, title):
    d.text(26, y, 1500, 30, title, size=18, font=None, color="000000", wrap="none", name="見出し")
    y += 38
    with d.group("一覧表"):
        cx = x0
        for t, w in cols:
            d.shape(cx, y, w, 40, "rect", fill=("bg2",), line="A6A6A6", lw=0.75, text=[[(t, {"bold": True})]], size=10.5,
                    font=UD, color="000000", name="表の見出し")
            cx += w
        y += 40
        for r in rows:
            cells = [[[(r[0], {"bold": True})]]] + [cell(t) for t in r[1:]]
            hs = [need_h(c, w, 10, UD, (6, 3, 4, 3)) for c, (_, w) in zip(cells, cols)]
            rh = max(36, max(hs) + 6)
            cx = x0
            for i, (c, (_, w)) in enumerate(zip(cells, cols)):
                d.shape(cx, y, w, rh, "rect", fill=("bg2",) if i == 0 else "FFFFFF", line="A6A6A6", lw=0.75,
                        text=c, size=10, font=UD, color=INK, align="l", anchor="ctr", ins=(6, 3, 4, 3), name="表のセル")
                cx += w
            y += rh
    return y


WAY_COLS = [("比べる所", 170), ("A　独自のサブエージェントに差し替える（agent_hint）", 330),
            ("B　役ごとの skill を設定で渡す（agent_skills）", 330), ("C　Capability の文を依頼文に足す（contributions）", 330),
            ("D　Capability の手順で、拡張点に処理を挟む（steps）", 330)]
WAY_ROWS = [
    ("置く物の多さ",
     "✕ 多い。キットのサブエージェント 38 体（中継ぎ 14・子 24）、hook、skill、状態のファイル。",
     "○ 少ない。役ごとの skill 数本、設定、PROJECT.md の 1 行、案件のツール。",
     "○ Capability 1 つ（役ごとの文・スクリプト）に寄る。UI の 2 役（gsd-ui-researcher・gsd-ui-checker）の skill と設定は別に置く。",
     "△ Capability に加えて、流す skill・起こすサブエージェントのファイルを setup で置く。案件用の Capability からは置かれない。"),
    ("決まりが GSD の役に届く確かさ",
     "○ 起きるのがキットのサブエージェントなので、定義に書いた決まりは必ず読まれる。",
     "○ 手順書が依頼文に skill を必ず入れる作り。確かめの段の中・UI フェーズ・点検役にも入る。メインには届かない。",
     "△ 4 役（gsd-planner・gsd-plan-checker・gsd-executor・gsd-verifier）には、毎回届いた。ログイン画面の通しの試しまで見た。ただし多くは、手順書の一文をメインがどう読むかに頼る。"
     "GSD が文を渡す作りになっていない所は、メイン宛ての文か B で補う。",
     "△ 作業は挟んだ手順（方法論の skill）がやり切るので、決まりはそこに書ける。"
     "ただし手順は止めない扱いで、流し忘れると決まりを持たない gsd-executor が作る。"),
    ("役ごとに道具・見張り・点検役を変えられるか",
     "○ 役ごとに道具・hook の見張り・点検役・作る⇄確かめるの往復を組める。",
     "△ 役は GSD 標準のまま。往復は GSD の流れ（gsd-executor の中で測り直す・確かめの後に追加の計画書で直すギャップ修正）で代わりにする。"
     "画面を押すのは Playwright の CLI。",
     "△ B と同じ。止めたい所は、gsd-executor が必ず呼ぶ作業の中身のスクリプトで止める（失敗で止まる）。",
     "△ 挟んだ所だけ、独自のサブエージェントで道具を変えられる。gsd-executor の作業の途中には挟めない。"),
    ("GSD の版上げ",
     "✕ GSD の手順書や役が変わるたびに、キットのサブエージェントと台帳の扱いを直す。",
     "○ 使うのは GSD の設定の欄だけ。役の名前が変わった時だけ直す。",
     "△ 正式な拡張の仕組み。ただし届くかは手順書の書き方に頼るので、版を上げたら届くかを確かめ直す。",
     "△ C と同じ。加えて、置いた skill・サブエージェントのファイルの保守が要る。"),
    ("案件を写した時（別のフォルダ・別の PC）",
     "○ ファイルとして案件に入るので、写しても動く。",
     "○ 同じく、写しても動く。",
     "✕ Capability を入れた時の同意が元の場所に結び付くので、写すと黙って無効になる。入れ直しが要る"
     "（無効なら gsd-executor が何も変えずに止まる形にはできる）。",
     "✕ C と同じ。"),
    ("人がすること",
     "○ 最初に setup を 1 回。あとは GSD の入口のコマンドだけ。",
     "○ A と同じ。",
     "△ 最初に setup を 1 回（Capability と設定を入れる）。案件を写したら入れ直す。",
     "△ C と同じ。"),
    ("実機で確かめたか",
     "○ キット v2 として、実機の試しを重ねてきた。",
     "○ ログイン画面で、修正ループまで回った。",
     "○ ログイン画面の通し（Opus・Sonnet）で、4 役に毎回届いた。確かめの段の中への手当ても届いた。",
     "△ 1 回（Sonnet）。手順の子がコミットまでやり切り、gsd-executor は 1 分で記録だけを書いた。手順の報告が SUMMARY に渡らない穴が見えた。"),
    ("今の位置づけ",
     "今のキット v2 の形。独自のサブエージェントを足さない形が理想なので、次の形では離れる。",
     "前の案。C に移った後も、UI の 2 役と、GSD が文を渡す作りになっていない所の補いに使う。",
     "今の方針（利用者の決定）。",
     "候補。作業を方法論の手順で行い、GSD 標準の gsd-executor を記録役にする形。報告の渡し方と、流し忘れへの備えが残る。"),
]

UI_COLS = [("比べる所", 170), ("UI フェーズを使う（/gsd-ui-phase で UI-SPEC.md を作る）", 565),
           ("UI フェーズを使わない（digest だけで作る）", 555)]
UI_ROWS = [
    ("何をするか",
     "gsd-ui-researcher が、digest（モックの SVG から抜いた値）を、GSD の画面の仕様書 UI-SPEC.md に写す。gsd-ui-checker がそれを点検する。",
     "UI-SPEC.md を作らず、計画書から digest を直接読ませる。"),
    ("仕様書",
     "○ GSD 標準の画面の仕様書が残る。GSD はそれを gsd-planner に渡す。人がギャップ修正で決めた値の置き場にもなる。",
     "✕ GSD の仕様書が無い。人が決めた値を、別の所に持つ必要がある。"),
    ("決まりの届け方",
     "△ UI の 2 役には Capability の文が届かない（UI フェーズは拡張点を流さない）ので、agent_skills で渡す。"
     "gsd-ui-checker は字の種類・余白の決まりを持つので、「モックの値は対象外」と skill に書かないと止まる。",
     "○ 決まりを届ける相手が 2 役減る。"),
    ("gsd-executor に仕様が届くか",
     "△ GSD は gsd-executor に UI-SPEC.md を直接渡さない。計画書の read_first（最初に読む物）に書かせて届ける（作業した 9 回とも触れた）。",
     "― 計画書に digest を書かせて届ける。"),
    ("GSD の確かめ",
     "○ UI の安全ゲート（UI-SPEC.md があるかを見る）を通る。確かめの後に UI レビュー（gsd-ui-auditor）が流れ、"
     "アクセシビリティの指摘は出る（外側ループで直した 3 件は挙げなかった）。",
     "✕ 既定の UI の安全ゲートが「UI のファイルを変えたのに UI-SPEC.md が無い」で止める。設定（workflow.ui_safety_gate など）を切る必要がある。"),
    ("時間・手間",
     "△ 画面のフェーズの前に、UI フェーズの分の時間がかかる。",
     "○ その分は無い。"),
    ("実機で確かめたか",
     "○ これまでの試しは、全部この形。",
     "✕ 試していない（安全ゲートの止め方は、GSD のコードで確かめた）。"),
    ("今の位置づけ",
     "使う（今の方針）。",
     "取っていない。"),
]


def tables(Y0):
    d = Drawing(tag="cwtab", name="比べの表")
    y = table(d, 34, Y0, WAY_COLS, WAY_ROWS, "比べの表 1　決まり・処理の届け方（4 案）　○ よい　△ 条件つき　✕ 弱い・できない")
    y = table(d, 34, y + 40, UI_COLS, UI_ROWS, "比べの表 2　UI フェーズを使うか（2 案）")
    with d.group("今の方針"):
        y += 30
        text = [
            [("今の方針: ", {"bold": True}),
             ("届け方は C（Capability の文）を主にし、UI フェーズは使う。", {})],
            [("・UI の 2 役（gsd-ui-researcher・gsd-ui-checker）と、", {})],
            [("　GSD が文を渡す作りになっていない所（確かめの段の中の 3 つ・点検役）は、", {})],
            [("　メイン宛ての文（「起こす時にこの文を貼る」）か B（agent_skills）で補う。", {})],
            [("・止めたい所は、ゲートではなく、gsd-executor が必ず呼ぶ作業の中身のスクリプトと、計画書の受け入れ条件に置く。", {})],
            [("・まだ手当てしていない所: gsd-ui-auditor（確かめの後の UI レビュー）には、決まりが届いていない。", {})],
            [("　/gsd-execute-phase の中でも起きる（そこではメインを宛先に取れない）ので、手当ての道は B。", {})],
        ]
        h = need_h(text, 1490, 11, UD, (10, 6, 8, 6)) + 4
        d.shape(34, y, 1490, h, "rect", fill=("accent2", 20, 80), line=("accent2",), lw=1, text=text, size=11, font=UD,
                color="000000", align="l", anchor="ctr", ins=(10, 6, 8, 6), name="今の方針")
        y += h + 14
        other = [
            [("ほかに考えて、取らなかった案", {"bold": True})],
            [("・gsd-executor から fork の skill で子のサブエージェントを起こす: 動くが、GSD が入口だけになる。", {})],
            [("・Capability のゲートで止める: 機械では止まらず、コマンドを打ち直すと素通りする。", {})],
            [("・Capability にサブエージェントと skill も入れて配る: 案件用の Capability からは置かれない（GSD 側で未実装）。", {})],
            [("・許可の設定（permissions.deny）でモックの画像を止める: 止まるが、方法論の cp・git diff まで止まる。", {})],
        ]
        h2 = need_h(other, 1490, 10, UD, (0, 0, 0, 0)) + 4
        d.text(34, y, 1490, h2, other, size=10, font=UD, color=INK, name="取らなかった案")
        y += h2
    return d, y + 20


def head():
    d = Drawing(tag="cwhead", name="頭書き")
    d.text(26, 0, 1500, 40, "GSD に方法論を載せる方法の比べ", size=26, font=None, color="000000", wrap="none", name="見出し")
    d.text(26, 44, 1500, 40,
           "結論: 決まりは Capability の文を依頼文に足す形（C）を主にし、UI フェーズは使う。\n"
           "GSD が文を渡す作りになっていない所だけ、メイン宛ての文か agent_skills（B）で補う。",
           size=12.5, font=UD, color="000000", wrap="none", name="見出し（結論）")
    d.text(26, 86, 1500, 44,
           "GSD: AI に計画書を書かせてから作らせる道具。　メイン: 人と話し、手順書を読んでサブエージェントを起こす AI。\n"
           "サブエージェント: メインが起こして作業を任せる別の AI。　方法論: モックから画面を作るキットの決まりと道具。\n"
           "Capability: GSD に部品を足す正式な仕組み。　拡張点: GSD の手順書の決まった所（計画の前・作業の後など）。",
           size=10.5, font=UD, color="000000", wrap="none", name="見出し（用語）")
    return d


def strip_all(src, tmp):
    """元の図（目印 xdraw の物すべて）とそのリンクを外した写しを作り、シートの名前を変える。"""
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "xl/drawings/drawing1.xml":
                x = data.decode("utf-8")
                x = re.sub(r'<xdr:twoCellAnchor\b(?:(?!</xdr:twoCellAnchor>).)*?descr="xdraw:\w*".*?</xdr:twoCellAnchor>',
                           "", x, flags=re.S)
                data = x.encode("utf-8")
            elif info.filename == "xl/drawings/_rels/drawing1.xml.rels":
                data = re.sub(r'<Relationship Id="rIdX\w*"[^>]*/>', "", data.decode("utf-8")).encode("utf-8")
            elif info.filename == "xl/workbook.xml":
                x = data.decode("utf-8")
                x = re.sub(r'<sheet name="[^"]*"', '<sheet name="届け方とUIフェーズの比べ"', x, count=1)
                x = re.sub(r"<mc:AlternateContent.*?</mc:AlternateContent>", "", x, flags=re.S)
                data = x.encode("utf-8")
            elif info.filename == "docProps/app.xml":
                data = data.decode("utf-8").replace("理想から今の形まで", "届け方とUIフェーズの比べ").encode("utf-8")
            zout.writestr(info, data)


def build(src, dst):
    grid = measure_grid(src)
    tmp = dst + ".tmp.xlsx"
    strip_all(src, tmp)
    h = head()
    df, bf = figure(146)
    dt, bt = tables(bf + 30)
    write_into(tmp, dst, [h, df, dt], grid=grid, sheet_edit=v4.move_end(grid, bt))
    os.remove(tmp)
    return bf, bt


if __name__ == "__main__":
    bf, bt = build(sys.argv[1], sys.argv[2])
    print(f"書きました: {sys.argv[2]}（図 146〜{bf:.0f}、表 〜{bt:.0f}）")
