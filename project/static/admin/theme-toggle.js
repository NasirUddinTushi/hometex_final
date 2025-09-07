(function () {
  function setTheme(mode) {
    document.documentElement.dataset.theme = mode;
    try { localStorage.setItem('hti_admin_theme', mode); } catch(e) {}
    var icon = document.querySelector('#hti-theme-toggle .hti-icon');
    if (icon) icon.textContent = mode === 'dark' ? '☀️' : '🌙';
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('hti-theme-toggle');
    if (!btn) return;
    var cur = document.documentElement.dataset.theme || 'light';
    var icon = btn.querySelector('.hti-icon');
    if (icon) icon.textContent = cur === 'dark' ? '☀️' : '🌙';

    btn.addEventListener('click', function () {
      var now = document.documentElement.dataset.theme || 'light';
      setTheme(now === 'dark' ? 'light' : 'dark');
    });
  });
})();
