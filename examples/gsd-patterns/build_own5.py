"""「GSD で自作のサブエージェントを起動する 5 つの方法」の Excel を作る（GSD 1.23.0 の実機の結果）。

使い方（openpyxl が要る。作業用の venv の python で実行する）:
  <venv>/bin/python build_own5.py <テーマの元の xlsx> <出力の xlsx>

- テーマの元の xlsx は、図形の色（緑 = accent6 など）を決めるテーマを写すために使う。前に出力した Excel 自身でよい。
- 人が作った Excel（GSDに独自処理を挟む方法の検討.xlsx）の見た目に合わせてある。
  - 見出しの帯・結論の数行・パターンの題と結果は、図形ではなくセルに書く（メイリオ）。
  - 図はパターンごとに 1 枚。注は紫の「ポイント」の箱 1 つで、3 行まで。長い説明は図に書かない。
  - 比べる話は別のシートのセルの表にする（シート 2: パターンの比較表、シート 3: ロールごとの結果）。
- 図のコマンドは /gsd-new-project から /gsd-verify-work まで描く。
- 詳しい検証の結果（問題点の全文・コマンドごとのループポイント・autonomous・GSD の外の方法の全項目）は Excel に入れない。
  作業場の 記録/資料の文字の版と根拠/ の md に残してある。ロールごとの表の内容は own5_data.py の ROLE_ROWS。
"""
import importlib.util
import math
import os
import sys
import zipfile

from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.indexed_list import IndexedList

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "excel-figure", "scripts"))
from xdraw import CellGrid, Drawing, ensure_drawing, write_into  # noqa: E402

sys.path.insert(0, HERE)
import doc_refs  # noqa: E402

spec = importlib.util.spec_from_file_location("v4", os.path.join(HERE, "build_3ways_v4.py"))
v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4)
GREEN, GREEN_LINE, BLUE, BLUE_LINE = v4.GREEN, v4.GREEN_LINE, v4.BLUE, v4.BLUE_LINE
INK, SUB, YU, UD, LINES = v4.INK, v4.SUB, v4.YU, v4.UD, v4.LINES
OK_GREEN, GOLD, RED = v4.OK_GREEN, v4.GOLD, v4.RED

# ---- セルの大きさ（人の Excel と同じ方眼。既定の字体は 游ゴシック 12） ---------------------------
# 列の幅 3.7109375・行の高さ 20 のシートを Mac の Excel で開いた時の実際の大きさ（EMU）。既存の図から測った値。
COL_EMU, ROW_EMU = 331931.875, 259772.792
PX_EMU = ROW_EMU / 27            # 行の高さ 20pt は 27 ピクセルで描かれる
EMU_PT = 12700
MEIRYO = "メイリオ"
BAND_FILL = "A9D98B"             # 見出しの帯（人の Excel の緑）
HEAD_FILL = "B4C6E7"             # 表の見出し（人の比較表の青）
SHEETS = ("1.自作サブエージェントを起動する方法", "2.パターンの比較表", "3.ロールごとの結果")
LAST_COL = 61                    # 帯を塗る右端の列（図の枠の右端）

# ---- シート 1 の文（セルに書く） ---------------------------------------------------------------
LEAD = "GSD に自作のサブエージェントを起動させる方法を 5 つ、GSD 1.23.0 の実機で検証した。結論は下記の通り。"
CONCLUSIONS = [
    "[1] 1 つのパターンで、GSD の全部のサブエージェントを自作に置き換えることはできない",
    "[2] パターンA は gsd-executor だけ、パターンB・C はループポイントのある所のサブエージェントだけを置き換えられる",
    "[3] パターンD・E は、既定のサブエージェントやメインエージェントに自作の起動を任せる形で、毎回は効かない",
    "[4] どのパターンでも、自作のサブエージェントの定義は、案件ごとの setup で .claude/ に配置する必要がある",
    "[5] GSD の外の仕組み（Claude Code の hook）を使うと、全部のサブエージェントを置き換えられる。/gsd-autonomous でも同じ（シート 2 の参考）",
    "[6] /gsd-autonomous（人に聞かずに自動で進めるコマンド）でも、パターンA・B・D はそのまま使える。パターンC・E は一部が違う",
    "[7] 自作に skill を持たせるには、自作の定義ファイルの skills の欄に書く。config の agent_skills に自作の名前を書いても渡らない（シート 2 の参考）",
]
TERMS = [
    "言葉）メインエージェント = 人と話し、コマンドの手順どおりにサブエージェント（作業を任せる別の AI）を起動する AI。",
    "　　　ループポイント = Capability（GSD に部品を追加する正式な仕組み）の処理を挿入できる場所（plan:pre など）。",
    "　　　fork skill = 呼ぶと、指定したサブエージェントを子として起動する skill。　setup = 案件ごとに 1 回、自作の部品を .claude/ に配置する作業。",
]

# ---- 図の骨組み -----------------------------------------------------------------------------
FX, FW, FH = 45, 1516, 600
BAR_X, BAR_W = 401, 1148
CMDS = [("np", 401, 150, "/gsd-new-project", "案件を始める"), ("discuss", 563, 150, "/gsd-discuss-phase", "決め事を相談"),
        ("plan", 725, 250, "/gsd-plan-phase", "計画書を書く"), ("execute", 987, 320, "/gsd-execute-phase", "作る"),
        ("verify", 1319, 230, "/gsd-verify-work", "人が確認する")]
