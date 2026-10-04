const app = document.querySelector('#app');

async function init() {
  let config;
  try {
    const response = await fetch('access-config.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('Configuration unavailable');
    config = await response.json();
    if (!/^[a-f0-9]{64}$/.test(config.passwordSha256) || !crypto.subtle) {
      throw new Error('Invalid configuration or unsupported browser');
    }
  } catch {
    app.innerHTML = '<section class="card"><h1>読み込めませんでした</h1><p>通信状況を確認して、ページを再読み込みしてください。</p><button onclick="location.reload()">再読み込み</button></section>';
    return;
  }

  app.innerHTML = `<section class="card access-card">
    <div class="eyebrow">LESSON REVIEW</div>
    <h1>パスワードを入力</h1>
    <p class="muted">教えてもらったパスワードで、復習テストを開こう。</p>
    <form id="access-form">
      <label for="password">パスワード</label>
      <input id="password" name="password" type="password" required autocomplete="current-password" autocapitalize="off" spellcheck="false" aria-describedby="access-error">
      <label class="password-toggle"><input id="show-password" type="checkbox">パスワードを表示する</label>
      <p id="access-error" role="alert"></p>
      <button class="primary wide" type="submit">テストを開く</button>
    </form>
  </section>`;

  const form = document.querySelector('#access-form');
  const input = document.querySelector('#password');
  const error = document.querySelector('#access-error');
  const button = form.querySelector('button');
  document.querySelector('#show-password').onchange = event => {
    input.type = event.target.checked ? 'text' : 'password';
  };
  form.addEventListener('submit', async event => {
    event.preventDefault();
    button.disabled = true;
    error.textContent = '';
    input.removeAttribute('aria-invalid');
    try {
      const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(input.value));
      const hash = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
      if (hash !== config.passwordSha256) {
        error.textContent = 'パスワードが違います。もう一度入力してください。';
        input.setAttribute('aria-invalid', 'true');
        input.focus();
        input.select();
        return;
      }
      input.value = '';
      app.innerHTML = '<p>テストを読み込み中…</p>';
      await import('./app.js');
    } catch {
      app.innerHTML = '<section class="card"><h1>読み込めませんでした</h1><p>ページを再読み込みして、もう一度お試しください。</p></section>';
    } finally {
      button.disabled = false;
    }
  });
}

// 解錠状態は保存せず、ページを開くたびに入力を求める。
// これは静的サイトの簡易ロック。データのアクセス制御ではない。
init();
