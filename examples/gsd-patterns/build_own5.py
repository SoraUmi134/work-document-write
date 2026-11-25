"""「GSD で自作のサブエージェントを起動する 5 つの方法」（GSD 1.23.0 の実機の結果）を描く。

使い方:
  python3 build_own5.py <手本の xlsx（GSDに独自処理を挟む3つの方法_v4.xlsx）> <出力の xlsx>

- 手本の xlsx のシートと列・行の大きさを使い、手本の図は外して、この台本の図（目印 own5*）を描く。
- 部品（色・字・箱・吹き出し・凡例・表のセル）は build_3ways_v4.py の物をそのまま使う。
- 図の中の事実は、検証用の案件のコピー（trials-v2/own-*）で GSD 1.23.0 を実際に実行した結果だけを書く。
  仕様（GSD の文書）は参考リンクにとどめ、仕様と実際が違った所はそう書く。
- 吹き出しの線は、図の枠の右端に置いた番号へ引く（線が図の中の箱を横切らないように）。
- 表の中身・結論・一部の文は own5_data.py に置く。
"""
import importlib.util
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("v4", os.path.join(HERE, "build_3ways_v4.py"))
v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4)
Drawing, measure_grid, write_into = v4.Drawing, v4.measure_grid, v4.write_into
GREEN, GREEN_LINE, BLUE, BLUE_LINE, PURPLE = v4.GREEN, v4.GREEN_LINE, v4.BLUE, v4.BLUE_LINE, v4.PURPLE
RED, GOLD, OK_GREEN, INK, SUB, UD, YU, AW = v4.RED, v4.GOLD, v4.OK_GREEN, v4.INK, v4.SUB, v4.UD, v4.YU, v4.AW
LINES = v4.LINES
box, doc, ghost, line, badge, note, need_h = v4.box, v4.doc, v4.ghost, v4.line, v4.badge, v4.note, v4.need_h
place_problems = v4.place_problems
LEGEND_TEXT = {
    "colors": "緑の箱 = GSD の物　青の箱 = 自作の物（キットが用意する）",
    "doc": "書類の形 = 読むだけの物（setup が配置する物・設定）",
    "ghost": "灰の点線の箱 = 起動されなかった物・できない所",
    "graycross": "灰の ✕ = 既定のロールが起動されなかった",
    "red": "赤い丸の数字 = できない所（数字は右の問題点の番号）",
    "gold": "金の丸の数字 = 条件つき・毎回ではない所（数字は右の問題点の番号）",
    "callout": "淡い黄の吹き出し = 問題点（線の先の右端の番号が、図の中の同じ番号）",
    "purple": "紫の字 = GSD の動きを変える設定・指示",
}


def legend(d, x, y, lines, shapes):
    """build_3ways_v4 の凡例と同じ見た目で、この図の言葉に合わせた物。"""
    with d.group("凡例"):
        d.text(x, y, 120, 18, [[("凡例", {"bold": True})]], size=10, font=UD, color="000000", wrap="none",
               name="凡例の見出し")
        yy = y + 20
        for k in lines:
            color, lw, dash, label, _ = LINES[k]
            if k == "spawn":
                label = "サブエージェントを起動する"
            elif k == "read":
                label = "読む（矢印の先の物を読む）"
            elif k == "write":
                label = "計画書を書く"
            elif k == "boundary":
                label = "コマンドごとの境目（その上のコマンドで動く範囲）"
            d.connector((x, yy + 9), (x + 34, yy + 9), color=color, lw=lw, dash=dash, name="凡例の線")
            d.text(x + 40, yy, 280, 18, label, size=10, font=UD, color="000000", wrap="none", name="凡例の文")
            yy += 19
        yy += 4
        for k in shapes:
            if k == "colors":
                d.shape(x, yy + 2, 16, 14, "roundRect", fill=GREEN, line=GREEN_LINE, adj=8000, name="凡例の色")
                d.shape(x + 18, yy + 2, 16, 14, "roundRect", fill=BLUE, line=BLUE_LINE, adj=8000, name="凡例の色")
            elif k == "doc":
                d.shape(x, yy + 1, 34, 16, "flowChartDocument", fill=BLUE, line=BLUE_LINE, dash="dash", name="凡例の書類")
            elif k == "ghost":
                d.shape(x, yy + 1, 34, 16, "roundRect", fill=v4.GHOST_FILL, line=v4.GHOST_LINE, dash="dash", adj=8000,
                        name="凡例の要る物")
            elif k == "graycross":
                d.cross(x + 17, yy + 9, size=16, color=("tx1", 50, 50))
            elif k == "red":
                badge(d, x + 10, yy + 9, "N", size=18)
            elif k == "gold":
                badge(d, x + 10, yy + 9, "N", gold=True, size=18)
            elif k == "callout":
                d.shape(x, yy + 1, 34, 16, "rect", fill=v4.CALLOUT_FILL, line=v4.CALLOUT_LINE, lw=1, name="凡例の吹き出し")
            elif k == "purple":
                d.text(x, yy, 36, 18, "紫の字", size=9, font=UD, color=PURPLE, wrap="none", name="凡例の紫")
            d.text(x + 40, yy, 280, 18, LEGEND_TEXT[k], size=10, font=UD, color="000000", wrap="none", name="凡例の文")
            yy += 20
    return yy

GH = "https://github.com/open-gsd/gsd-core"
v4.L.update({
    "hint123": GH + "/blob/v1.23.0/docs/reference/plan-md.md#per-plan-executor-routing",
    "routing123": GH + "/blob/v1.23.0/gsd-core/workflows/execute-phase/steps/per-plan-executor-routing.md",
    "steps123": GH + "/blob/v1.23.0/docs/reference/capability-manifest.md#steps",
    "points123": GH + "/blob/v1.23.0/docs/reference/capability-manifest.md#valid-point-values",
    "agents123": GH + "/blob/v1.23.0/docs/reference/capability-manifest.md#agents",
    "5738": GH + "/issues/5738",
    "toggles123": GH + "/blob/v1.23.0/docs/CONFIGURATION.md#workflow-toggles",
    "skills123": GH + "/blob/v1.23.0/docs/CONFIGURATION.md#agent-skills-injection",
})


