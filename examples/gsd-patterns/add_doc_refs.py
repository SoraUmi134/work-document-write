"""「GSDに独自処理を挟む方法の検討.xlsx」の 3 つのパターンの図に、公式ドキュメントの記載場所の箱を追加する。

使い方:
  python3 add_doc_refs.py <元の xlsx> <出力の xlsx>

人が描いた図形には触らない。パターンごとに、ポイントの箱の右（図の枠の中の空いている所）へ箱を 1 つ追加する。
箱の内容（リンク先）は doc_refs.py が持つ。同じ目印（tag）で書くので、何度実行しても箱は 1 つずつになる。
元の xlsx は書き換えない。
"""
import os
import re
import sys
import zipfile

PART = "xl/drawings/drawing1.xml"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "excel-figure", "scripts"))
sys.path.insert(0, HERE)
import doc_refs  # noqa: E402
from xdraw import CellGrid, Drawing, write_into  # noqa: E402

# パターンごとの箱の位置（pt）。ポイントの箱の右端から 20pt 空け、上端をポイントの箱にそろえた
PLACES = {"1": (1232, 891, 420), "2": (1262, 1666, 420), "3": (1426, 2420, 420)}
FONT, SIZE = "BIZ UDGothic", 10


ANCHOR = re.compile(r"<xdr:twoCellAnchor\b.*?<xdr:from><xdr:col>\d+</xdr:col><xdr:colOff>-?\d+</xdr:colOff>"
                    r"<xdr:row>(\d+)</xdr:row><xdr:rowOff>(-?\d+)</xdr:rowOff></xdr:from>.*?"
                    r'<a:off x="-?\d+" y="(-?\d+)"/>', re.S)
LAST_TALL_ROW = 16               # この行（1 始まり）より上に、高さを変えた行がある


def local_grid(src):
    """図の近くの行から、セルの大きさを測る。

    このシートは上の方（16 行目まで）に高さを変えた行があり、xdraw の測り方（一番大きい図の平均）では
    図の位置が 2 行ほど下にずれる。図が固定されている行の上端の位置を 2 つ取り、その間の行数で割って
    標準の行の高さを出し、上の行の分は 1 行目にまとめて持たせる。"""
    with zipfile.ZipFile(src) as z:
        dxml = z.read(PART).decode("utf-8")
        sheet = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    tops = sorted({(int(r), int(y) - int(off)) for r, off, y in ANCHOR.findall(dxml) if int(r) >= LAST_TALL_ROW})
    (r1, y1), (r2, y2) = tops[0], tops[-1]
    row_h = (y2 - y1) / (r2 - r1)
    base = CellGrid.measure(dxml, sheet)
    return CellGrid(base.col_w, row_h, base.custom_cols, {0: y1 - (r1 - 1) * row_h})


def build(src, dst):
    grid = local_grid(src)
    drawings = []
    for key, (x, y, w) in PLACES.items():
        d = Drawing(tag="docref" + key, name="パターン" + key + " 公式ドキュメントの記載場所")
        doc_refs.ref_box(d, x, y, w, key, size=SIZE, font=FONT)
        drawings.append(d)
    write_into(src, dst, drawings, drawing_part=PART, grid=grid)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
    print(f"書きました: {sys.argv[2]}")
