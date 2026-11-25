"""build_own5.py の表・結論・可変の文。GSD 1.23.0 の実機の結果（trials-v2/own-*）だけを書く。
数は「子を起動できた回 / ロールが起動された回」。コピーの名前は trials-v2/own-<名前>。
"""

# ---- 結果待ちだった所（結果が出たら、ここを直す） ----
A7_FACT = ("案件の CLAUDE.md で頼んだ回（A7）は、quick の計画書に agent_hint: own-a-executor が書かれた。"
           "それでも起動されたのは gsd-executor だった（仕様の「quick は対象外」と一致）。")
E_EXEC_SUB = "execute-phase の最後の確認（verify:post）でも起動された（追加）"
E_EXEC_FACT = ("execute-phase の verify:post の文で gsd-ui-auditor の置き換えを頼んだ回（E-rep-exec）は、own-e-ui-auditor が起動され、"
               "gsd-ui-auditor は起動されなかった。ただし UI-REVIEW.md は書かれなかった。")
E_EXEC_SHORT = "ui-auditor は own-e-ui-auditor に置き換わった（UI-REVIEW.md は書かれなかった）"
ADVISOR = {"bc": ("BF8F00", "△ 通常・advisor モードでは discuss:pre・post で自作が起動された。advisor-researcher をオフにするキーは無い"
                         "（USER-PROFILE.md が無いと起動されない）。assumptions モードはポイント無し。"),
           "d": ("38761D", "○ advisor-researcher は CLAUDE.md 3/3・agent_skills 4/4。assumptions-analyzer は 1/1・1/1。"),
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
         (G, "△ researcher は CLAUDE.md 1/1・agent_skills 1/2。pattern-mapper は Skill が無く ✕。"),
         (X, "✕ plan のポイントには文を入れられない。"),
         "R-plan-b・R-plan-c・R-ctrl-plan・D-plan・D2-quick"),
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
        ("gsd-mempalace-curator・gsd-user-profiler・gsd-intel-updater",
         (X, "✕"),
         (N, "未検証。curator は ship:post の後（push と PR の後）にしか起動されず、git push はしない約束なので実行していない。"
             "ship:pre では B・C・E とも起動された。"),
         (N, "未検証（3 ロールとも Skill が無い）。"),
         (N, "未検証。"),
         "L1-verify0（ship）・L1-intel（intel を有効にしても intel-updater は起動されなかった）・profile-user は PC 全体の設定に書き込むため実行していない"),
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
        "結論: 1 つの方法で全部のロールは置き換えられない。ロールによって使える方法が違う。",
        "A は executor だけ。B・C はループポイントのある所のロール。E は verify-work の中のロール（debugger など）。",
        "D は置き換えではなく、既定のロールが自作の子に任せる形で、ポイントの無いコマンドのロールはこれしか無い。",
        "どの方法でも、自作の定義は setup で .claude/ に配置する必要がある。",
    ]
    m.VERIFY_NOTE[:] = [
        "検証の方法: 小さな案件（数を数える静的なページ）を GSD 1.23.0 で作り、コマンドと方法ごとに案件をコピーして実行した（約 80 本）。",
        "実行は claude -p（メイン・サブエージェントとも Sonnet）。会話の記録から、起動されたサブエージェントの種類と回数を数えた。",
    ]
    m.CONCLUSION[:] = [
        [("結論: ", {"bold": True}), ("どの方法も、自作の定義（と skill）は setup で .claude/ に配置する必要がある。", {})],
        [("  ", {}), ("Capability からは配置されない（#5738 は 1.23.0 でも未実装）。", {})],
        [("・ 置き換わった: ", {"bold": True}), ("executor（A）。", {})],
        [("  ", {}), ("researcher・pattern-mapper・plan-checker・code-reviewer・verifier（B・C）。", {})],
        [("  ", {}), ("security・nyquist・ui の 3 つの監査と、ui-researcher（B・C）。", {})],
        [("  ", {}), ("B・C は、既定のロールを config でオフにし、同じポイントで起動する形。", {})],
        [("  ", {}), ("debugger と、修正の計画の planner・plan-checker（E。verify-work のメイン宛ての文）。", {})],
        [("・ 置き換わらなかった: ", {"bold": True}), ("planner と executor のオフ。ポイントの無いコマンドのロール。", {})],
        [("  ", {}), ("（new-project・ui-phase・code-review --fix・debug・map-codebase など）", {})],
        [("  ", {}), ("これらは D（既定のロールが子に任せる）しか無く、Skill の無い 14 ロールは D も使えない。", {})],
        [("・ 毎回ではない: ", {"bold": True}), ("D と E は、サブエージェントやメインが指示に従うかしだい。", {})],
        [("  ", {}), ("例: plan-checker は 6 回中 3 回。B・C の step も、止める力は無い（advisory）。", {})],
    ]