ITEM_H, ITEM_GAP, ITEM_TOP = 62, 16, 236
POINT_FILL, POINT_LINE = ("accent5", 20, 80), ("accent5", 50, None)


def G(name, sub=None, **kw):
    return dict(kind="gsd", name=name, sub=sub, **kw)


def O(name, sub=None, **kw):
    return dict(kind="own", name=name, sub=sub, **kw)


def OFF(name):
    return dict(kind="off", name=name, sub=None)


def NONE(text):
    return dict(kind="none", name=text, sub=None)


STEP_COLS = lambda arrow: {  # noqa: E731  パターンB・C の列（arrow は「step」の後ろに付ける字）
    "np": [NONE("ループポイントが無い\n（自作を起動できない）")],
    "discuss": [O("own-○○", f"discuss:pre・post{arrow}（追加）")],
    "plan": [O("own-researcher", f"plan:pre{arrow}（gsd-phase-researcher の代わり）"),
             G("gsd-planner", "オフにできない（必ず動く）"),
             O("own-plan-checker", f"plan:post{arrow}（gsd-plan-checker の代わり）")],
    "execute": [G("gsd-executor", "オフにできない（必ず動く）"),
                O("own-code-reviewer・own-verifier", f"execute:post{arrow}（既定の 2 つの代わり）"),
                O("own-○○-auditor（監査の 3 つ）", f"verify:post{arrow}（既定の監査の代わり）")],
    "verify": [O("own-○○", f"verify:pre{arrow}（追加）"),
               NONE("不具合の調査（gsd-debugger）の所には\nループポイントが無い")],
}

PATTERNS = [
    dict(key="A", auto=('○', '使える（単独のコマンドと同じに起動される）', '使える。単独のコマンドと同じに、own-executor が起動される。'), title="パターンA（計画書の agent_hint で、gsd-executor を自作に置き換える）",
         verdict="結果）△　置き換えられるのは、/gsd-execute-phase の gsd-executor だけ。",
         setup=[".claude/agents/own-executor.md", "gsd-planner への指示:", "「計画書に agent_hint: own-executor を書く」"],
         cols={"plan": [G("gsd-planner", doc=["計画書 PLAN.md", "agent_hint: own-executor"])],
               "execute": [O("own-executor", "gsd-executor の代わりに起動される"), OFF("gsd-executor"),
                           G("gsd-verifier", "置き換わらない")],
               "verify": [G("gsd-debugger など", "置き換わらない")]},
         points=["① 置き換わるのは、/gsd-execute-phase の gsd-executor だけ（4 回中 4 回）。",
                 "② agent_hint に gsd-verifier など別のサブエージェントの名前を書いても、置き換わらない。",
                 "③ /gsd-quick と、--interactive を付けた /gsd-execute-phase では、置き換わらない。"]),
    dict(key="B", auto=('○', '使える（計画と実装の中は、単独のコマンドと同じ）', '使える。計画と実装の中は、単独のコマンドと同じに起動される。相談の discuss:pre・post だけ起動されない。'), title="パターンB（Capability の step で、ループポイントに自作を起動する）",
         verdict="結果）△〜○　ループポイントのある所は置き換えられる。gsd-planner と gsd-executor は置き換えられない。",
         setup=[".claude/agents/own-○○.md", "capability.json の steps:", '  { "point": "plan:pre",',
                '    "ref": { "agent": "own-researcher" } }', "config.json で既定のサブエージェントをオフ:",
                '  "research": false など'],
         cols=STEP_COLS(""),
         points=["① 自作を起動できるのは、ループポイントのあるコマンドだけ。/gsd-new-project など 19 コマンドでは起動されない。",
                 "② config.json で既定のサブエージェントをオフにすると置き換えになる。gsd-planner・gsd-executor はオフにできない。",
                 "③ step に止める力は無い。自作の plan-checker が問題を見つけても、gsd-planner への差し戻しは起きない。"]),
    dict(key="C", auto=('△', '使える（ただし plan:pre の skill が 2 回動く）', '使える。起動される場所はパターンB と同じ。ただし plan:pre の skill が 2 回動く。'), title="パターンC（Capability の step が fork skill を呼び、skill が自作を起動する）",
         verdict="結果）△〜○　起動される場所と置き換えられる範囲は、パターンB と同じ。",
         setup=[".claude/agents/own-○○.md", ".claude/skills/own-○○/SKILL.md", "  （context: fork・agent: own-○○）",
                "capability.json の steps:", '  { "point": "plan:pre",', '    "ref": { "skill": "own-researcher" } }',
                "config.json で既定のサブエージェントをオフ"],
         cols=STEP_COLS(" → skill"),
         points=["① パターンB との違いは、step が skill を呼び、その skill が自作を子として起動すること。",
                 "② skill も setup で .claude/skills/ に配置する（Capability に入れても配置されない）。",
                 "③ /gsd-autonomous では、plan:pre の skill が 2 回動く。"]),
    dict(key="D", auto=('○', '使える（起動された 8 体の全部が子を起動した）', '使える。指示を案件の CLAUDE.md で渡すと、起動された 8 体の全部が子を起動した。'), title="パターンD（GSD の既定のサブエージェントが、fork skill で自作の子を起動する）",
         verdict="結果）△　置き換えではない。既定のサブエージェントは必ず動き、作業の一部を自作の子に任せる形。",
         setup=[".claude/agents/own-○○.md（自作の子）", ".claude/skills/own-○○/SKILL.md（fork skill）",
                "既定のサブエージェントへの指示:", "「最初に Skill で own-○○ を呼ぶ」",
                "  案件の CLAUDE.md か、config の agent_skills"],
         cols={"np": [G("gsd-roadmapper", child="own-○○")], "plan": [G("gsd-planner", child="own-○○")],
               "execute": [G("gsd-executor", child="own-○○"), G("gsd-verifier", child="own-○○")],
               "verify": [G("gsd-debugger", child="own-○○")]},
         side=("execute",),
         points=["① 既定のサブエージェントは必ず動く。子が作業をしても、自分のルールで最後まで動く。",
                 "② 子を起動できるのは、Skill の道具を持つ 22 体だけ。残りの 14 体には、config の agent_tools で道具を追加する。",
                 "③ 指示に従わない回がある（gsd-plan-checker は 6 回中 3 回）。"]),
    dict(key="E", auto=('△', '一部だけ（実装の最後の verify:post だけ）', '一部だけ。起動されるのは実装の最後の verify:post だけで、相談の文は渡らない。'), title="パターンE（Capability の文でメインエージェントに頼み、自作を起動させる）",
         verdict="結果）△　使えるのは discuss・verify・ship の前後だけ。メインエージェントが文に従う保証は無い。",
         setup=[".claude/agents/own-○○.md", "capability.json の contributions:", '  { "point": "verify:pre",',
                '    "into": "orchestrator", … }', "文の例:", "「gsd-debugger の代わりに own-debugger を起動する」"],
         cols={"discuss": [O("own-○○", "discuss:pre・post の文（追加）")],
               "plan": [NONE("メインエージェント宛ての文を\n入れられない（インストールで止まる）")],
               "execute": [NONE("メインエージェント宛ての文を\n入れられない"), O("own-○○", "最後の verify:post の文だけ（追加）")],
               "verify": [O("own-debugger など", "verify:pre の文（既定の 3 つの代わり）"), OFF("gsd-debugger など")]},
         points=["① メインエージェントへの依頼文に「自作を起動する」と書く形。従うかはメインエージェントの判断で、保証は無い。",
                 "② 文を入れられるのは discuss・verify・ship の前後の 6 か所だけ。plan と execute には入れられない。",
                 "③ /gsd-verify-work では、gsd-debugger・gsd-planner・gsd-plan-checker が自作に置き換わった。"]),
]

