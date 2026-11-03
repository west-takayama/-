"""One shared, accessible letter form; only the message and publication choice are required."""
from html import escape as e
FORM='https://docs.google.com/forms/d/e/1FAIpQLSea2bdr7tSewOsgCaq4NtdKIMvv6Krf1y3dvWhX0oqlqd0Lzg/viewform'

def letter_form(cast):
    options='<option value="みんなへ">みんなへ</option>'+''.join(f'<option value="{e(p["name"])}" data-member-id="{e(p["id"])}">{e(p["name"])}へ</option>' for p in cast)
    return f'''<form class="br-letter" id="letter-form" action="{FORM}" method="get">
<p class="br-help">一言だけでも、匿名でもOK。メールアドレスは不要です。</p>
<div class="br-prompts" aria-label="書き始めのヒント"><button type="button" data-letter-prompt="感想：">💬 感想</button><button type="button" data-letter-prompt="聞いてみたいこと：">❓ 質問</button><button type="button" data-letter-prompt="話してほしいテーマ：">💡 テーマ</button></div>
<div class="form-group"><label class="form-label" for="letter-body">メッセージ <span>必須</span></label><textarea class="form-textarea" id="letter-body" name="entry.721706859" required maxlength="1500" aria-describedby="letter-count letter-error" placeholder="「この話、私も同じ！」など、一言からどうぞ。"></textarea><p class="char-count" id="letter-count">0 / 1500</p></div>
<details class="br-letter-options" id="letter-options"><summary>名前・宛先を選ぶ（任意）</summary><div class="form-group"><label class="form-label" for="letter-name">ラジオネーム（空欄なら匿名）</label><input class="form-input" id="letter-name" name="entry.1204434679" maxlength="40" autocomplete="nickname" placeholder="匿名でも送れます"></div><div class="form-group"><label class="form-label" for="letter-to">宛先</label><select class="form-select" id="letter-to" name="entry.2111815986">{options}</select></div></details>
<div class="form-group"><label class="form-label" for="letter-public">番組で紹介してもいいですか？ <span>必須</span></label><select class="form-select" id="letter-public" name="entry.1377887326" required><option value="">選んでください</option><option value="はい">はい、紹介してOK</option><option value="いいえ">いいえ、非公開で</option></select></div>
<p class="br-form-error" id="letter-error" role="alert"></p><button class="btn-main br-send" type="submit">📮 確認・送信画面へ</button><p class="br-help">次のGoogleフォームで「送信」を押すと届きます。この画面ではまだ送信されません。</p>
<p class="br-help" id="letter-save-state" role="status"></p><button class="br-draft-clear" id="letter-clear" type="button">下書きを消す</button>
<noscript><p class="br-help">しゃり・はぎ・りゅう・れお宛ては、次の画面で「みんなへ」を選び、本文に宛先を添えてください。</p></noscript></form>'''
