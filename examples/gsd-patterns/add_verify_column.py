"""人が描いた「GSDに独自処理を挟む方法の検討.xlsx」の 3 つのパターンの図に、/gsd-verify-work の列を追加する。

使い方:
  python3 add_verify_column.py <元の xlsx> <出力の xlsx>

人の図は、グループが入れ子になっていて、グループごとに倍率が付いている。そこで次の方針で手を入れる。
- 既存の図形は動かさない。枠・メインエージェントの帯・区切り線の 3 つだけ、右へ伸ばす。
- /gsd-execute-phase の列の図形（コマンドの矢印形・線・番号・箱・書類）を写して右へずらし、字だけを変える。
  同じグループの中に写すので、色・字体・線の太さは人の図とまったく同じになる。
- グループの大きさと、セルへの留め方（to の列）も、伸ばした分だけ広げる。
元の xlsx は書き換えない。何度実行しても同じ結果になるよう、必ず手を入れる前のファイルを入力にする。
"""
import os
import re
import sys
import zipfile

EMU = 12700
PART = "xl/drawings/drawing1.xml"
COL_W = 330                      # 追加する列の幅（pt）
GAP = 12                         # 隣の列との間（pt）
WIDEN = COL_W + GAP
TOKEN = re.compile(r"<xdr:grpSp>|</xdr:grpSp>|<xdr:(sp|cxnSp|pic)\b.*?</xdr:\1>", re.S)
XFRM = re.compile(r'(<a:xfrm[^>]*><a:off x=")(-?\d+)(" y=")(-?\d+)("/><a:ext cx=")(\d+)(" cy=")(\d+)("/>)')
GXFRM = re.compile(r'(<a:xfrm[^>]*><a:off x=")(-?\d+)(" y=")(-?\d+)("/><a:ext cx=")(\d+)(" cy=")(\d+)'
                   r'("/><a:chOff x=")(-?\d+)(" y=")(-?\d+)("/><a:chExt cx=")(\d+)(" cy=")(\d+)("/>)')
# 写した図形の中の字の入れ替え（左が元、右が新しい字）。番号はパターンごとに違う
NUMBERS = {1: {"(6)": "(8)", "(7)": "(9)"}, 2: {"(6)": "(8)", "(7)": "(9)"}, 3: {"(7)": "(10)", "(8)": "(11)", "(9)": "(12)"}}
WORDS = {"/gsd-execute-phase": "/gsd-verify-work", "作る": "確認する", "gsd-executor": "gsd-verifier", "△△": "□□",
         "execute:post": "verify:post"}


class Node:
    """図形（leaf）かグループ（grp）。xa・xb は、この中の x をシートの x にする式（x_sheet = xa * x + xb）。y も同じ。"""

    def __init__(self, kind, start, parent):
        self.kind, self.start, self.end, self.parent, self.kids = kind, start, None, parent, []
        self.xml = self.name = None
        self.xa, self.xb, self.ya, self.yb = 1.0, 0.0, 1.0, 0.0


def parse(xml, lo, hi):
    """lo〜hi の間のグループと図形を木にする。"""
    root = Node("root", lo, None)
    cur = root
    for m in TOKEN.finditer(xml, lo, hi):
        t = m.group(0)
        if t == "<xdr:grpSp>":
            n = Node("grp", m.start(), cur)
            cur.kids.append(n)
            cur = n
        elif t == "</xdr:grpSp>":
            cur.end = m.end()
            cur = cur.parent
        else:
            n = Node("leaf", m.start(), cur)
            n.end, n.xml = m.end(), t
            n.name = re.search(r'<xdr:cNvPr id="\d+" name="([^"]*)"', t).group(1)
            cur.kids.append(n)
    return root


def place(xml, node):
    """各図形とグループの、シート上の位置（EMU）を計算する。"""
    for k in node.kids:
        if k.kind == "grp":
            head = xml[k.start:k.kids[0].start if k.kids else k.end]
            g = GXFRM.search(head)
            ox, oy, ex, ey, cx, cy, cw, ch = (int(g.group(i)) for i in (2, 4, 6, 8, 10, 12, 14, 16))
            k.g, k.xfrm_at = g, k.start + g.start()
            k.x, k.w = node.xa * ox + node.xb, node.xa * ex              # グループの枠は親の座標にある
            k.xa, k.xb = node.xa * ex / cw, node.xa * (ox - cx * ex / cw) + node.xb
            k.ya, k.yb = node.ya * ey / ch, node.ya * (oy - cy * ey / ch) + node.yb
            place(xml, k)
        else:
            f = XFRM.search(k.xml)
            k.f = f
            k.x, k.w = node.xa * int(f.group(2)) + node.xb, node.xa * int(f.group(6))
            k.y, k.h = node.ya * int(f.group(4)) + node.yb, node.ya * int(f.group(8))


def leaves(node):
    for k in node.kids:
        if k.kind == "grp":
            yield from leaves(k)
        else:
            yield k


def groups_above(n):
    while n.parent is not None and n.parent.kind == "grp":
        n = n.parent
        yield n


def with_xfrm(n, dx=0.0, dw=0.0):
    """図形の XML を、x を dx、幅を dw だけ変えた物にする（dx・dw はシートの EMU）。"""
    f, scale = n.f, n.parent.xa
    new = (f"{f.group(1)}{int(f.group(2)) + round(dx / scale)}{f.group(3)}{f.group(4)}{f.group(5)}"
           f"{int(f.group(6)) + round(dw / scale)}{f.group(7)}{f.group(8)}{f.group(9)}")
    return n.xml[:f.start()] + new + n.xml[f.end():]