# ---- シート 2 の文 ---------------------------------------------------------------------------
COMPARE_HEAD = [
    "【パターンA】\n計画書（PLAN.md）の agent_hint の欄に、自作のサブエージェントの名前を書く",
    "【パターンB】\ncapability.json の steps に、ループポイントと自作のサブエージェント（ref.agent）を書く",
    "【パターンC】\ncapability.json の steps に、ループポイントと fork skill（ref.skill）を書き、skill が自作を起動する",
    "【パターンD】\nGSD の既定のサブエージェントに「fork skill を呼ぶ」指示を渡し、自作を子として起動させる",
    "【パターンE】\ncapability.json の contributions に、メインエージェント宛ての「自作を起動する」文を書く",
]
COMPARE_ROWS = [
    ("置き換えられるサブエージェント", [
        ("△", "gsd-executor だけ。別のサブエージェントの名前を書いても置き換わらない"),
        ("△〜○", "ループポイントのある所の 9 体（調査・計画のチェック・コードレビュー・検証・監査）。gsd-planner と gsd-executor はオフにできない"),
        ("△〜○", "パターンB と同じ"),
        ("✕", "置き換えではない。既定のサブエージェントは必ず動き、自作は子として追加される"),
        ("△", "/gsd-verify-work の中の gsd-debugger・gsd-planner・gsd-plan-checker。メインエージェントが文に従った時だけ"),
    ]),
    ("使えるコマンドの範囲", [
        ("△", "/gsd-execute-phase だけ。/gsd-quick では置き換わらなかった。--interactive を付けると、メインエージェントが自分で実装し、gsd-executor は起動されない"),
        ("△", "ループポイントのある discuss・plan・execute・verify-work。/gsd-new-project・/gsd-quick-batch など 19 コマンドでは起動されない"),
        ("△", "パターンB と同じ"),
        ("○", "全部のコマンド（指示を案件の CLAUDE.md で渡した場合）。ループポイントの無いコマンドでも子を起動した。agent_skills で渡すと、渡らないコマンドがある"),
        ("△", "discuss・verify・ship の前後の 6 か所だけ。plan と execute には文を入れられない"),
    ]),
    ("/gsd-autonomous（人に聞かずに自動で進めるコマンド）で使えるか\n\n重要", [
        ("○", "使える。単独のコマンドと同じに起動される"),
        ("○", "使える。計画と実装の中は単独のコマンドと同じ。相談（smart discuss）の discuss:pre・post だけ起動されない"),
        ("△", "使える。パターンB と同じ。ただし plan:pre の skill が 2 回動く"),
        ("○", "使える。指示を案件の CLAUDE.md で渡すと、起動された 8 体の全部が子を起動した"),
        ("△", "一部だけ。実装の最後の verify:post だけ起動される。相談の文は渡らない"),
    ]),
    ("毎回、設定どおりに動くか\n\n重要", [
        ("○", "4 回中 4 回。GSD の手順書が agent_hint を読んで振り分ける"),
        ("○", "ループポイントのある所では毎回起動された。ただし step に止める力は無い"),
        ("○", "パターンB と同じ"),
        ("△", "サブエージェントが指示に従うかしだい。gsd-plan-checker は 6 回中 3 回"),
        ("△", "メインエージェントが文に従うかしだい。相談のモードによっては文が渡らなかった"),
    ]),
    ("GSD の設定を変えずに使えるか", [
        ("○", "GSD の正規の欄を使う。設定は変えない"),
        ("△", "置き換えるには、config.json で既定のサブエージェントをオフにする"),
        ("△", "パターンB と同じ"),
        ("△〜○", "変えない。Skill の道具が無い 14 体に使う時だけ、config の agent_tools で道具を追加する"),
        ("○", "変えない"),
    ]),
    ("案件ごとの setup で配置する物", [
        ("", "自作のサブエージェントの定義"),
        ("", "自作のサブエージェントの定義（Capability に入れても配置されない）"),
        ("", "自作のサブエージェントの定義と skill"),
        ("", "自作のサブエージェントの定義と skill、既定のサブエージェントへの指示の文"),
        ("", "自作のサブエージェントの定義"),
    ]),
]
OUTSIDE_TITLE = "参考）GSD の外の方法（Claude Code の仕組みと GSD の設定）"
OUTSIDE_HEAD = ["方法", "やること", "実機の結果", "使うときの注意"]
OUTSIDE_ROWS = [
    ("F　Claude Code の hook で起動を書き換える",
     "GSD が gsd-○○ を起動する直前に、hook（PreToolUse）で起動するサブエージェントを自作に書き換える",
     ("○", "全部のサブエージェントが自作に置き換わった。/gsd-autonomous で 10 回中 10 回、--auto で 9 回中 9 回。実装・人の確認・/gsd-quick でも全部"),
     "Claude Code 以外の実行環境には無い。hook の設定は setup で配置する。自作は GSD の約束（成果物・コミット）を守る必要がある。"
     "config の agent_skills の skill は、既定の名前（gsd-○○）の欄に書く"),
    ("G　同じ名前のファイルで上書きする",
     ".claude/agents/gsd-○○.md を自作の内容にする",
     ("△", "GSD は gsd-○○ を起動し、動いたのは自作の内容だった。/gsd-autonomous で 10 回中 10 回"),
     "GSD を案件に入れていると、再インストールや版上げで元に戻る"),
    ("D3　サブエージェントの起動時に hook で指示を挿入する",
     "gsd-○○ が起動された直後に、hook（SubagentStart）で「Skill で own-○○ を呼ぶ」を挿入する（パターンD の指示の渡し方）",
     ("○", "/gsd-autonomous と --auto で、Skill の道具を持つ 8 回中 8 回に挿入され、8 回とも子を起動した"),
     "Claude Code 以外の実行環境には無い。Skill の道具が無いサブエージェントには使えない"),
    ("agent_tools　サブエージェントに道具を追加する",
     "config.json の agent_tools に追加したい道具を書き、GSD を再インストールする",
     ("○", "Skill の道具が無かった gsd-pattern-mapper・gsd-debug-session-manager・gsd-doc-verifier も、パターンD で子を起動した"),
     "再インストールが要る（setup で行う）"),
    ("自作のサブエージェントに skill を持たせる",
     "自作の定義ファイル（.claude/agents/own-○○.md）の skills の欄に、skill の名前を書く",
     ("○", "どのパターンで起動しても、起動時に skill の本文が読み込まれた。config の agent_skills に自作の名前を書く形は、step や fork skill で起動した自作には渡らなかった"),
     "skill は .claude/skills/ に配置する（ほかの場所の skill は、Skill の道具で呼べない）。skill の allowed-tools は、道具の制限にならない"),
    ("Capability の gates　チェックして止める",
     "capability.json の gates に、ループポイントとスクリプトの判定を書き、止める設定（blocking: true）にする",
     ("○", "plan:post の gate が失敗を返すと、計画のコミットの後で止まり、実装は始まらなかった。/gsd-autonomous の下でも gate は実行された"),
     "止まっても STATE.md は「実行できる」のままなので、人が /gsd-execute-phase を打つと実装に進む想定（未確認）。サブエージェントに判定させる形（agentVerdict）は、止める設定にできない"),
]
MARK_COLOR = {"○": OK_GREEN, "△": GOLD, "△〜○": GOLD, "✕": RED, "": INK}


