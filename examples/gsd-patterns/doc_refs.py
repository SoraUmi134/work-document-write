"""パターンごとの「公式ドキュメントの記載場所」の箱。

GSD に処理を挿入する方法（agent_skills・Capability の contributions・steps・agent_hint）が、
GSD の公式サイト（docs.opengsd.net）と GitHub の docs（open-gsd/gsd-core）のどこに書かれているかを、
図の中にリンクの札として並べる。build_own5.py（自作のサブエージェントを起動する 5 つの方法）と
add_doc_refs.py（GSD に独自処理を挟む方法の検討）の両方が使う。

リンク先は、GitHub は v1.23.0 のタグで固定した。docs.opengsd.net は gsd-core の全ページを検索し、
載っていたのは agent_skills（Configuration › Integrations）だけだった。
"""
GH = "https://github.com/open-gsd/gsd-core/blob/v1.23.0/docs/"
MANIFEST = GH + "reference/capability-manifest.md"
SITE_SKILLS = "https://docs.opengsd.net/core/configuration/integrations#custom-agent-skills-injection"
CC_FORK = "https://code.claude.com/docs/en/skills#run-skills-in-a-subagent"

TITLE = "公式ドキュメントの記載場所"
GH_HEAD = ("head", "GitHub の docs（gsd-core v1.23.0）")
SITE_NONE = ("head", "docs.opengsd.net: 記載なし")
SITE_HEAD = ("head", "docs.opengsd.net")
SITE_LINK = ("link", "・Integrations「Custom agent skills injection」", SITE_SKILLS)
GH_SKILLS = ("link", "・CONFIGURATION.md「Agent Skills Injection」", GH + "CONFIGURATION.md#agent-skills-injection")
STEPS = ("link", "・capability-manifest.md「steps」", MANIFEST + "#steps")
POINTS = ("link", "・capability-manifest.md「Valid point values」", MANIFEST + "#valid-point-values")
CONTRIB = ("link", "・capability-manifest.md「contributions」", MANIFEST + "#contributions")
INTO = ("link", "・capability-manifest.md「Conformance invariants」", MANIFEST + "#conformance-invariants")
CC_HEAD = ("head", "Claude Code の docs（fork skill は Claude Code の機能）")
CC_LINK = ("link", "・skills「Run skills in a subagent」", CC_FORK)

# キー: 1〜3 = 「GSD に独自処理を挟む方法の検討」のパターン、A〜E = 「自作のサブエージェントを起動する 5 つの方法」のパターン
REFS = {
    "1": [SITE_HEAD, SITE_LINK, GH_HEAD, GH_SKILLS],
    "2": [GH_HEAD, CONTRIB, POINTS, INTO, SITE_NONE],
    "3": [GH_HEAD, STEPS, POINTS,
          ("link", "・how-to/develop-a-capability.md「Add hooks」", GH + "how-to/develop-a-capability.md#add-hooks"),
          SITE_NONE],
    "A": [GH_HEAD,
          ("link", "・plan-md.md「Per-plan executor routing」", GH + "reference/plan-md.md#per-plan-executor-routing"),
          ("link", "・how-to/route-a-plan-to-a-specialist-executor.md",
           GH + "how-to/route-a-plan-to-a-specialist-executor.md"),
          SITE_NONE],
    "B": [GH_HEAD, STEPS, POINTS,
          ("link", "・capability-manifest.md「skills and agents」", MANIFEST + "#skills-and-agents"),
          SITE_NONE],
    "C": [GH_HEAD, STEPS, POINTS, CC_HEAD, CC_LINK, SITE_NONE],
    "D": [GH_HEAD, GH_SKILLS, SITE_HEAD, SITE_LINK, CC_HEAD, CC_LINK],
    "E": [GH_HEAD, CONTRIB, INTO, SITE_NONE],
}

LINK_BLUE = "0563C1"


def pitch(size):
    """1 行の高さ（pt）。"""
    return size + 5


def height(key, size=9):
    """箱の高さ（pt）。題の 1 行と、REFS の行数から決まる。"""
    return 10 + (len(REFS[key]) + 1) * pitch(size)


def ref_box(d, x, y, w, key, size=9, font="Meiryo", ink="222222"):
    """(x, y) を左上にして、記載場所の箱を描く。リンクの行は下線付きの青字で、クリックで該当の節が開く。"""
    step, h = pitch(size), height(key, size)
    with d.group("公式ドキュメントの記載場所"):
        d.shape(x, y, w, h, "rect", fill="FFFFFF", line="7F7F7F", lw=0.75, name="記載場所の枠")
        d.text(x + 8, y + 5, w - 16, step, TITLE, size=size, font=font, color=ink, bold=True, wrap="none",
               name="記載場所の題")
        for k, row in enumerate(REFS[key], start=1):
            top = y + 5 + k * step
            if row[0] == "link":
                d.text(x + 8, top, w - 16, step, row[1], size=size, font=font, color=LINK_BLUE, underline=True,
                       link=row[2], wrap="none", name="参考リンク")
            else:
                d.text(x + 8, top, w - 16, step, row[1], size=size, font=font, color=ink, wrap="none",
                       name="記載場所の見出し")
    return h
