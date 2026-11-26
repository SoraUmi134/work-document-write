"""build_own5.py の表・結論・可変の文。GSD 1.23.0 の実機の結果（trials-v2/own-*）だけを書く。
数は「子を起動できた回 / ロールが起動された回」。コピーの名前は trials-v2/own-<名前>。
"""

# ---- 結果待ちだった所（結果が出たら、ここを修正する） ----
A7_FACT = ("案件の CLAUDE.md で頼んだ回（A7）は、quick の計画書に agent_hint: own-a-executor が書かれた。"
           "それでも起動されたのは gsd-executor だった（仕様の「quick は対象外」と一致）。")
E_EXEC_SUB = "execute-phase の最後の確認（verify:post）でも起動された（追加）"
E_EXEC_FACT = ("execute-phase の verify:post の文で gsd-ui-auditor の置き換えを頼んだ回（E-rep-exec）は、own-e-ui-auditor が起動され、"
               "gsd-ui-auditor は起動されなかった。ただし UI-REVIEW.md は書かれなかった。")
E_EXEC_SHORT = "ui-auditor は own-e-ui-auditor に置き換わった（UI-REVIEW.md は書かれなかった）"
ADVISOR = {"bc": ("BF8F00", "△ 通常・advisor モードでは discuss:pre・post で自作が起動された。advisor-researcher をオフにするキーは無い"
                         "（USER-PROFILE.md が無いと起動されない）。assumptions モードはポイント無し。"),
           "d": ("38761D", "○ advisor-researcher は CLAUDE.md 3/3・agent_skills 4/4。assumptions-analyzer は 1/1・1/1。"
                            "fork skill そのものを agent_skills に登録した形では、advisor-researcher は子を起動しなかった（0/4）。"),
           "e": ("BF8F00", "△ advisor-researcher の置き換えを discuss:pre の文で頼んだ回は、メインが discuss:pre の処理（render-hooks）を"
                         "実行せず、文が渡らなかった。gsd-advisor-researcher が 4 回起動された（追加の形は L1-advisor で起動された）。")}