# =============================================================================================
#  セル（openpyxl）
# =============================================================================================
def new_workbook(theme_src):
    wb = Workbook()
    wb._fonts = IndexedList([Font(name="游ゴシック", sz=12, family=2, charset=128, scheme="minor")])
    with zipfile.ZipFile(theme_src) as z:
        wb.loaded_theme = z.read("xl/theme/theme1.xml")
    return wb


def grid_sheet(ws):
    """人の Excel と同じ方眼（細い列・高さ 20 の行）にする。目盛り線は出さない。"""
    ws.sheet_format.baseColWidth = 10
    ws.sheet_format.defaultColWidth = 3.7109375
    ws.sheet_format.defaultRowHeight = 20
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 85


class Rows:
    """シート 1 の行の割り当て。文字を書いた行は高さを決め、図を置く位置（pt）を計算できるようにする。"""

    def __init__(self, ws):
        self.ws, self.heights, self.r = ws, {}, 2

    def put(self, text, size, ht, col=2, bold=False, color=INK, band=False):
        c = self.ws.cell(row=self.r, column=col, value=text)
        c.font = Font(name=MEIRYO, sz=size, b=bold, color=color)
        c.alignment = Alignment(vertical="center")
        self.ws.row_dimensions[self.r].height = ht
        self.heights[self.r] = ht
        if band:
            for k in range(2, LAST_COL + 1):
                self.ws.cell(row=self.r, column=k).fill = PatternFill("solid", fgColor=BAND_FILL)
        self.r += 1

    def skip(self, n=1):
        self.r += n

    def y_of(self, row):
        """row（1 始まり）の上端の位置（pt）。"""
        emu = sum(round(self.heights[k] * 4 / 3) * PX_EMU if k in self.heights else ROW_EMU for k in range(1, row))
        return emu / EMU_PT

    def grid(self):
        custom = {k - 1: round(h * 4 / 3) * PX_EMU for k, h in self.heights.items()}
        return CellGrid(COL_EMU, ROW_EMU, custom_rows=custom)


