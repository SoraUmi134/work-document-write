# work-document-write

利用者への返答と、資料作成で守るルールを、Claude Code のスキルとしてまとめたリポジトリ。
対象は、ふだんのチャットの返答、人に渡す資料（Markdown・Excel の説明図）、画面の文言（ボタン・ラベル・エラーメッセージ・通知文）、その前のチェック。
利用者から指摘を受けるたびに、該当するスキルへ追記する。

## スキルの一覧

| スキル | 使う場面 | 内容 |
|---|---|---|
| `skills/chat-reply/` | ふだんのチャットの返答すべて | 日本語で回答する、聞かれたことに最初に答える、未確認は明記する、ファイルは絶対パスで書く、進捗の報告の仕方 |
| `skills/ja-writing-style/` | 日本語の文章すべて（返答・資料） | 和語に言い換えず熟語とカタカナ語で書く（置き換え表）。AI 特有の言い回しの一覧と代わりの書き方 |
| `skills/explain-before-shorten/` | 説明文・報告を書くとき | 短くする前に、口頭で説明する文を組み立ててから削る |
| `skills/doc-writing/` | 人に渡す資料を書くとき | 結論から書く、「何が起きる → 何が困る」まで書く、文を足しすぎない、根拠のリンクの付け方 |
| `skills/review-before-delivery/` | 資料を渡す前 | 機械のチェック・Excel での見た目の確認・前提知識なしのレビュアーによる確認。指摘を受けたら禁止語とチェックに追加する |
| `skills/excel-figure/` | Excel の説明図を描くとき | 人が描いた図の描き方に合わせて、オートシェイプで図を追加する |
| `skills/ui-copy-ja/` | 画面の文言・通知文・リリースノートを書く・直す・点検するとき | 既存の文言から語を探す、普通に使われる漢語を言い換えない、動詞から名詞を作らない、部品や実装の呼び名を出さない。PR の前に別の読み手に点検させる。出典は HolyGrail/skills（MIT） |

補助のスクリプト:

| 場所 | 内容 |
|---|---|
| `skills/excel-figure/scripts/xdraw.py` | 図形を組み立てて xlsx に書き込む部品（python3 の標準ライブラリだけで動く） |
| `skills/excel-figure/scripts/render_drawing.py` | xlsx の図を PNG / SVG に描画して確認する。図形の一覧も出せる |
| `skills/excel-figure/scripts/check_figure.py` | Excel の図の機械のチェック（あふれ・凡例と線の対応・線の向き・横切り・重なり・禁止語・長い段落） |
| `skills/review-before-delivery/scripts/check_text.py` | 文書の機械のチェック（禁止語・長い文） |
| `skills/review-before-delivery/banned_words.txt` | 使わない言い方と、代わりの言い方 |
| `skills/ui-copy-ja/references/scripts/copy-diff.sh` | ブランチで足した、人に見せる日本語の行を一覧にする。点検済みの記録も付ける |
| `skills/ui-copy-ja/references/scripts/copy-guard.sh` | PR を出す前に、足した日本語が点検済みかを確認する hook（任意） |
| `examples/gsd-patterns/` | Excel の図を描いた実例のスクリプト |

## Claude Code で使う

リポジトリを `~/Develop/work-document-write` にクローンし、スキルのフォルダを `~/.claude/skills/` へシンボリックリンクで繋ぐ。コピーではないので、このリポジトリを修正すればすぐ反映される。

```bash
gh repo clone SoraUmi134/work-document-write ~/Develop/work-document-write
```

```bash
for s in chat-reply ja-writing-style explain-before-shorten doc-writing review-before-delivery excel-figure ui-copy-ja; do ln -s ~/Develop/work-document-write/skills/$s ~/.claude/skills/$s; done
```

チャットの返答で毎回使われるよう、`~/.claude/rules/language.md` などの常に読まれるルールに、chat-reply を参照する 1 行を置く。
チェックを自動で実行する hook の設定は、`skills/review-before-delivery/SKILL.md` の最後にある。
### PR の前に文言の点検を確認する hook（ui-copy-ja）

人に見せる日本語を足したブランチで、点検しないまま `gh pr create` / `gh pr ready` を実行すると止める。
足した日本語が無いとき、点検済みのとき、git リポジトリでないときは止めない。仕組みと止まったときの手順は `skills/ui-copy-ja/SKILL.md` の「点検を hook で担保する」にある。

どのプロジェクトでも効くよう、ユーザーの設定（`~/.claude/settings.json`）の `hooks.PreToolUse` に、次の 1 件を足す。ほかの hook はそのまま残す。

```json
{
  "matcher": "Bash|mcp__github__create_pull_request",
  "hooks": [
    {
      "type": "command",
      "command": "bash ~/.claude/skills/ui-copy-ja/references/scripts/copy-guard.sh"
    }
  ]
}
```

jq で足すときは、控えを取ってから実行する（要る物: jq、perl、shasum）。

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak && jq '.hooks.PreToolUse += [{"matcher":"Bash|mcp__github__create_pull_request","hooks":[{"type":"command","command":"bash ~/.claude/skills/ui-copy-ja/references/scripts/copy-guard.sh"}]}]' ~/.claude/settings.json.bak > ~/.claude/settings.json
```

`command` のパスは、`~/.claude/skills/ui-copy-ja` のシンボリックリンクを通す。hook は自分と同じフォルダの `copy-diff.sh` を呼ぶので、スクリプトを別の場所へコピーしない。登録は新しいセッションから効く。

## 要る物

- python3
- `rsvg-convert`（図を PNG にする。`brew install librsvg`）
- Microsoft Excel（仕上がりを確かめる。無ければ LibreOffice で代わりに見る）

## 追記のルール

- 返答について指摘を受けたら、chat-reply か ja-writing-style に追記する。
- 資料や図について「違う」と言われたら、該当するスキルの「一番大事なこと」か「細かい落とし穴」に追記する。機械で拾える物は、チェックのスクリプトと banned_words.txt にも追加する。
- スクリプトで修正した所は、実例のスクリプトにも反映する。