def split_para(t, limit):
    """長い文を、句点（。）で段落に分ける。それでも長い所は読点（、）で分ける。"""
    out = []
    for s in re.findall(r"[^。]+。?", t):
        while len(s) > limit:
            cut = max(s.rfind("、", 0, limit), s.rfind("・", 0, limit), s.rfind("）", 0, limit))
            if cut < limit // 3:
                break
            out.append(s[:cut + 1])
            s = s[cut + 1:]
        if s.strip():
            out.append(s)
    return out


def PP(text, red=None):
    """吹き出しの段落の list を作る。text は濃い字、red は赤（何が困るか）。長い文は段落に分ける。"""
    paras = [[(p, {"color": INK})] for p in split_para(text, 90)] if text else []
    if red:
        paras += [[(p, {"color": RED})] for p in split_para(red, 90)]
    return paras


def cell(text):
    """表のセルの文。長い文は段落に分ける（1 段落 70 字まで）。"""
    return split_para(text, 70)


# ---- 骨組み（コマンド 5 つ） ----------------------------------------------------------
X0 = 372
CMDS = [(X0, 150, "/gsd-new-project", "案件を始める"), (X0 + 154, 122, "/gsd-discuss-phase", "決め事を相談"),
        (X0 + 280, 290, "/gsd-plan-phase", "計画書を書く"), (X0 + 574, 380, "/gsd-execute-phase", "実装する"),
        (X0 + 958, 211, "/gsd-verify-work", "人が確認する")]
BOUNDS = tuple(c[0] - 2 for c in CMDS[1:])
POINTS = [[], ["discuss:pre", "discuss:post"], ["plan:pre", "plan:post"],
          ["execute:pre", "wave:pre", "wave:post", "execute:post", "verify:post"], ["verify:pre", "verify:post"]]
FX, FW = 34, 1517            # 図の枠
EDGE = FX + FW               # 枠の右端（吹き出しの線の先の番号を置く）
T_ = {}                      # own5_data が入れる文


def verdict_badge(d, x, y, label, color):
    w = 15 * len(label) + 24
    d.shape(x, y, w, 26, "roundRect", fill=color, line=None, adj=20000,
            text=[[(label, {"bold": True, "color": "FFFFFF"})]], size=13, font=UD, ins=(0, 0, 0, 0), name="見出し（評価）")
    return x + w


def skeleton(d, Y0, title, verdict, vcolor, why, fired=None):
    d.text(26, Y0, 1500, 44, title, size=28, font=None, color="000000", wrap="none", name="見出し")
    x = verdict_badge(d, 34, Y0 + 47, verdict, vcolor)
    d.text(x + 10, Y0 + 48, 1400, 26, why, size=14, font=UD, color="000000", wrap="none", name="見出し（理由）")
    T = Y0 + 82
    cmds = []
    for cx, w, a, b in CMDS:
        cmds.append(d.shape(cx, T + 20, w, 61, "homePlate", fill=GREEN, line=GREEN_LINE, lw=0.75, adj=18000,
                            text=[[(a, {"bold": True})], b], size=10.5, font=YU, color="000000", ins=(2, 0, 9, 0), name=a))
    d.text(78, T + 78, 150, 24, "人（入力するコマンド）", size=12, font=None, color="000000", wrap="none", name="文字")
    d.connector((56, T + 102), (EDGE - 12, T + 102), color="A6A6A6", lw=1, tail=False, name="区切り線")
    d.text(78, T + 104, 80, 24, "裏側の処理", size=12, font=None, color="000000", wrap="none", name="文字")
    main = d.shape(X0, T + 143, CMDS[-1][0] + CMDS[-1][1] - X0, 41, "roundRect", fill=GREEN, line=GREEN_LINE, adj=8000,
                   text="メインエージェント（人と話す AI。コマンドの手順書どおりにサブエージェントを起動する）",
                   size=13, font=UD, color=INK, name="メインエージェント")
    MB = T + 184
    for c in cmds:
        line(d, "cmd", (c, 2), (c.site(2)[0], T + 143))
    with d.group("ループポイントの札"):
        for (cx, w, a, _), pts in zip(CMDS, POINTS):
            if not pts:
                d.text(cx + 2, MB + 9, w - 4, 18, "ループポイント無し", size=8.5, font=UD, color=SUB, align="ctr",
                       wrap="none", name="ポイント無し")
                continue
            tw = (w - 8 - 3 * (len(pts) - 1)) / len(pts)
            for k, p in enumerate(pts):
                on = fired is not None and p in fired
                d.shape(cx + 4 + k * (tw + 3), MB + 6, tw, 22, "rect", fill=("accent1", 20, 80) if on else "FFFFFF",
                        line=BLUE_LINE if on else "A6A6A6", lw=0.75, text=p, size=8, font=UD,
                        color=INK if on else SUB, ins=(1, 0, 1, 0), name=f"ポイント {p}")
    return T, main, MB


def finish(d, T, bottom):
    """枠とコマンドごとの境目を、中身の高さに合わせて描く。"""
    FH = bottom - T + 20
    d.shape(FX, T, FW, FH, "rect", fill=None, line=("tx2",), lw=2.25, name="枠")
    with d.group("コマンドごとの境目"):
        for bx in BOUNDS:
            line(d, "boundary", (bx, T + 6), (bx, T + 141), tail=False)
            line(d, "boundary", (bx, T + 186), (bx, T + FH - 6), tail=False)
    return T + FH


def col_x(i):
    return CMDS[i][0], CMDS[i][1]


def _h(lines, w):
    return need_h(lines, w, 10, YU, (4, 2, 4, 2)) + 4


def gsd_box(d, x, y, w, name, sub=None):
    lines = [[("GSDのサブエージェント", {"bold": True})], name] + ([sub] if sub else [])
    return box(d, x, y, w, _h(lines, w), lines, name=name)