def box_border(ws, top, bottom, left, right):
    """セルの外周に細い枠線を引く（結論の一覧の枠）。"""
    thin = Side(style="thin", color="000000")
    for r in range(top, bottom + 1):
        for c in range(left, right + 1):
            sides = dict(top=thin if r == top else None, bottom=thin if r == bottom else None,
                         left=thin if c == left else None, right=thin if c == right else None)
            if any(sides.values()):
                ws.cell(row=r, column=c).border = Border(**{k: v for k, v in sides.items() if v})


def sheet1_cells(ws):
    """シート 1 のセルの文字を書き、パターンごとの図の位置（左上の pt）を返す。"""
    grid_sheet(ws)
    ws.sheet_properties.tabColor = "FCE4D6"
    rows = Rows(ws)
    rows.put("1.この資料の結論", 18, 29, band=True)
    rows.skip()
    rows.put(LEAD, 14, 24)
    rows.skip()
    top = rows.r
    rows.skip()
    for line in CONCLUSIONS:
        rows.put(line, 14, 24, col=3)
    box_border(ws, top, rows.r, 2, 50)
    rows.skip(3)
    rows.put("2.自作のサブエージェントを起動する 5 つのパターン", 18, 29, band=True)
    rows.skip()
    for line in TERMS:
        rows.put(line, 11, 20, color=SUB)
    rows.skip()
    fig_rows = math.ceil((FH + 12) * EMU_PT / ROW_EMU)
    tops = []
    for p in PATTERNS:
        rows.put(p["title"], 18, 30)
        rows.put(p["verdict"], 12, 22, col=3)
        rows.put(f"/gsd-autonomous（自動で進めるコマンド）で使えるか）{p['auto'][0]}　{p['auto'][2]}", 12, 22, col=3)
        tops.append(rows.y_of(rows.r) + 6)
        rows.skip(fig_rows + 2)
    rows.put("以上", 12, 20)
    return rows, tops


def mark_cell(cell, mark, text, size=10):
    """「○」などの印を色つきで上に置き、その下に理由を書く（人の比較表と同じ形）。"""
    cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    cell.font = Font(name=MEIRYO, sz=size, color=INK)
    if not mark:
        cell.value = text
        return
    head = TextBlock(InlineFont(rFont=MEIRYO, sz=14, b=True, color=MARK_COLOR[mark]), mark)
    body = TextBlock(InlineFont(rFont=MEIRYO, sz=size, color=INK), f"\n\n（{text}）")
    cell.value = CellRichText(head, body)


def lines_of(text, per_line):
    return sum(max(1, math.ceil(len(p) / per_line)) for p in text.split("\n"))


def table_border(ws, top, bottom, left, right):
    thin = Side(style="thin", color="000000")
    for r in range(top, bottom + 1):
        for c in range(left, right + 1):
            ws.cell(row=r, column=c).border = Border(top=thin, bottom=thin, left=thin, right=thin)


def head_cell(cell, text, size=10):
    cell.value = text
    cell.font = Font(name=MEIRYO, sz=size, color=INK)
    cell.fill = PatternFill("solid", fgColor=HEAD_FILL)
    cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")