def fill(m):
    O, G, X, N = m.OK_GREEN, m.GOLD, m.RED, m.SUB

    m.T_.update({
        "A_fact1": "計画書に agent_hint を書くと own-a-executor が起動され、gsd-executor は起動されなかった（4 回中 4 回）。",
        "A_quick_box": ["/gsd-quick では、", "executor を置き換えられ", "なかった"],
        "A_quick_fact": "quick の planner には Capability の contribution が渡らず、計画書に agent_hint が書かれなかった（A6）。" + A7_FACT,
        "D_comply": "plan-checker は、CLAUDE.md の指示で 6 回中 3 回、agent_skills で 3 回中 0 回だけ子を起動した。"
                    "ui-checker・integration-checker・ui-auditor・code-reviewer にも、指示を読んだのに子を起動しない回があった。",
        "E_exec_sub": E_EXEC_SUB,
        "D_tools_red": "道具は Capability からは足せない。config の agent_tools に書いて GSD を再インストールすると足せる（表4。"
                       "debug-session-manager で子を起動できた）。",
        "E_rep": "verify-work（verify:pre の文）では、メインが own-e-debugger・own-e-planner・own-e-plan-checker を起動し、"
                 "既定の 3 ロールは起動されなかった（E-rep-verify）。" + E_EXEC_FACT +
                 "advisor モードの discuss では、メインが discuss:pre の処理を実行せず、文が渡らなかった（E-rep-advisor）。",
    })

    m.ROLE_ROWS[:] = [
        ("gsd-executor（実装）",
         (O, "○ execute-phase で置き換わった（4/4 回: worktree あり・なし、計画書に直接書く・planner に書かせる）。"
             "agent_hint_routing=false では置き換わらない。/gsd-quick では置き換わらなかった。"),
         (G, "△ オフにするキーが無い。execute:wave:pre で自作を起動しても、gsd-executor は必ず起動された。"),
         (O, "○ CLAUDE.md 2/2、agent_skills 2/3。"),
         (X, "✕ execute のポイントには文を入れられない（インストールで止まる）。"),
         "A1-wt・A2-seq・A3-off・A5-planner・A6-quick・A7-quick・L1-exec・R-ctrl-exec・D-exec・D2-quick"),
        ("gsd-planner（計画）",
         (X, "✕ executor のロールにしか使えない。"),
         (G, "△ オフにできない。plan:pre・plan:post で自作を追加することはできる。"),
         (O, "○ CLAUDE.md 6/6、agent_skills 3/3（agent_skills は依頼文に入らず、自分で指示のファイルを探した回を含む）。"),
         (G, "△ 修正の計画（verify-work）では、メイン宛ての文で own-e-planner に置き換わった。/gsd-plan-phase には文を入れられない。"),
         "R-ctrl-plan・L1-plan・D-plan・D2-quick・D2-verify・E-rep-verify"),
        ("gsd-plan-checker（計画のチェック）",
         (X, "✕"),
         (G, "△ plan_check=false ＋ plan:post で置き換わった。ただし planner への差し戻しの往復は起きなかった。"),
         (G, "△ CLAUDE.md 3/6、agent_skills 0/3（読んでも子を起動しない回が多い）。"),
         (G, "△ verify-work（verify:pre の文）で own-e-plan-checker に置き換わった。/gsd-plan-phase には文を入れられない。"),
         "R-plan-b・R-plan-c・R-ctrl-plan・D-plan・D2-quick・E-rep-verify"),
        ("gsd-phase-researcher・gsd-pattern-mapper（計画の前の調査）",
         (X, "✕"),
         (O, "○ research=false・pattern_mapper=false ＋ plan:pre で置き換わり、planner は自作の RESEARCH.md・PATTERNS.md を読んだ。"),
         (G, "△ researcher は CLAUDE.md 1/1・agent_skills 1/2。pattern-mapper は Skill が無く ✕。"
             "config の agent_tools で Skill を追加すると、pattern-mapper も子を起動した（1/1）。"),
         (X, "✕ plan のポイントには文を入れられない。"),
         "R-plan-b・R-plan-c・R-ctrl-plan・D-plan・D2-quick・HK-AT-pmr"),
        ("gsd-ui-researcher・gsd-ui-checker（UI の決め事）",
         (X, "✕"),
         (G, "△ /gsd-ui-phase にはポイントが無い。plan-phase で ui_phase=false ＋ plan:pre にすると置き換わり、planner は自作の UI-SPEC.md を読んだ。"),
         (G, "△ CLAUDE.md は 2 ロールとも 1/1。agent_skills は researcher 1/1、checker 0/1。"),
         (X, "✕"),
         "L1-ui・R-ui-b・R-ui-c・R-ctrl-ui・D-ui・D2-ui"),
        ("gsd-code-reviewer（コードレビュー）",
         (X, "✕"),
         (O, "○ code_review=false ＋ execute:post で置き換わった（自作が REVIEW.md を書いた）。"),
         (G, "△ CLAUDE.md 2/2、agent_skills 1/3。"),
         (X, "✕ execute のポイントには文を入れられない。"),
         "R-exec-b・R-exec-c・R-ctrl-exec・D-exec・D-livedom・D2-quick"),
        ("gsd-code-fixer（指摘の修正）",
         (X, "✕"),
         (X, "✕ /gsd-code-review --fix にはポイントが無い。"),
         (G, "△ CLAUDE.md 1/1。agent_skills は依頼文に入らなかった（0/1）。"),
         (X, "✕"),
         "L1-crfix・D-crfix・D2-crfix"),
        ("gsd-verifier（フェーズの検証）",
         (X, "✕ gsd-verifier の名前を書いても置き換わらない。"),
         (O, "○ verifier=false ＋ execute:post で置き換わった。GSD の手順書を読んだ限りではこのキーを読む所が見つからなかったが、実機ではオフにすると gsd-verifier は起動されなかった。"),
         (O, "○ CLAUDE.md 2/2、agent_skills 2/3。"),
         (X, "✕"),
         "A4-gsdname・R-exec-b・R-exec-c・R-ctrl-exec・D-exec・D2-quick"),
        ("gsd-security-auditor・gsd-nyquist-auditor・gsd-ui-auditor（実装後の監査）",
         (X, "✕"),
         (G, "△ execute-phase の中では、各キーを false ＋ verify:post で置き換わった。/gsd-secure-phase・/gsd-validate-phase・/gsd-ui-review を単独で実行するとポイントが無い。"),
         (G, "△ ui-auditor は CLAUDE.md 2/2・agent_skills 2/3。security・nyquist は CLAUDE.md 1/1・agent_skills 0/1"
             "（/gsd-secure-phase・/gsd-validate-phase では agent_skills が依頼文に入らない）。"),
         (G, "△ verify:post に文は入る（execute-phase の最後で own-e-verify-post が起動された）。置き換え: " + E_EXEC_SHORT + "。"),
         "R-exec-b・R-exec-c・L1-sec2・L1-val2・L1-uireview・E-rep-exec・D-sec3・D-val3・D2-sec3・D2-val3"),
        ("gsd-debugger・gsd-debug-session-manager（不具合の調査）",
         (X, "✕"),
         (X, "✕ verify-work の不具合の調査・/gsd-debug の場所にはポイントが無い。"),
         (G, "△ debugger は CLAUDE.md 2/2・agent_skills 0/2（入らない）。debug-session-manager は Skill が無く ✕。"),
         (O, "○ verify-work（verify:pre の文）で own-e-debugger に置き換わった。/gsd-debug には文を入れる場所が無い。"),
         "L1-verify・L1-debug・D-verify・D2-verify・D2-debug・E-rep-verify"),
        ("gsd-project-researcher・gsd-research-synthesizer・gsd-roadmapper（案件の開始）",
         (X, "✕"),
         (X, "✕ /gsd-new-project にはポイントが無い。"),
         (G, "△ CLAUDE.md 6/6。agent_skills は defaults.json に書いても渡らなかった（0/6）。"),
         (X, "✕"),
         "L1-np・D-np・D2-np"),
        ("gsd-advisor-researcher・gsd-assumptions-analyzer（決め事の相談）",
         (X, "✕"),
         ADVISOR["bc"],
         ADVISOR["d"],
         ADVISOR["e"],
         "L1-discuss・L1-assume・D-assume・D2-assume・L1-advisor・D2-advisor・D-advisor"),
        ("gsd-codebase-mapper・gsd-integration-checker・gsd-doc-writer・gsd-eval-auditor",
         (X, "✕"),
         (X, "✕ map-codebase・audit-milestone・docs-update・eval-review にはポイントが無い。"),
         (G, "△ CLAUDE.md は 4 ロールとも全回（mapper 4/4・checker 1/1・writer 6/6・auditor 1/1）。agent_skills は mapper 2/4・checker 0/1。"),
         (X, "✕"),
         "L1-mapcb・L1-audit・L1-docs・L1-evalrev・D-*・D2-*"),
        ("Skill の無いロール: doc-verifier・doc-classifier・doc-synthesizer・framework-selector・ai-researcher・"
         "domain-researcher・eval-planner・dom-verifier・behavior-verifier",
         (X, "✕"),
         (G, "△ これらが起動されるコマンドにはポイントが無い。dom-verifier・behavior-verifier は GSD 自身が step で起動するロールなので、"
             "同じポイントに自作を配置すれば代わりは組める（既定はオフ）。"),
         (X, "✕ Skill の道具が無く、指示を読んでも子を起動しなかった。"),
         (X, "✕"),
         "L1-docs・L1-ingest・L1-ai2・L1-livedom・L1-deepv・D2-*"),
        ("gsd-mempalace-curator・gsd-user-profiler",
         (X, "✕"),
         (N, "未検証。curator は ship:post の後（push と PR の後）にしか起動されず、git push はしない約束なので実行していない。"
             "ship:pre では B・C・E とも起動された。"),
         (N, "未検証（2 ロールとも Skill が無い）。"),
         (N, "未検証。"),
         "L1-verify0（ship）・profile-user は PC 全体の設定に書き込むため実行していない"),
        ("gsd-intel-updater",
         (X, "✕"),
         (G, "△ 起動する手順書が GSD に無い。/gsd-map-codebase --query refresh で、メインが自分の判断で起動した（1 回）。"
             "plan:pre の step で、gsd-intel-updater か自作を起動する形は動いた。"),
         (O, "○ config の agent_tools で Skill を追加すると、子を起動した（1/1）。"),
         (N, "未検証。"),
         "HK-IN-0・IN-f2・IN-d・IN-b2r・IN-b3r"),
    ]

    m.FIRE_ROWS[:] = [
        ("/gsd-new-project（リサーチあり）", {}, "ポイント無し。"),
        ("/gsd-discuss-phase（通常）", {"discuss:pre": "B C E", "discuss:post": "B C E"}, "既定のサブエージェントは起動されない。"),
        ("/gsd-discuss-phase（assumptions モード）", {}, "ポイント無し。"),
        ("/gsd-plan-phase", {"plan:pre": "B C", "plan:post": "B C"}, "E は plan に文を入れられない。"),
        ("/gsd-ui-phase", {}, "ポイント無し。"),
        ("/gsd-execute-phase", {"execute:pre": "B C", "wave:pre": "B C", "wave:post": "B C", "execute:post": "B C",
                                "verify:post": "B C E"}, "最後の確認の verify:post では E も入る。"),
        ("/gsd-verify-work（不具合 1 件）", {"verify:pre": "B C E"},
         "不具合があると verify:post は起きない。修正の計画の plan:pre・plan:post も起きない。"),
        ("/gsd-verify-work（不具合 0 件）", {"verify:pre": "B C E", "verify:post": "B C E"}, ""),
        ("/gsd-quick --full", {"execute:post": "B C"}, "計画と実装の間のポイントは起きない。"),
        ("/gsd-ship（リモート無し）", {"ship:pre": "B C E"}, "push の前で止まり、ship:post は起きない。"),
        ("/gsd-code-review --fix・audit-milestone・map-codebase・debug・docs-update・ingest-docs・"
         "ai-integration-phase・eval-review・ui-review・secure-phase・validate-phase", {}, "どれもポイント無し。"),
    ]

    m.HEAD_CONCLUSION[:] = [
        "結論: GSD の中の方法（A〜E）は、1 つで全部のロールを置き換えられない。ロールによって使える方法が違う。",
        "A は executor だけ。B・C はループポイントのある所のロール。E は verify-work の中のロール（debugger など）。",
        "D は置き換えではなく、既定のロールが自作の子に任せる形で、ポイントの無いコマンドのロールはこれしか無い。",
        "GSD の外の方法（表4）: Claude Code の hook で起動を書き換える F は、全コマンド・全ロールに効く。",
        "autonomous（表3）: 自作も対象になる。計画・実装のポイント・委任は単独のコマンドと同じに起きる。",
        "  autonomous の相談（smart discuss）はループポイントを読まず、discuss:pre・post の自作は起動されない。",
        "どの方法でも、自作の定義（と hook の設定）は setup で .claude/ に配置する必要がある。",
    ]
    m.VERIFY_NOTE[:] = [
        "検証の方法: 小さな案件（数を数える静的なページ）を GSD 1.23.0 で作り、コマンドと方法ごとに案件をコピーして実行した（約 100 本）。",
        "実行は claude -p（Claude Code 2.1.332）。会話の記録から、起動されたサブエージェントの種類と回数を数えた。",
        "A〜E の約 80 本: メインは Sonnet。サブエージェントは GSD の model_profile の指定が優先された。",
        "  （planner は Opus、plan-checker・ui-auditor は Haiku、ほかは Sonnet）",
        "表3・表4 の約 20 本（autonomous・--auto・hook・agent_tools）: メイン・サブエージェントとも Opus 5.5。",
        "  （CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1 でそろえた）",
    ]
    m.CONCLUSION[:] = [
        [("結論: ", {"bold": True}), ("どの方法も、自作の定義（と skill）は setup で .claude/ に配置する必要がある。", {})],
        [("  ", {}), ("Capability からは配置されない（#5738 は 1.23.0 でも未実装）。", {})],
        [("・ 置き換わった: ", {"bold": True}), ("executor（A）。", {})],
        [("  ", {}), ("researcher・pattern-mapper・plan-checker・code-reviewer・verifier（B・C）。", {})],
        [("  ", {}), ("security・nyquist・ui の 3 つの監査と、ui-researcher（B・C）。", {})],
        [("  ", {}), ("B・C は、既定のロールを config でオフにし、同じポイントで起動する形。", {})],
        [("  ", {}), ("debugger と、修正の計画の planner・plan-checker（E。verify-work のメイン宛ての文）。", {})],
        [("・ 置き換わらなかった: ", {"bold": True}), ("planner と executor の config でのオフ（A は executor の差し替えで、オフではない）。", {})],
        [("  ", {}), ("ポイントの無いコマンドのロール。", {})],
        [("  ", {}), ("（new-project・ui-phase・code-review --fix・debug・map-codebase など）", {})],
        [("  ", {}), ("これらは D（既定のロールが子に任せる）しか無く、Skill の無い 14 ロールは D も使えない。", {})],
        [("・ 毎回ではない: ", {"bold": True}), ("D と E は、サブエージェントやメインが指示に従うかしだい。", {})],
        [("  ", {}), ("例: plan-checker は 6 回中 3 回。B・C の step も止める力は無い（止めるのは Capability の gates）。", {})],
        [("・ GSD の外の方法（表4）: ", {"bold": True}), ("Claude Code の hook で起動を書き換える F は、全ロールを確実に置き換えられる。", {})],
        [("  ", {}), ("オフにできない planner・executor も対象。SubagentStart の hook で指示を挿入する D3 も確実。", {})],
        [("  ", {}), ("Skill の無いロールは、config の agent_tools で道具を足せる。", {})],
        [("・ autonomous（表3）: ", {"bold": True}), ("自作を入れても止まらずに進み、計画・実装の中のポイント・委任は単独のコマンドと同じに起きた。", {})],
        [("  ", {}), ("相談（smart discuss）だけはポイントの処理が無く、discuss:pre・post の自作は起動されない。", {})],
    ]
    m.TEXT_TABLES[:] = [auto_table(m), other_table(m)]