def own_box(d, x, y, w, name, sub=None):
    lines = [[("自作のサブエージェント", {"bold": True})], [(name, {"color": PURPLE})]] + (sub.split("\n") if sub else [])
    return box(d, x, y, w, _h(lines, w), lines, fill=BLUE, line=BLUE_LINE, name=name)


def off_box(d, x, y, w, name, sub="（起動されなかった）"):
    lines = [name, sub]
    g = ghost(d, x, y, w, _h(lines, w), lines, name=f"{name}（起動されない）")
    d.cross(x + w - 9, y + 9, size=13, color=("tx1", 50, 50))
    return g


def cannot_box(d, x, y, w, text, n, gold=False):
    g = ghost(d, x, y, w, _h(text, w), text, name="できない所")
    badge(d, x + w - 4, y + 4, n, gold=gold)
    return g


def spawn_tree(d, trunk_x, top, boxes):
    if not boxes:
        return
    color = LINES["spawn"][0]
    d.connector((trunk_x, top), (trunk_x, boxes[-1].cy), color=color, lw=AW, tail=False, name="起こす矢印の幹")
    for b in boxes:
        d.connector((trunk_x, b.cy), (b, 1), color=color, lw=AW, name="起こす矢印の枝")


def setup_doc(d, MB, lines):
    h = need_h(lines, 300, 9.5, YU, (6, 2, 4, 2)) + 22
    return doc(d, 52, MB + 40, 304, h, lines, size=9.5, name="setup が配置する物", align="l")


SETUP_HEAD = [("setup（キット側の作業。案件ごとに 1 回）が配置する物", {"bold": True})]


def edge_items(d, items):
    """吹き出しの線の先を、枠の右端の番号にする。items の at は、話の対象の y。
    番号どうしが重ならないよう、上から順に 24pt 以上あける。吹き出しは番号の上から順に並べる。"""
    items = sorted(items, key=lambda it: it["at"])
    last = -1e9
    for it in items:
        y = max(it.pop("at"), last + 24)
        for k, (n, g) in enumerate(zip(it["nums"], it["gold"])):
            badge(d, EDGE + 14, y + 22 * k, n, gold=g, size=18)
        last = y + 22 * (len(it["nums"]) - 1)
        it["to"] = (EDGE + 23, y)
    return items


def item(nums, gold, head, body, at, keys):
    return dict(nums=nums, gold=gold, head=head, body=body, at=at, keys=keys)


# ---- 図 A: agent_hint ---------------------------------------------------------------
def figA(Y0):
    d = Drawing(tag="own5A", name="図A agent_hint")
    T, main, MB = skeleton(d, Y0, "図A　計画書の agent_hint で、executor を自作に置き換える", "executor だけ", GOLD,
                           "execute-phase の executor は置き換わった。ほかのロールと /gsd-quick では置き換わらなかった")
    sd = setup_doc(d, MB, [SETUP_HEAD,
                           "・.claude/agents/own-a-executor.md",
                           [("（gsd-executor.md のコピーに、名前と手順を追記した物）", {"color": SUB})],
                           "・planner への指示（Capability の contribution）",
                           [("  計画書の frontmatter に agent_hint: own-a-executor", {"color": PURPLE})]])
    line(d, "read", (main, 1), (sd, 0))
    y0 = MB + 44
    x, w = col_x(2)
    pl = gsd_box(d, x + 18, y0, 130, "gsd-planner", "（計画立案）")
    card = box(d, x + 160, y0, w - 166, 74, [[("計画書 PLAN.md", {"bold": True})], [("agent_hint:", {"color": PURPLE})],
                                               [("own-a-executor", {"color": PURPLE})]], name="計画書")
    line(d, "write", (pl, 3), (card, 1))
    spawn_tree(d, x + 9, MB + 30, [pl])
    x, w = col_x(3)
    oa = own_box(d, x + 18, y0, 190, "own-a-executor", "gsd-executor の代わりに起動。コミットと SUMMARY.md まで GSD の約束どおり")
    gx = off_box(d, x + 18, oa.y + oa.h + 16, 190, "gsd-executor")
    spawn_tree(d, x + 9, MB + 30, [oa])
    rv = gsd_box(d, x + 228, y0, w - 234, "gsd-code-reviewer", "（置き換わらない）")
    vf = gsd_box(d, x + 228, rv.y + rv.h + 10, w - 234, "gsd-verifier", "（置き換わらない）")
    d.connector((x + 220, MB + 30), (x + 220, vf.cy), color=LINES["spawn"][0], lw=AW, tail=False, name="起こす矢印の幹")
    for b in (rv, vf):
        d.connector((x + 220, b.cy), (b, 1), color=LINES["spawn"][0], lw=AW, name="起こす矢印の枝")
    badge(d, oa.x + oa.w - 4, oa.y + 4, 1, gold=True)
    nv = cannot_box(d, x + 18, gx.y + gx.h + 18, w - 24,
                    ["agent_hint: gsd-verifier と書いた計画書は、", "gsd-executor が実装した（verifier のロールにはならない）"], 2)
    x, w = col_x(4)
    q = cannot_box(d, x + 10, y0, w - 18, T_["A_quick_box"], 3)
    lb = legend(d, 52, sd.y + sd.h + 20, ["cmd", "spawn", "write", "read", "boundary"],
                ["colors", "doc", "ghost", "graycross", "red", "gold", "callout", "purple"])
    bottom = finish(d, T, max(lb, nv.y + nv.h, q.y + q.h))
    items = edge_items(d, [
        item([1], [True], "問題点 1　置き換わるのは execute-phase の executor だけ",
             PP(T_["A_fact1"] + "自作の executor には、gsd-executor の約束（タスクごとのコミット・SUMMARY.md）を守らせる必要がある。",
                "planner・verifier・code-reviewer などは、この方法では置き換えられない。"),
             oa.y + 10, ["hint123", "routing123"]),
        item([2], [False], "問題点 2　GSD の別のロール名を書いても置き換わらない",
             PP("agent_hint: gsd-verifier と書いた計画書は、gsd-executor が実装した。仕様の「executor 以外のロール名は拒否する」と一致した。",
                "executor 以外のロールの置き換えには使えない。"),
             nv.cy, ["routing123"]),
        item([3], [False], "問題点 3　/gsd-quick では executor を置き換えられなかった",
             PP(T_["A_quick_fact"], "quick で実装する作業には、自作の executor を使えない。"),
             q.cy, ["routing123"]),
    ])
    pb = place_problems(d, items, MB - 16)
    return d, max(bottom, pb)