def sheet2_cells(ws):
    """パターンの比較表と、GSD の外の方法の表（どちらもセル）。"""
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 110
    ws.sheet_properties.tabColor = "E2EFDA"
    widths = {"A": 1.7, "B": 4.5, "C": 20, "D": 40, "E": 40, "F": 40, "G": 40, "H": 40}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    per_line = 21                                   # 幅 40 の列に入る、メイリオ 10 の全角の字数の目安
    r = 2
    head_cell(ws.cell(row=r, column=2), "No", 12)
    head_cell(ws.cell(row=r, column=3), "観点")
    for k, text in enumerate(COMPARE_HEAD):
        head_cell(ws.cell(row=r, column=4 + k), text)
    ws.row_dimensions[r].height = 76
    for n, (view, cells) in enumerate(COMPARE_ROWS, 1):
        r += 1
        c = ws.cell(row=r, column=2, value=n)
        c.font, c.alignment = Font(name=MEIRYO, sz=12), Alignment(horizontal="center", vertical="center")
        c = ws.cell(row=r, column=3)
        if "\n\n重要" in view:
            name = view.replace("\n\n重要", "")
            c.value = CellRichText(TextBlock(InlineFont(rFont=MEIRYO, sz=10, color=INK), name + "\n\n"),
                                   TextBlock(InlineFont(rFont=MEIRYO, sz=10, b=True, color=RED), "重要"))
        else:
            c.value = view
        c.font, c.alignment = Font(name=MEIRYO, sz=10, color=INK), Alignment(wrap_text=True, vertical="center", horizontal="center")
        need = 0
        for k, (mark, text) in enumerate(cells):
            mark_cell(ws.cell(row=r, column=4 + k), mark, text)
            need = max(need, lines_of(text, per_line) + (3 if mark else 0))
        ws.row_dimensions[r].height = max(48, need * 16 + 22)
    table_border(ws, 2, r, 2, 8)

    r += 3
    c = ws.cell(row=r, column=2, value=OUTSIDE_TITLE)
    c.font = Font(name=MEIRYO, sz=12, color=INK)
    r += 1
    top = r
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    head_cell(ws.cell(row=r, column=2), OUTSIDE_HEAD[0])
    for k, text in enumerate(OUTSIDE_HEAD[1:]):
        head_cell(ws.cell(row=r, column=4 + k), text)
    ws.row_dimensions[r].height = 26
    for name, what, (mark, result), caution in OUTSIDE_ROWS:
        r += 1
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        left = Alignment(wrap_text=True, vertical="center", horizontal="left")
        for col, text in ((2, name), (4, what), (6, caution)):
            c = ws.cell(row=r, column=col, value=text)
            c.font, c.alignment = Font(name=MEIRYO, sz=10, color=INK), left
        mark_cell(ws.cell(row=r, column=5), mark, result)
        need = max(lines_of(what, per_line), lines_of(result, per_line) + 3, lines_of(caution, per_line))
        ws.row_dimensions[r].height = max(48, need * 16 + 22)
    table_border(ws, top, r, 2, 6)


ROLE_ROWS = []          # own5_data.fill が入れる（ロール, A, B・C, D, E, 検証の名前）
ROLE_HEAD = ["GSD のサブエージェント（ロール）", "パターンA\nagent_hint", "パターンB・C\nCapability の step", "パターンD\n既定のサブエージェントからの委任",
             "パターンE\nメインエージェント宛ての文"]
ROLE_NOTES = [
    "○ = 実機で置き換わった（パターンD は、子を起動できた）。△ = 条件つき、または毎回ではない。✕ = できなかった。",
    "パターンD の数は「子を起動できた回 / そのサブエージェントが起動された回」。",
]


def sheet3_cells(ws):
    """ロールごとの結果（セルの表）。印の色は ○ = 緑、△ = 金、✕ = 赤。未検証の文は灰。"""
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 110
    ws.sheet_properties.tabColor = "DDEBF7"
    for col, w in {"A": 1.7, "B": 30, "C": 34, "D": 46, "E": 46, "F": 46}.items():
        ws.column_dimensions[col].width = w
    r = 2
    for note in ROLE_NOTES:
        c = ws.cell(row=r, column=2, value=note)
        c.font = Font(name=MEIRYO, sz=11, color=INK)
        r += 1
    r += 1
    top = r
    for k, text in enumerate(ROLE_HEAD):
        head_cell(ws.cell(row=r, column=2 + k), text)
    ws.row_dimensions[r].height = 40
    per_line = {3: 18, 4: 24, 5: 24, 6: 24}
    wrap = Alignment(wrap_text=True, vertical="center", horizontal="left")
    for name, *cells in ROLE_ROWS:
        r += 1
        c = ws.cell(row=r, column=2, value=name)
        c.font, c.alignment = Font(name=MEIRYO, sz=10, b=True, color=INK), wrap
        need = lines_of(name, 15)
        for k, (color, text) in enumerate(cells[:4]):
            c = ws.cell(row=r, column=3 + k)
            c.font, c.alignment = Font(name=MEIRYO, sz=10, color=INK), wrap
            if text[:1] in "○△✕":                     # 印だけに色を付け、理由は黒で書く
                c.value = CellRichText(TextBlock(InlineFont(rFont=MEIRYO, sz=12, b=True, color=color), text[:1]),
                                       TextBlock(InlineFont(rFont=MEIRYO, sz=10, color=INK), text[1:]))
            else:
                c.value = text
                c.font = Font(name=MEIRYO, sz=10, color=color)
            need = max(need, lines_of(text, per_line[3 + k]))
        ws.row_dimensions[r].height = max(30, need * 16 + 10)
    table_border(ws, top, r, 2, 6)