# ---- 表3: autonomous（/gsd-autonomous）と --auto の下での結果 ----
def auto_table(m):
    O, G, X, N, I = m.OK_GREEN, m.GOLD, m.RED, m.SUB, m.INK
    return {
        "tag": "own5T3", "name": "表3 autonomous",
        "title": "表3　autonomous（/gsd-autonomous）と --auto の下で、自作が起動されたか（GSD 1.23.0・Opus 5.5）",
        "notes": [
            "/gsd-autonomous は、フェーズごとに 相談（smart discuss）→ UI の設計書 → 計画 → 実装 → レビュー を進める。",
            "計画以降はメインが Skill で呼ぶ。人に聞くのは判断が要る所だけ。検証: フェーズ 2（画面）を --only 2 で実行（8 本）。",
            "--auto は /gsd-discuss-phase 2 --auto で、相談→計画→実装をつなぐ（3 本）。",
            "○（緑）= 単独のコマンドと同じに起動された。△（金）= 一部だけ。空欄 = その組は検証していない。",
            "コピー = 検証用コピーの名前（削除済み）。根拠は会話の記録 ~/.claude/projects/…trials-v2-own-<名前>。",
        ],
        "cols": [("方法", 150), ("/gsd-autonomous --only 2 で起動された所", 420), ("単独のコマンドとの違い・気づいたこと", 420),
                 ("--auto（discuss → plan → execute）", 300), ("コピー", 160)],
        "rows": [
            [(I, "A agent_hint"), (O, AU_A), (I, AU_A_NOTE), (N, ""), (N, "AU-a")],
            [(I, "B step（agent）"),
             (O, "○ plan:pre・plan:post・execute:pre・wave:pre・wave:post・execute:post・verify:post の 7 か所で起動（単独のコマンドと同じ）。discuss:pre・post は起きない。"),
             (I, "smart discuss（autonomous の相談）はループポイントの処理を読まない。verify:pre は verify-work を通らないので起きない。"),
             (O, CH_B), (N, "AU-b・CH-b")],
            [(I, "C step（fork skill）"),
             (O, "○ B と同じ 7 か所。plan:pre は 2 回起動された。autonomous の UI の設計書の手順が plan:pre の skill の step を先に呼び、plan-phase でもう 1 回呼ぶ。"),
             (I, "ref.skill の step は、autonomous 自身が UI の設計書の前に呼ぶ（手順書の 3a.5）。verify:post の UI レビューの所では呼ばず、1 回だった。ref.agent の step は autonomous 自身は呼ばない。"),
             (N, ""), (N, "AU-c")],
            [(I, "D 委任（CLAUDE.md）"),
             (O, "○ 起動された 8 ロール全部が子を起動した（ui-researcher・ui-checker・planner・plan-checker・executor・ui-auditor・code-reviewer・verifier）。pattern-mapper は Skill が無い。"),
             (I, "単独のコマンド（Sonnet・Haiku）より従う率が高かった。plan-checker・ui-checker・ui-auditor も従った（Opus 5.5 のため）。"),
             (O, CH_D2), (N, "AU-d2・CH-d2")],
            [(I, "D 委任（agent_skills）"),
             (G, "△ 8 ロール中 5（planner・ui-researcher・executor・code-reviewer・verifier）。plan-checker・ui-checker・ui-auditor は従わなかった。"),
             (I, "autonomous 自身は agent_skills を渡さず、呼ぶ plan-phase・execute-phase が渡す（手順書に明記）。渡る範囲は単独のコマンドと同じ。"),
             (N, ""), (N, "AU-d")],
            [(I, "E メイン宛ての文"),
             (G, "△ verify:post（execute-phase の最後）の 1 か所だけ起動。discuss:pre・post の文は、smart discuss が処理を読まないので渡らなかった。"),
             (I, "単独の /gsd-discuss-phase では discuss:pre・post で起動されたが、autonomous では起きない。"),
             (O, CH_E), (N, "AU-e・CH-e")],
            [(I, "置き換え（B・C。既定を config でオフ）"), (O, AU_R), (I, AU_R_NOTE), (N, ""), (N, "AU-rb・AU-rc")],
            [(I, "F・G・D3（Claude Code の hook・同名の上書き）"),
             (N, "autonomous では検証していない。コマンドに依らない仕組み（Agent の呼び出し・サブエージェントの起動のたびに効く）なので、単独のコマンドと同じに効く想定。"),
             (N, ""), (N, ""), (N, "")],
            [(I, "autonomous そのものの動き（共通）"),
             (I, "8 本とも、フェーズ 2 の実装と自動の検証まで止まらずに進んだ。人の確認（UAT）が残る所で STATE.md に記録して止まった（仕様どおり）。自作を入れたことで止まった回は無い。"),
             (I, "autonomous は smart discuss を自分で行い、UI の設計書（gsd-ui-phase）・計画・実装・レビューは Skill で呼ぶ。ai-integration-phase も毎回呼ばれた。費用は 1 本 40〜50 ドル（Opus 5.5、約 200 turns）。"),
             (I, CH_NOTE), (N, "")],
        ],
    }