# ---- 図 B・C: Capability の step ----------------------------------------------------
STEP_FIRED = {"discuss:pre", "discuss:post", "plan:pre", "plan:post", "execute:pre", "wave:pre", "wave:post",
              "execute:post", "verify:pre", "verify:post"}


def fig_step(Y0, mode):
    tag = "own5B" if mode == "b" else "own5C"
    d = Drawing(tag=tag, name="図B step（agent）" if mode == "b" else "図C step（fork skill）")
    if mode == "b":
        title = "図B　Capability の step で、自作のサブエージェントを起動する（ref.agent）"
        why = "既定のロールを config でオフにし、同じループポイントで自作に本来の作業をさせると、後の工程がその成果物を使った"
    else:
        title = "図C　Capability の step で fork skill を呼び、自作のサブエージェントを起動する（ref.skill）"
        why = "図B と同じ場所で起動され、同じ置き換えができた。違いは skill を 1 つ挟むことと、skill も配置する手間"
    T, main, MB = skeleton(d, Y0, title, "ポイントのある所だけ", OK_GREEN, why, fired=STEP_FIRED)
    lines_ = [SETUP_HEAD, "・.claude/agents/own-r-○○.md（自作のロール）"]
    if mode == "c":
        lines_ += ["・.claude/skills/ownr-○○/SKILL.md と gsd-ownr-○○/",
                   [("  （context: fork・agent: own-r-○○）", {"color": SUB})]]
    lines_ += ["・Capability の steps（point と ref）",
               [("・config.json で既定のロールをオフ:", {"color": PURPLE})],
               [("  research・pattern_mapper・plan_check・", {"color": PURPLE})],
               [("  code_review・verifier・security_enforcement・", {"color": PURPLE})],
               [("  nyquist_validation・ui_review・ui_phase を false", {"color": PURPLE})]]
    sd = setup_doc(d, MB, lines_)
    line(d, "read", (main, 1), (sd, 0))
    y0 = MB + 44
    sfx = " の step" if mode == "b" else " の step → skill"
    x, w = col_x(0)
    np_ = cannot_box(d, x + 4, y0, w - 8, ["ポイントが無い。", "project-", "researcher・", "roadmapper は", "置き換え不可"], 4)
    x, w = col_x(1)
    od = own_box(d, x + 18, y0, w - 22, "own-" + mode + "-discuss-○○", "pre・post で起動（追加）")
    spawn_tree(d, x + 9, MB + 30, [od])
    # 計画
    x, w = col_x(2)
    bw = 150
    r1 = own_box(d, x + 18, y0, bw, "own-r-phase-researcher", "plan:pre" + sfx)
    r2 = own_box(d, x + 18, r1.y + r1.h + 8, bw, "own-r-pattern-mapper", "plan:pre" + sfx)
    pl = gsd_box(d, x + 18, r2.y + r2.h + 8, bw, "gsd-planner", "（オフにできない）")
    r3 = own_box(d, x + 18, pl.y + pl.h + 8, bw, "own-r-plan-checker", "plan:post" + sfx)
    ui = own_box(d, x + 18, r3.y + r3.h + 24, w - 22, "own-r-ui-researcher",
                 "UI のフェーズ: ui_phase を false にし、plan:pre" + sfx + "。\nplanner は自作の UI-SPEC.md を読んだ")
    spawn_tree(d, x + 9, MB + 30, [r1, r2, pl, r3, ui])
    for b, nm in [(r1, "gsd-phase-researcher"), (r2, "gsd-pattern-mapper"), (r3, "gsd-plan-checker")]:
        off_box(d, x + bw + 26, b.y, w - bw - 30, nm)
    badge(d, pl.x + pl.w - 4, pl.y + 4, 5)
    badge(d, r3.x + r3.w - 4, r3.y + 4, 6, gold=True)
    # 実装
    x, w = col_x(3)
    bw = 196
    ex = gsd_box(d, x + 18, y0, bw, "gsd-executor", "（オフにできない）")
    rs = []
    yy = ex.y + ex.h + 8
    for nm, pt in [("own-r-code-reviewer", "execute:post"), ("own-r-verifier", "execute:post"),
                   ("own-r-security-auditor", "verify:post"), ("own-r-nyquist-auditor", "verify:post"),
                   ("own-r-ui-auditor", "verify:post")]:
        b = own_box(d, x + 18, yy, bw, nm, pt + sfx)
        rs.append(b)
        yy = b.y + b.h + 6
    spawn_tree(d, x + 9, MB + 30, [ex] + rs)
    badge(d, ex.x + ex.w - 4, ex.y + 4, 5)
    for b, nm in zip(rs, ["gsd-code-reviewer", "gsd-verifier", "gsd-security-auditor", "gsd-nyquist-auditor",
                          "gsd-ui-auditor"]):
        off_box(d, x + bw + 26, b.y, w - bw - 30, nm)
    badge(d, rs[0].x + rs[0].w - 4, rs[0].y + 4, 7, gold=True)
    # 人の確認
    x, w = col_x(4)
    ov = own_box(d, x + 18, y0, w - 22, "own-" + mode + "-verify-○○", "verify:pre で起動（追加）。verify:post は不具合が 0 件のときだけ")
    db = cannot_box(d, x + 18, ov.y + ov.h + 14, w - 22,
                    ["gsd-debugger と、修正の計画の", "gsd-planner・gsd-plan-checker の", "所にはポイントが無い"], 8)
    spawn_tree(d, x + 9, MB + 30, [ov])
    yy = legend(d, 52, sd.y + sd.h + 20, ["cmd", "spawn", "read", "boundary"],
                ["colors", "doc", "ghost", "graycross", "red", "gold", "callout", "purple"])
    nb = note(d, 52, yy + 6, 300, [[("ポイントの札: ", {"bold": True}),
                                    ("青 = この方法で自作が実際に起動された所。白 = 起動されなかった所", {})]], size=9.5, name="札の見方")
    bottom = finish(d, T, max(nb, ui.y + ui.h, rs[-1].y + rs[-1].h, db.y + db.h))
    items = edge_items(d, [
        item([4], [False], "問題点 4　ポイントの無いコマンドでは何もできない",
             PP("自作が 1 回も起動されなかったコマンドは 14 個あった（表2 の下の行）。"
                "例: new-project・ui-phase・code-review --fix・debug・map-codebase。",
                "これらのコマンドで起動されるロールは、この方法では置き換えられない。"),
             np_.y + 14, ["points123"]),
        item([5], [False], "問題点 5　planner と executor はオフにできない",
             PP("オフにするキーが無い。オフにできるロールを全部オフにした対照の回でも、gsd-planner と gsd-executor は起動された。",
                "自作は追加になり、既定の planner・executor は必ず動く。"),
             pl.cy, ["toggles123"]),
        item([6], [True], "問題点 6　自作の plan-checker では、planner への差し戻しが起きない",
             PP("既定の plan-checker は、問題があると planner に書き直させる（最大 3 回）。step の自作は計画の後に 1 回動くだけで、"
                "planner は 1 回しか起動されなかった。",
                "計画の修正の往復は、自作の側で組む必要がある。"),
             r3.cy, ["steps123"]),
        item([7], [True], "問題点 7　成果物の名前が、GSD 同梱の部品と重なる",
             PP("step の成果物（produces）に RESEARCH.md などの本来の名前を書くと、インストールが止まった。"
                "既定のロールをオフにしていても同じ。別の名前で宣言し、本来の名前でも書かせると通った。",
                "宣言と実際のファイル名がずれた形で持つことになる。"),
             rs[0].cy, ["steps123"]),
        item([8], [False], "問題点 8　修正の往復（verify-work）のロールは置き換えられない",
             PP("不具合を報告した verify-work では、verify:pre だけが起きた。gsd-debugger と、修正の計画の planner・plan-checker "
                "が動く所にはポイントが無かった。",
                "修正の往復のロールを、この方法では置き換えられない。"),
             db.cy, ["points123"]),
        item([9], [True], "問題点 9　自作の定義" + ("と skill" if mode == "c" else "") + "は setup で配置する",
             PP("Capability の agents[]" + ("・skills[]" if mode == "c" else "") + " に入れた物は、.claude/ に配置されなかった。"
                "インストールでも GSD の再インストールでも同じだった。issue #5738 は承認済みで、1.23.0 でも未実装。",
                "案件をコピーしたら、setup と Capability の再インストールが要る。"),
             sd.y + 30, ["agents123", "5738"]),
    ])
    pb = place_problems(d, items, MB - 16)
    return d, max(bottom, pb)