# =============================================================================================
#  図（図形）
# =============================================================================================
def item_box(d, it, x, y, w, h=ITEM_H):
    kind, name, sub = it["kind"], it["name"], it.get("sub")
    if kind in ("off", "none"):
        text = name.split("\n") if kind == "none" else [name, "（起動されない）"]
        s = v4.ghost(d, x, y, w, h, [[(t, {"size": 9})] for t in text],
                     name="できない所" if kind == "none" else "起動されない物")
        if kind == "off":
            d.cross(x + w - 16, y + h / 2, size=26, color=("tx1", 50, 50))
        return s
    head, fill, line = (("GSD のサブエージェント", GREEN, GREEN_LINE) if kind == "gsd"
                        else ("自作のサブエージェント", BLUE, BLUE_LINE))
    lines = [[(head, {"size": 8, "color": SUB})], [(name, {"bold": True})]]
    if sub:
        lines.append([(sub, {"size": 8.5, "color": SUB})])
    return v4.box(d, x, y, w, h, lines, fill=fill, line=line, size=10, name=f"サブエージェント {name}")


def draw_column(d, col, items, Y0, side, numbers):
    """1 つのコマンドの列を描く。上から、コマンド → メインエージェント → 起動される物。"""
    _, cx, cw, cmd, sub = col
    chev = d.shape(cx, Y0 + 20, cw, 61, "homePlate", fill=GREEN, line=GREEN_LINE, lw=0.75, adj=18000,
                   text=[[(cmd, {"bold": True})], sub], size=11, font=YU, color="000000", ins=(2, 0, 9, 2), name=cmd)
    ax = chev.site(2)[0]
    v4.line(d, "cmd", (chev, 2), (ax, Y0 + 144))
    v4.number(d, ax + 4, Y0 + 108, f"({next(numbers)})")
    spawned = [it for it in items if it["kind"] in ("gsd", "own")]
    if not items:
        return
    bar_bottom = Y0 + 185
    if spawned:
        label = f"({next(numbers)})"
    if side:                                         # 2 つを横に並べ、それぞれメインエージェントから直に起動する
        w = (cw - 36) / 2
        for k, it in enumerate(items):
            x = cx + 12 + k * (w + 12)
            s = item_box(d, it, x, Y0 + ITEM_TOP, w)
            v4.line(d, "spawn", (s.site(0)[0], bar_bottom), (s, 0))
            if k == 0:
                v4.number(d, s.site(0)[0] + 4, bar_bottom + 6, label)
            draw_child(d, it, s, x, Y0 + ITEM_TOP, w)
        return
    if len(items) == 1:
        it = items[0]
        w = min(cw - 24, 190)
        x = cx + (cw - w) / 2
        s = item_box(d, it, x, Y0 + ITEM_TOP, w)
        if spawned:
            v4.line(d, "spawn", (s.site(0)[0], bar_bottom), (s, 0))
            v4.number(d, s.site(0)[0] + 4, bar_bottom + 6, label)
        draw_child(d, it, s, x, Y0 + ITEM_TOP, w)
        return
    tx, x, w = cx + 14, cx + 34, cw - 46                 # 縦に並べ、幹から枝で入れる
    last = None
    for k, it in enumerate(items):
        y = Y0 + ITEM_TOP + k * (ITEM_H + ITEM_GAP)
        s = item_box(d, it, x, y, w)
        if it["kind"] in ("gsd", "own"):
            last = s
            d.connector((tx, s.site(1)[1]), (s, 1), color=LINES["spawn"][0], lw=LINES["spawn"][1], name="起こす矢印の枝")
    if last is not None:
        d.connector((tx, bar_bottom), (tx, last.site(1)[1]), color=LINES["spawn"][0], lw=LINES["spawn"][1], tail=False,
                    name="起こす矢印の幹")
        v4.number(d, tx + 4, bar_bottom + 6, label)


def draw_child(d, it, parent, x, y, w):
    """既定のサブエージェントが起動する自作の子（パターンD）と、書く計画書（パターンA）。"""
    if it.get("child"):
        child = item_box(d, O(it["child"], "fork skill の子"), x, y + ITEM_H + 24, w)
        v4.line(d, "spawn", (parent, 2), (child, 0))
    if it.get("doc"):
        lines = [[(it["doc"][0], {"bold": True})]] + [[(t, {"color": v4.PURPLE})] for t in it["doc"][1:]]
        paper = v4.doc(d, x, y + ITEM_H + 24, w, 56, lines, size=9, name="計画書")
        v4.line(d, "write", (parent, 2), (paper, 0))


def legend(d, x, y, kinds):
    with d.group("凡例"):
        d.text(x, y, 120, 18, "凡例", size=11, font=UD, color=INK, bold=True, name="凡例の見出し")
        y += 22
        for kind in kinds:
            v4.line(d, kind, (x, y + 9), (x + 34, y + 9), tail=kind != "boundary")
            d.text(x + 40, y, 290, 18, LINES[kind][3], size=9.5, font=UD, color=INK, name="凡例の文")
            y += 19
        d.shape(x, y + 2, 16, 14, "roundRect", fill=GREEN, line=GREEN_LINE, lw=0.75, adj=8000, name="凡例の箱")
        d.shape(x + 18, y + 2, 16, 14, "roundRect", fill=BLUE, line=BLUE_LINE, lw=0.75, adj=8000, name="凡例の箱")
        d.text(x + 40, y, 290, 18, "緑の箱 = GSD の物　青の箱 = 自作の物", size=9.5, font=UD, color=INK, name="凡例の文")
        y += 19
        d.shape(x, y + 2, 34, 14, "flowChartDocument", fill=BLUE, line=BLUE_LINE, lw=0.75, dash="dash", name="凡例の箱")
        d.text(x + 40, y, 290, 18, "書類の形 = 読む物・書く物（setup が配置する物・計画書）", size=9.5, font=UD, color=INK, name="凡例の文")
        y += 19
        d.shape(x, y + 2, 34, 14, "roundRect", fill=v4.GHOST_FILL, line=v4.GHOST_LINE, lw=1, dash="dash", adj=8000,
                name="凡例の箱")
        d.text(x + 40, y, 290, 18, "灰の点線の箱 = 起動されない物・できない所", size=9.5, font=UD, color=INK, name="凡例の文")
    return y + 19