# 結果（autonomous・--auto の検証。コピーは AU-*・CH-*）
AU_A = "○ planner への指示（Capability の contribution）で計画書に agent_hint が書かれ、execute-phase で own-a-executor が起動された（gsd-executor は 0 回）。"
AU_A_NOTE = "単独の /gsd-execute-phase と同じ。autonomous は execute-phase を Skill で呼ぶだけなので、agent_hint の振り分けはそのまま効く。"
AU_R = "○ 9 ロール（phase-researcher・pattern-mapper・ui-researcher・plan-checker・code-reviewer・verifier・3 つの監査）が自作に置き換わり、既定は 1 回も起動されなかった。"
AU_R_NOTE = "C（fork skill）では計画の前の 3 ロールが 2 回ずつ動いた（autonomous の UI の設計書の手順が先に呼び、plan-phase でもう 1 回）。成果物が 2 度書かれ、計画も 2 本になった。B（agent）は 1 回ずつ。"
CH_B = "○ discuss:pre・post を含む 9 か所で起動（単独のコマンドと同じ）。autonomous と違い、相談は gsd-discuss-phase そのものなので、ポイントが起きる。"
CH_E = "○ discuss:pre・post と verify:post で起動。"
CH_D2 = "○ 8 ロール全部が子を起動した。"
CH_NOTE = "--auto は discuss-phase が plan-phase を、plan-phase が execute-phase を Skill で呼ぶ形。3 本とも実装と自動の検証まで進み、人の確認で止まった。"