# ---- 図 D: 既定のロールが fork skill で自作の子を起動する -------------------------------------------
def figD(Y0):
    d = Drawing(tag="own5D", name="図D 既定のロールから委任")
    T, main, MB = skeleton(d, Y0, "図D　既定のサブエージェントが、fork skill で自作の子を起動する（委任）", "追加・委任だけ", GOLD,
                           "Skill を持つ 22 ロールは子を起動できた。既定のロールは必ず動き、指示が渡らない経路・従わない回もある")
    sd = setup_doc(d, MB, [SETUP_HEAD,
                           "・.claude/agents/own-d-○○.md（自作の子）",
                           "・.claude/skills/ownd-○○/SKILL.md",
                           [("  （context: fork・agent: own-d-○○）", {"color": SUB})],
                           [("・「最初に Skill で ownd-○○ を呼ぶ」指示", {"color": PURPLE})],
                           [("  案件の CLAUDE.md（全コマンドで渡った）、または", {"color": PURPLE})],
                           [("  config の agent_skills（渡らないコマンドがあった）", {"color": PURPLE})]])
    line(d, "read", (main, 1), (sd, 0))
    y0 = MB + 44
    pairs = [(0, ["gsd-project-researcher", "gsd-roadmapper"]), (2, ["gsd-planner", "gsd-plan-checker"]),
             (3, ["gsd-executor", "gsd-verifier"]), (4, ["gsd-debugger"])]
    first = {}
    lows = []
    for ci, roles in pairs:
        x, w = col_x(ci)
        bw = w - 22 if ci not in (2, 3) else 170
        yy = y0
        parents = []
        for r in roles:
            p = gsd_box(d, x + 18, yy, bw, r)
            ind = 8
            c = own_box(d, x + 18 + ind, p.y + p.h + 18, bw - ind, "own-d-" + r[4:], "fork skill の子")
            line(d, "spawn", (p.x + ind + (bw - ind) / 2, p.y + p.h), (c, 0))
            parents.append(p)
            first[r] = p
            yy = c.y + c.h + 16
        lows.append(yy)
        spawn_tree(d, x + 9, MB + 30, parents)
    x, w = col_x(3)
    ns = cannot_box(d, x + 200, y0, w - 204, ["Skill の道具が無い 14 ロールは、", "子を起動できない",
                                              "（例: pattern-mapper・dom-verifier・", "doc-verifier・debug-session-manager）"], 10)
    pc, dbg, pr = first["gsd-plan-checker"], first["gsd-debugger"], first["gsd-project-researcher"]
    badge(d, pc.x + pc.w - 4, pc.y + 4, 11, gold=True)
    badge(d, dbg.x + dbg.w - 4, dbg.y + 4, 12, gold=True)
    badge(d, pr.x + pr.w - 4, pr.y + 4, 12, gold=True)
    badge(d, sd.x + sd.w - 8, sd.y + 8, 13, gold=True)
    lb = legend(d, 52, sd.y + sd.h + 20, ["cmd", "spawn", "read", "boundary"],
                ["colors", "doc", "ghost", "red", "gold", "callout", "purple"])
    bottom = finish(d, T, max([lb] + lows))
    items = edge_items(d, [
        item([13], [True], "問題点 13　既定のロールは必ず動く（置き換えではなく委任）",
             PP("子が作業をしても、既定のロールは起動され、自分の決まり（成果物の形式・コミット）で最後まで動いた。",
                "既定のロールの決まりと、子にさせたい決まりがぶつかる所は残る。"),
             sd.y + 20, []),
        item([12], [True], "問題点 12　agent_skills が渡らないコマンドがある",
             PP("agent_skills の指示が依頼文に入らなかった: new-project（defaults.json に書いても config に引き継がれない）・quick・"
                "verify-work・code-review --fix・debug・ingest-docs・secure-phase・validate-phase。案件の CLAUDE.md なら全コマンドで渡った。",
                "agent_skills だけに頼ると、指示が渡らないロールがある。"),
             pr.y + 14, ["skills123"]),
        item([11], [True], "問題点 11　指示に従わない回がある",
             PP(T_["D_comply"], "決まりを子に任せる形は、毎回は効かない。"),
             pc.cy, []),
        item([10], [False], "問題点 10　Skill の道具が無いロールは、子を起動できない",
             PP("36 ロールのうち Skill を持つのは 22 ロール。持たない 14 ロール（doc-verifier・doc-classifier・doc-synthesizer・"
                "framework-selector・ai-researcher・domain-researcher・eval-planner・pattern-mapper・dom-verifier・"
                "behavior-verifier・debug-session-manager など）は、指示を読んでも子を起動しなかった。"
                "security-auditor・nyquist-auditor は tools の欄がリストの形だが Skill を持ち、CLAUDE.md の指示で子を起動した。",
                T_["D_tools_red"]),
             ns.cy, ["skills123"]),
    ])
    pb = place_problems(d, items, MB - 16)
    return d, max(bottom, pb)


