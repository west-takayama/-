# ブリッジラジオ 00s

既存の黒×黄色のホーム、下部4メニュー、今日の一言、占いの全内容・1日3回・音声・演出を保持した公式サイトの更新ソースです。

## ビルドと検証

Python 3.11以降とNode.jsを使用します。外部パッケージや有料APIは不要です。

```sh
python scripts/build.py
python -m unittest discover -s tests -v
node --test tests/goal.test.mjs tests/letters.test.mjs
```

`index.html`は元のホームのテンプレートです。生成結果は`dist/`に出力します。元CSS・占い・下部メニュー・音源との一致、内部リンク、構造化データ、お便り導線、目標集計日の扱いを検証します。

## 公開機能

- 公式RSSの99配信の個別ページ、検索、Podcast入門と第94回の紹介記事。
- canonical、OGP、構造化データ、サイトマップ。
- 公開目標シートを読むNetlify Function。古い集計は「最新集計待ち」とし、取得日時で集計日を置き換えません。
- お便り本文の一時保存と入力補助、既存Googleフォームへの確認導線。フォームへ移動しただけで送信完了とは表示しません。
- GA4の既存測定IDを使用します。再生位置イベントは聴取時間やPodcast再生数とは別です。

## 更新と公開経路

公開先は既存の `https://spectacular-cuchufli-3e84ee.netlify.app/` のみ。`netlify.toml`のビルドは`python3 scripts/build.py`、公開ディレクトリは`dist`です。Netlifyの既存サイトとこのリポジトリの接続確認が必要です。GitHubへの保存だけでは本番反映完了ではありません。

GitHub Actionsは検証のみを行い、デプロイや定期実行を追加しません。定期運営は既存の運営タスクで継続します。`scripts/refresh.py`で公開RSS・note・目標シートを更新できます。音声未確認の発言や薄い要約記事を自動公開しません。

管理記録、告知案、記事下書き、動画制作素材は公開リポジトリと`dist`に含めません。運営者用の非公開プロジェクトで管理します。

元サイトの復旧基点: `93d380608eaf6ce9c3e2003a40d22ccaf19cae2b`。