def clone(n, dx, ids, words, new_w=None):
    """図形を写して、右へ dx（シートの EMU）だけずらす。字は words で入れ替える。"""
    x = with_xfrm(n, dx=dx, dw=(new_w - n.w) if new_w is not None else 0.0)
    x = re.sub(r'(<xdr:cNvPr id=")\d+(")', lambda m: f"{m.group(1)}{next(ids)}{m.group(2)}", x, count=1)
    x = re.sub(r"<a:extLst>.*?</a:extLst>", "", x, count=1, flags=re.S)       # 作成時の ID は写さない
    x = re.sub(r"<a:(stCxn|endCxn)\b[^>]*/>", "", x)                          # 元の箱へのつなぎは写さない

    def swap(m):
        t = m.group(1)
        for old, new in words.items():
            t = t.replace(old, new)
        return f"<a:t>{t}</a:t>"
    return re.sub(r"<a:t>(.*?)</a:t>", swap, x, flags=re.S)


def is_pointer(n):
    """要点の箱から伸びる斜めの線（列の物ではないので写さない）。"""
    return n.xml.startswith("<xdr:cxnSp") and n.w > 50 * EMU and n.h > 50 * EMU


def edit_pattern(xml, anchor, pattern_no, ids, col_emu):
    lo, hi = anchor.start(), anchor.end()
    root = parse(xml, lo, hi)
    place(xml, root)
    every = list(leaves(root))

    def one(name):
        hit = [n for n in every if n.name == name]
        assert len(hit) == 1, (pattern_no, name, len(hit))
        return hit[0]
    frame, bar, divider, chev = one("枠"), one("メインエージェント"), one("区切り線"), one("/gsd-execute-phase")
    widen = WIDEN * EMU
    bar_right = bar.x + bar.w
    vx = bar_right + GAP * EMU                               # 新しい列の左端
    edits = [(n.start, n.end, with_xfrm(n, dw=widen)) for n in (frame, bar, divider)]
    # 実行の列の図形（枠・帯・区切り線・境目・凡例・要点の箱とその線を除く）を写す
    column = [n for n in every if n not in (frame, bar, divider, chev) and n.name != "境目"
              and not n.name.startswith(("凡例", "吹き出し")) and not is_pointer(n)
              and n.x >= chev.x - EMU and n.x + n.w <= bar_right + 30 * EMU and chev.y <= n.y <= chev.y + 400 * EMU]
    solid = [n for n in column if not n.xml.startswith("<xdr:cxnSp") and n.name != "番号"]
    left, right = min(n.x for n in solid), max(n.x + n.w for n in solid)
    shift = vx + (COL_W * EMU - (right - left)) / 2 - left   # 写した物を、新しい列の真ん中に置く
    words = dict(WORDS, **NUMBERS[pattern_no])
    for n in column:
        edits.append((n.end, n.end, clone(n, shift, ids, words)))
    edits.append((chev.end, chev.end, clone(chev, vx - chev.x, ids, words, new_w=COL_W * EMU)))
    for n in sorted((n for n in every if n.name == "境目"), key=lambda n: n.x)[-2:]:
        edits.append((n.end, n.end, clone(n, (vx - 6 * EMU) - n.x, ids, {})))
    # 広げた図形を含むグループを、外側まで全部広げる
    touched = {}
    for n in (frame, bar, divider):
        for g in groups_above(n):
            touched[id(g)] = g
    for g in touched.values():
        m = g.g
        new = (f"{m.group(1)}{m.group(2)}{m.group(3)}{m.group(4)}{m.group(5)}{int(m.group(6)) + round(widen / g.parent.xa)}"
               f"{m.group(7)}{m.group(8)}{m.group(9)}{m.group(10)}{m.group(11)}{m.group(12)}{m.group(13)}"
               f"{int(m.group(14)) + round(widen / g.xa)}{m.group(15)}{m.group(16)}{m.group(17)}")
        edits.append((g.xfrm_at, g.xfrm_at + (m.end() - m.start()), new))
    # セルへの留め方（右端の列）
    top = root.kids[0]
    right_edge = top.x + top.w + widen
    col = int(right_edge // col_emu)
    m = re.compile(r"(<xdr:to><xdr:col>)\d+(</xdr:col><xdr:colOff>)-?\d+(</xdr:colOff>)").search(xml, lo, hi)
    edits.append((m.start(), m.end(), f"{m.group(1)}{col}{m.group(2)}{round(right_edge - col * col_emu)}{m.group(3)}"))
    return edits, len(column)


def main(src, dst):
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "..", "..", "skills", "excel-figure", "scripts"))
    from xdraw import measure_grid
    grid = measure_grid(src, PART)
    with zipfile.ZipFile(src) as z:
        xml = z.read(PART).decode("utf-8")
        parts = [(i, z.read(i.filename)) for i in z.infolist()]
    used = max(int(v) for v in re.findall(r'<xdr:cNvPr id="(\d+)"', xml))
    ids = iter(range(used + 1, used + 5000))
    anchors = [m for m in re.finditer(r"<xdr:twoCellAnchor\b.*?</xdr:twoCellAnchor>", xml, re.S)
               if 'name="/gsd-execute-phase"' in m.group(0)]
    assert len(anchors) == 3, len(anchors)
    edits = []
    for no, m in enumerate(anchors, 1):
        e, n = edit_pattern(xml, m, no, ids, grid.col_w)
        edits += e
        print(f"パターン{no}: 実行の列から {n} 個の図形を写した")
    for start, end, new in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
        xml = xml[:start] + new + xml[end:]
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for info, raw in parts:
            z.writestr(info, xml.encode("utf-8") if info.filename == PART else raw)
    print(f"書きました: {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