# ---- 図 E: メイン宛ての文 ---------------------------------------------------------------
E_FIRED = {"discuss:pre", "discuss:post", "verify:pre", "verify:post"}


def figE(Y0):
    d = Drawing(tag="own5E", name="図E メイン宛ての文")
    T, main, MB = skeleton(d, Y0, "図E　メイン宛ての文（contribution の orchestrator）で、自作を起動させる", "discuss・verify・ship の 6 か所だけ", GOLD,
                           "文を入れられるのは discuss・verify・ship の前後の 6 か所だけ。plan と execute ではインストールで止まる",
                           fired=E_FIRED)
    sd = setup_doc(d, MB, [SETUP_HEAD,
                           "・.claude/agents/own-e-○○.md（自作のロール）",
                           "・Capability の contributions",
                           [('  into: "orchestrator"', {"color": PURPLE})],
                           [("  「ここで own-e-○○ を起動する」（追加）", {"color": PURPLE})],
                           [("  「gsd-○○ の代わりに own-e-○○ を起動する」（置き換え）", {"color": PURPLE})]])
    line(d, "read", (main, 1), (sd, 0))
    y0 = MB + 44
    x, w = col_x(1)
    o1 = own_box(d, x + 18, y0, w - 22, "own-e-discuss-○○", "pre・post で起動（追加）")
    spawn_tree(d, x + 9, MB + 30, [o1])
    pc = None
    for ci in (2, 3):
        x, w = col_x(ci)
        c = cannot_box(d, x + 22, y0, w - 28, ["plan・execute のポイントには、", "メイン宛ての文を入れられない",
                                                "（インストールで止まった）"], 14)
        pc = pc or c
    x, w = col_x(3)
    o3 = own_box(d, x + 18, y0 + 90, w - 22, "own-e-verify-post", T_["E_exec_sub"])
    d.connector((x + 9, MB + 30), (x + 9, o3.cy), color=LINES["spawn"][0], lw=AW, tail=False, name="起こす矢印の幹")
    d.connector((x + 9, o3.cy), (o3, 1), color=LINES["spawn"][0], lw=AW, name="起こす矢印の枝")
    x, w = col_x(4)
    o4 = own_box(d, x + 18, y0, w - 22, "own-e-verify-○○", "verify:pre・verify:post で起動（追加）")
    rep = own_box(d, x + 18, o4.y + o4.h + 14, w - 22, "own-e-debugger・planner・plan-checker",
                  "gsd-debugger・gsd-planner・gsd-plan-checker の代わりに起動された（置き換え）")
    spawn_tree(d, x + 9, MB + 30, [o4, rep])
    badge(d, rep.x + rep.w - 4, rep.y + 4, 15, gold=True)
    lb = legend(d, 52, sd.y + sd.h + 20, ["cmd", "spawn", "read", "boundary"],
                ["colors", "doc", "ghost", "red", "gold", "callout", "purple"])
    bottom = finish(d, T, max(lb, rep.y + rep.h, o3.y + o3.h))
    items = edge_items(d, [
        item([14], [False], "問題点 14　plan と execute では使えない",
             PP("into: orchestrator の文は、plan:pre・plan:post・execute の 4 か所ではインストールが止まった"
                "（orchestrator は agentRoles に無い）。discuss・verify・ship の前後の 6 か所だけ入った。",
                "計画と実装の間のロールを、この方法では起動できない（execute-phase の最後の verify:post だけは入る）。"),
             pc.cy, ["points123"]),
        item([15], [True], "問題点 15　置き換えは、メインが文に従うかしだい",
             PP(T_["E_rep"], "文に従うかはメインの判断で、仕組みとしての保証は無い。"),
             rep.cy, []),
    ])
    pb = place_problems(d, items, MB - 16)
    return d, max(bottom, pb)


# ---- 表 1: ロールごとの結果 -----------------------------------------------------------------
ROLE_ROWS = []
ROLE_COLS = [("ロール（GSD のサブエージェント）", 220), ("A agent_hint", 190), ("B・C Capability の step", 300),
             ("D 既定のロールから委任", 270), ("E メイン宛ての文", 240), ("実機の検証（コピーの名前）", 230)]