# ---- 表4: 検討したほかの方法と、見直しで分かった考慮漏れ ----
def other_table(m):
    O, G, X, N, I = m.OK_GREEN, m.GOLD, m.RED, m.SUB, m.INK
    return {
        "tag": "own5T4", "name": "表4 ほかの方法",
        "title": "表4　GSD の外の方法と、見直しで分かった考慮漏れ（GSD 1.23.0・Claude Code 2.1.332）",
        "notes": [
            "5 つの方法（A〜E）は GSD の仕組みの中で起動する方法。",
            "ここは、Claude Code の仕組みや GSD の設定で起動・差し替えする方法と、文書とソースの見直しで見つけた考慮漏れ。",
            "○（緑）= 実機で確認した。△（金）= 条件つき。未検証 = 文書とソースで確認しただけ（コピーの列が空）。",
            "コピー = 検証用コピーの名前（削除済み）。根拠は会話の記録 ~/.claude/projects/…trials-v2-own-<名前>。",
        ],
        "cols": [("方法・項目", 170), ("何か", 400), ("実機の結果・判断", 420), ("使うときの注意", 330), ("コピー", 130)],
        "rows": [
            [(I, "F　Claude Code の hook で起動を書き換える"),
             (I, "PreToolUse hook（Agent ツール）。GSD が gsd-○○ を起動する直前に subagent_type を自作に書き換える（updatedInput）。"),
             (O, "○ /gsd-plan-phase 2 で gsd-planner → own-f-planner、gsd-plan-checker → own-f-plan-checker の 2 回とも置き換わった。自作は GSD の依頼文をそのまま受け取り、計画とチェックは普通に完了した。"),
             (I, "GSD の外の仕組みなので全コマンド・全ロールに効き、オフにできない planner・executor も置き換えられる。hook は .claude/settings.json に setup で置く。Claude Code 以外の実行環境には無い。自作は GSD の約束（成果物・コミット）を守る必要がある。"),
             (N, "F-plan")],
            [(I, "G　同じ名前で上書き（影にする）"),
             (I, ".claude/agents/gsd-○○.md を自作の内容にする。Claude Code は案件の .claude/agents をユーザーの ~/.claude/agents やプラグインより優先する。"),
             (G, "△ gsd-plan-checker.md を自作の内容にすると、GSD は gsd-plan-checker を起動し、動いたのは自作の内容だった（印 own-g-plan-checker）。"),
             (I, "GSD を案件に入れている（--local）と、再インストールや版上げで上書きされる。GSD が ~/.claude にあれば、案件の .claude/agents に同名を置くだけで影になる（文書で確認。実機では検証していない）。"),
             (N, "G-plan")],
            [(I, "D3　SubagentStart の hook で指示を挿入する"),
             (I, "Claude Code の SubagentStart hook。gsd-○○ が起動された直後に、additionalContext で「Skill で ownd-○○ を呼べ」を挿入する。方法 D の指示の 3 つ目の経路。"),
             (O, "○ /gsd-plan-phase 2 で gsd-planner・gsd-plan-checker の 2 回とも挿入され、2 回とも子を起動した。"),
             (I, "agent_skills（渡らないコマンドがある）・CLAUDE.md（メインにも読まれる）と違い、起動のたびに確実に、そのロールだけに渡る。Skill を持たないロールには効かない（→ agent_tools）。"),
             (N, "D3-plan")],
            [(I, "agent_tools　道具を追加する（問題点 10 の対策）"),
             (I, "config.json の agent_tools に {\"gsd-○○\": [\"Skill\"]} と書き、GSD を再インストールする。そのロールの tools に足される。Capability からは足せない。"),
             (O, "○ pattern-mapper・dom-verifier・debug-session-manager・doc-verifier の tools に Skill が足された。Skill の無かった debug-session-manager（/gsd-debug）と doc-verifier（/gsd-docs-update）が、CLAUDE.md の指示で子を起動した。"),
             (I, "再インストールが要る（setup で行う）。これで「Skill の無い 14 ロールは D が使えない」は解ける。tools がリストの形のロールにも足される。"),
             (N, "AT-test・AT-debug・AT-docs")],
            [(I, "Capability の gates"),
             (I, "ループポイントでチェックして止める部品。check は query か predicate（スクリプトの判定）か agentVerdict（AI の判定）。"),
             (N, "未検証。検証のコードでは、query・predicate の gate は blocking: true で止められる。agentVerdict は blocking: false に限られる。autonomous は plan:pre の gate を実行しない。"),
             (I, "step は助言だけで止める力が無い。止めたいときは gates を使う。自作のサブエージェントの判定では止められず、スクリプトの判定なら止められる。"),
             (N, "")],
            [(I, "review:pre　13 番目のループポイント"),
             (I, "/gsd-review（外部の AI に計画をレビューさせる）の中の点。この資料の「12 か所」は review:pre を除いた数。"),
             (N, "未検証。contribution（into: reviewer）だけを受け付け、step・gate は受け付けない（手順書）。"),
             (I, "自作のサブエージェントを起動する場所にはならない。"),
             (N, "")],
            [(I, "外部のコマンドを差す設定"),
             (I, "workflow.code_review_command（/gsd-ship で diff を標準入力に渡す）、workflow.plan_bounce_script（計画書を渡し、非 0 で止める）。"),
             (N, "未検証。サブエージェントではなく、外部のスクリプト・CLI を呼ぶ口。"),
             (I, "キットが持つ自動チェックのスクリプトを、GSD の流れに差す口の候補。"),
             (N, "")],
            [(I, "自作のコマンド（手順書のコピー）"),
             (I, "GSD の手順書のコピーを .claude/commands か skills に置き、Agent の subagent_type を自作に変える。"),
             (N, "未検証。確実に動くが、GSD の版上げのたびにコピーを追従させる手間がある。人が打つコマンドも変わる。"),
             (I, "F（hook）の方が、手順書を写さずに同じことができる。"),
             (N, "")],
            [(I, "入れ子の Agent"),
             (I, "サブエージェントが Agent ツールで子を起動する。Claude Code 2.1.x は既定で 3 層まで入れ子にできる。"),
             (N, "未検証。既定のロールで Agent を持つのは debug-session-manager だけ。agent_tools で Agent を足せば、fork skill 無しで子を起動させる形も組める。"),
             (I, ""),
             (N, "")],
            [(I, "検証していないコマンド"),
             (I, "quick-batch（plan:pre を読む）・audit-fix・new-milestone・explore・diagnose-issues・execute-plan・scan・review・next。"),
             (N, "未検証。起動するロールは executor・planner・plan-checker・phase-researcher・verifier・project-researcher・roadmapper・debugger・codebase-mapper（手順書を grep）。"),
             (I, "ポイントの有無は手順書から: quick-batch は plan:pre、review は review:pre、ほかは無し。"),
             (N, "")],
            [(I, "検証の方法の注記（モデル）"),
             (I, "A〜E の約 80 本は、サブエージェントに CLAUDE_CODE_SUBAGENT_MODEL=sonnet を付けていたが、全部が Sonnet ではなかった。"),
             (I, "GSD が Agent() に model= を渡すロールはそちらが優先された（planner は Opus、plan-checker・ui-auditor は Haiku、ほかは Sonnet）。会話の記録で確認。"),
             (I, "表3・表4 の検証は CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1 で全部 Opus 5.5。"),
             (N, "")],
        ],
    }