def figure(p, Y0):
    d = Drawing(tag="own5" + p["key"], name="パターン" + p["key"])
    d.shape(FX, Y0, FW, FH, "rect", fill=None, line="1F2937", lw=1.5, name="図の枠")
    d.text(FX + 44, Y0 + 82, 170, 20, "人（入力するコマンド）", size=11, font=UD, color=SUB, name="段の名前")
    d.connector((FX + 22, Y0 + 104), (FX + FW - 12, Y0 + 104), color="A6A6A6", lw=1, tail=False, name="区切り線")
    d.text(FX + 44, Y0 + 108, 120, 20, "裏側の処理", size=11, font=UD, color=SUB, name="段の名前")
    v4.box(d, BAR_X, Y0 + 144, BAR_W, 41, ["メインエージェント"], size=14, name="メインエージェント")
    with d.group("コマンドごとの境目"):
        for _, cx, _, _, _ in CMDS[1:]:
            v4.line(d, "boundary", (cx - 6, Y0 + 8), (cx - 6, Y0 + 140), tail=False)
            v4.line(d, "boundary", (cx - 6, Y0 + 190), (cx - 6, Y0 + FH - 148), tail=False)
    mark, short, _ = p["auto"]
    color = MARK_COLOR[mark]
    d.shape(FX + 22, Y0 + 18, 306, 50, "roundRect", fill="FFFFFF", line=color, lw=1.5, adj=12000, align="l",
            text=[[("/gsd-autonomous（自動で進めるコマンド）", {"bold": True, "size": 9.5})],
                  [(f"{mark} {short}", {"bold": True, "color": color})]],
            size=10, font=YU, color=INK, ins=(8, 3, 6, 3), name="autonomous で使えるか")
    numbers = iter(range(1, 40))
    for col in CMDS:
        draw_column(d, col, p["cols"].get(col[0], []), Y0, col[0] in p.get("side", ()), numbers)

    lines = [[("setup が配置する物（案件ごとに 1 回）", {"bold": True})]] + p["setup"]
    h = 30 + 14 * len(p["setup"])
    paper = v4.doc(d, FX + 22, Y0 + 132, 306, h, lines, size=9, name="setup が配置する物", align="l")
    v4.line(d, "read", (BAR_X, Y0 + 164), (paper.site(3)[0], Y0 + 164))
    kinds = ["cmd", "spawn", "read"] + (["write"] if p["key"] == "A" else []) + ["boundary"]
    legend(d, FX + 22, Y0 + 132 + h + 26, kinds)

    text = [[("ポイント）", {"bold": True})]] + p["points"]
    d.shape(FX + 372, Y0 + FH - 136, FW - 392, 120, "rect", fill=POINT_FILL, line=POINT_LINE, lw=1, text=text, size=11,
            font="Meiryo", color="000000", align="l", anchor="t", ins=(8, 5, 8, 5), name="吹き出し 要点")
    # この方法が公式ドキュメントのどこに書かれているか（凡例の下、ポイントの箱の左）
    doc_refs.ref_box(d, FX + 22, Y0 + FH - 16 - doc_refs.height(p["key"]), 336, p["key"])
    return d


# =============================================================================================
def build(theme_src, dst):
    wb = new_workbook(theme_src)
    ws1 = wb.active
    ws1.title = SHEETS[0]
    rows, tops = sheet1_cells(ws1)
    sheet2_cells(wb.create_sheet(SHEETS[1]))
    sheet3_cells(wb.create_sheet(SHEETS[2]))
    tmp = dst + ".cells.xlsx"
    wb.properties.creator = None  # 作成者の欄に「openpyxl」を出力しない
    wb.save(tmp)
    part = ensure_drawing(tmp, tmp)
    drawings = [figure(p, y) for p, y in zip(PATTERNS, tops)]
    write_into(tmp, dst, drawings, drawing_part=part, grid=rows.grid())
    os.remove(tmp)
    return tops


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import own5_data

    class Shim:           # own5_data.fill が書き込む先（ロールごとの表だけを使う）
        OK_GREEN, GOLD, RED, SUB, INK = OK_GREEN, GOLD, RED, SUB, INK
        T_, ROLE_ROWS, FIRE_ROWS, HEAD_CONCLUSION, VERIFY_NOTE, CONCLUSION, TEXT_TABLES = {}, [], [], [], [], [], []

    own5_data.fill(Shim)
    ROLE_ROWS[:] = Shim.ROLE_ROWS
    tops = build(sys.argv[1], sys.argv[2])
    print(f"書きました: {sys.argv[2]}")
    for p, y in zip(PATTERNS, tops):
        print(f"  パターン{p['key']}: y {y:.0f}〜{y + FH:.0f}")