def table_head(d, x0, y, cols, size=11):
    cx = x0
    for title, w in cols:
        d.shape(cx, y, w, 30, "rect", fill=("bg2",), line="A6A6A6", lw=0.75, text=[[(title, {"bold": True})]],
                size=size, font=UD, color="000000", ins=(2, 0, 2, 0), name="表の見出し")
        cx += w
    return y + 30


def role_table(Y0):
    d = Drawing(tag="own5T1", name="ロールごとの結果")
    d.text(26, Y0, 1500, 40, "表1　ロールごとに、5 つの方法で自作に置き換えられたか（GSD 1.23.0 の実機の結果）", size=24, font=None,
           color="000000", wrap="none", name="見出し")
    note(d, 34, Y0 + 40, 1450,
         ["○ = 実機で置き換わった（D は子を起動できた）。△ = 条件つき、または毎回ではない。✕ = 実機でできなかった。",
          "D は置き換えではなく、既定のロールの中からの委任。数は「子を起動できた回 / ロールが起動された回」。",
          "右端の列は、検証で使った案件のコピー（trials-v2/own-<名前>）。根拠を確かめるときに、その会話の記録を開く。",
          "Claude Code の hook で差し替える方法（表4 の F）はロールに依らず効くので、この表の列にはしていない。"],
         size=11, name="表の見方")
    x0, y = 34, Y0 + 120
    with d.group("表1"):
        y = table_head(d, x0, y, ROLE_COLS)
        for row in ROLE_ROWS:
            cells = [(INK, cell(row[0]))] + [(c, cell(t)) for c, t in row[1:5]] + [(SUB, cell(row[5]))]
            rh = max(32, max(need_h(t, w, 9.5, UD, (6, 2, 4, 2)) for (_, t), (_, w) in zip(cells, ROLE_COLS)) + 6)
            cx = x0
            for (color, t), (_, w) in zip(cells, ROLE_COLS):
                d.shape(cx, y, w, rh, "rect", fill="FFFFFF", line="A6A6A6", lw=0.75, text=t, size=9.5, font=UD,
                        color=color, align="l", anchor="ctr", ins=(6, 2, 4, 2), name="表のセル")
                cx += w
            y += rh
    return d, y + 20


# ---- 表 2: コマンドごとに起きたポイント -----------------------------------------------------------
PT_COLS = ["discuss:pre", "discuss:post", "plan:pre", "plan:post", "execute:pre", "wave:pre", "wave:post", "execute:post",
           "verify:pre", "verify:post", "ship:pre", "ship:post"]
FIRE_ROWS = []


def fire_table(Y0):
    d = Drawing(tag="own5T2", name="ポイントの表")
    d.text(26, Y0, 1500, 40, "表2　コマンドごとに、自作のサブエージェントが起動されたループポイント（B・C・E の土台）", size=24,
           font=None, color="000000", wrap="none", name="見出し")
    note(d, 34, Y0 + 40, 1450,
         ["B = step（agent）、C = step（fork skill）、E = メイン宛ての文。書いてある記号の方法で、自作が実際に起動された。",
          "空欄 = 起動されなかった。E の文は discuss・verify・ship の前後にしか入らない。",
          "A（agent_hint）と D（既定のロールからの委任）はループポイントを使わないので、この表には出ない。"], size=11, name="表の見方")
    x0 = 34
    cw = [250] + [72] * len(PT_COLS) + [340]
    heads = ["コマンド（検証の条件）"] + PT_COLS + ["注"]
    y = Y0 + 104
    with d.group("表2"):
        y = table_head(d, x0, y, list(zip(heads, cw)), size=9)
        for cmd, marks, nt in FIRE_ROWS:
            cmd_t, nt_t = cell(cmd), cell(nt) if nt else ""
            h = max(30, need_h(nt_t, cw[-1], 9.5, UD, (6, 2, 4, 2)) + 6 if nt else 30,
                    need_h(cmd_t, cw[0], 9.5, UD, (6, 2, 4, 2)) + 6)
            cx = x0
            d.shape(cx, y, cw[0], h, "rect", fill="FFFFFF", line="A6A6A6", lw=0.75, text=cmd_t, size=9.5, font=UD,
                    color=INK, align="l", ins=(6, 2, 4, 2), name="表のセル")
            cx += cw[0]
            for p, w in zip(PT_COLS, cw[1:-1]):
                m = marks.get(p, "")
                d.shape(cx, y, w, h, "rect", fill=("accent1", 20, 80) if m else "FFFFFF", line="A6A6A6", lw=0.75,
                        text=m, size=9.5, font=UD, color=INK, ins=(1, 0, 1, 0), name="表のセル")
                cx += w
            d.shape(cx, y, cw[-1], h, "rect", fill="FFFFFF", line="A6A6A6", lw=0.75, text=nt_t, size=9.5, font=UD,
                    color=SUB, align="l", ins=(6, 2, 4, 2), name="表のセル")
            y += h
    return d, y + 20


# ---- 表 3・表 4: 文字だけの表（列と行は own5_data が入れる） --------------------------------------------
# 1 つの表 = dict(tag, name, title, notes, cols=[(見出し, 幅)], rows=[[(色, 文), ...]]). 文の色は INK/OK_GREEN/GOLD/RED/SUB。
TEXT_TABLES = []


def text_table(spec, Y0):
    d = Drawing(tag=spec["tag"], name=spec["name"])
    d.text(26, Y0, 1500, 40, spec["title"], size=24, font=None, color="000000", wrap="none", name="見出し")
    y = Y0 + 44
    if spec.get("notes"):
        note(d, 34, y, 1450, spec["notes"], size=11, name="表の見方")
        y += 16 * len(spec["notes"]) + 18
    x0 = 34
    with d.group(spec["name"]):
        y = table_head(d, x0, y, spec["cols"], size=spec.get("head_size", 11))
        for row in spec["rows"]:
            # 空のセルは "" にする（空の list だと txBody に段落が無くなり、Excel が「問題が見つかった」と修復を求める）
            cells = [(c, cell(t) if t else "") for c, t in row]
            rh = max(32, max(need_h(t, w, 9.5, UD, (6, 2, 4, 2)) for (_, t), (_, w) in zip(cells, spec["cols"]) if t) + 6)
            cx = x0
            for (color, t), (_, w) in zip(cells, spec["cols"]):
                d.shape(cx, y, w, rh, "rect", fill="FFFFFF", line="A6A6A6", lw=0.75, text=t, size=9.5, font=UD,
                        color=color, align="l", anchor="ctr", ins=(6, 2, 4, 2), name="表のセル")
                cx += w
            y += rh
    return d, y + 20


CONCLUSION = []
HEAD_CONCLUSION = []
VERIFY_NOTE = []


def conclusion(Y0):
    d = Drawing(tag="own5T3", name="結論")
    with d.group("結論"):
        h = need_h(CONCLUSION, 1450, 11, UD, (10, 4, 8, 4)) + 8
        d.shape(34, Y0, 1450, h, "rect", fill=("accent2", 20, 80), line=("accent2",), lw=1, text=CONCLUSION,
                size=11, font=UD, color="000000", align="l", anchor="ctr", ins=(10, 4, 8, 4), name="結論")
    return d, Y0 + h + 20


TERMS = ["GSD: AI に計画書を書かせてから実装させるツール。メイン: 人と話す AI。",
         "サブエージェント（ロール）: メインが起動して作業を任せる別の AI。既定のロールは gsd-○○ という名前で 36 種類ある。",
         "Capability: GSD に処理を追加する正式な部品。",
         "ループポイント: Capability の処理が差し込まれる場所（plan:pre など）。",
         "step: ループポイントでメインに起動させるサブエージェントか skill。contribution: ロールやメインへの依頼文に追記する文。",
         "fork skill: 呼ぶと、指定のサブエージェントを子として起動する skill。",
         "agent_skills: GSD の設定で、ロールに skill を渡す欄。",
         "setup: 案件ごとに 1 回、キットの部品を .claude/ などに配置する作業。",
         "autonomous: /gsd-autonomous。フェーズごとに相談→計画→実装を、人に聞かずにメインが順に進めるコマンド。",
         "--auto: 相談のコマンドに付けると、そのフェーズの計画→実装まで自動でつなぐ。",
         "hook: Claude Code の仕組み。道具の呼び出しの前後やサブエージェントの起動時に、決めたスクリプトを動かす。"]


def head():
    d = Drawing(tag="own5head", name="頭書き")
    d.text(26, 0, 1500, 44, "GSD で自作のサブエージェントを起動する 5 つの方法 ― GSD 1.23.0 の実機で確認した結果", size=26,
           font=None, color="000000", wrap="none", name="見出し")
    y = note(d, 26, 46, 1500, HEAD_CONCLUSION, size=12, name="見出し（結論）") + 10
    y = note(d, 26, y, 1500, TERMS, size=10.5, name="見出し（用語）") + 10
    y = note(d, 26, y, 1500, VERIFY_NOTE, size=10.5, color="595959", name="見出し（検証の方法）")
    return d, y + 30


# ---- 書き込み -------------------------------------------------------------------------------
def strip_all(src, tmp, sheet_name):
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "xl/drawings/drawing1.xml":
                x = data.decode("utf-8")
                x = re.sub(r'<xdr:(twoCellAnchor|absoluteAnchor|oneCellAnchor)\b.*?</xdr:\1>', "", x, flags=re.S)
                data = x.encode("utf-8")
            elif info.filename == "xl/drawings/_rels/drawing1.xml.rels":
                data = re.sub(r'<Relationship Id="rIdX[^"]*"[^>]*/>', "", data.decode("utf-8")).encode("utf-8")
            elif info.filename == "xl/workbook.xml":
                data = re.sub(r'(<sheet [^>]*name=")[^"]+(")', r"\g<1>" + sheet_name + r"\g<2>", data.decode("utf-8"),
                              count=1).encode("utf-8")
            elif info.filename == "docProps/app.xml":
                data = re.sub(r"<vt:lpstr>理想から今の形まで</vt:lpstr>", f"<vt:lpstr>{sheet_name}</vt:lpstr>",
                              data.decode("utf-8")).encode("utf-8")
            zout.writestr(info, data)


def build(src, dst):
    grid = measure_grid(src)
    tmp = dst + ".tmp.xlsx"
    strip_all(src, tmp, "自作サブエージェントの起動方法")
    hd, y = head()
    parts = [hd]
    spans = []
    for fn in (figA, lambda Y: fig_step(Y, "b"), lambda Y: fig_step(Y, "c"), figD, figE):
        d, b = fn(y)
        parts.append(d)
        spans.append((y, b))
        y = b + 50
    tails = [role_table, fire_table] + [(lambda Y, s=s: text_table(s, Y)) for s in TEXT_TABLES] + [conclusion]
    for fn in tails:
        d, b = fn(y)
        parts.append(d)
        spans.append((y, b))
        y = b + 30
    row = int(y * 12700 // grid.row_h) + 2

    def edit(sheet):
        sheet = re.sub(r'<row r="\d+" spans="2:2"><c r="B\d+" t="s"><v>0</v></c></row>',
                       f'<row r="{row}" spans="2:2"><c r="B{row}" t="s"><v>0</v></c></row>', sheet)
        return re.sub(r'<dimension ref="[^"]*"/>', f'<dimension ref="B{row}"/>', sheet)
    write_into(tmp, dst, parts, grid=grid, sheet_edit=edit)
    os.remove(tmp)
    return spans


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import own5_data
    own5_data.fill(sys.modules[__name__])
    spans = build(sys.argv[1], sys.argv[2])
    print(f"書きました: {sys.argv[2]}")
    names = ["図A", "図B", "図C", "図D", "図E", "表1", "表2"] + [s["name"] for s in TEXT_TABLES] + ["結論"]
    for n, (a, b) in zip(names, spans):
        print(f"  {n}: y {a:.0f}〜{b:.0f}")
