/* Work page: full-screen zoom on images, and share button. No dependencies. */
(function () {
  var fr = document.documentElement.lang === 'fr';
  var dlg = document.querySelector('dialog.zoom');
  if (fr) document.querySelectorAll('[data-fr-label]').forEach(function (el) {
    el.setAttribute('aria-label', el.dataset.frLabel);
  });

  // ----- zoom -----
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.work-images img'));
  if (dlg && dlg.showModal && imgs.length) {
    var big = dlg.querySelector('img'), i = 0, opener = null;
    var label = dlg.getAttribute('aria-label');
    var show = function (n) {
      i = (n + imgs.length) % imgs.length;
      var im = imgs[i];
      big.src = im.currentSrc || im.src;
      big.alt = im.alt || '';
    };
    imgs.forEach(function (im, n) {
      im.classList.add('zoomable');
      im.tabIndex = 0;
      im.setAttribute('role', 'button');
      im.setAttribute('aria-label', label + (im.alt ? ' : ' + im.alt : ''));
      var open = function () { opener = im; show(n); dlg.showModal(); };
      im.addEventListener('click', open);
      im.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
      });
    });
    var multi = imgs.length > 1;
    dlg.querySelector('.zoom-prev').hidden = !multi;
    dlg.querySelector('.zoom-next').hidden = !multi;
    dlg.querySelector('.zoom-prev').addEventListener('click', function () { show(i - 1); });
    dlg.querySelector('.zoom-next').addEventListener('click', function () { show(i + 1); });
    dlg.querySelector('.zoom-close').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target === big) dlg.close(); });
    dlg.addEventListener('keydown', function (e) {
      if (!multi) return;
      if (e.key === 'ArrowLeft') show(i - 1);
      if (e.key === 'ArrowRight') show(i + 1);
    });
    dlg.addEventListener('close', function () { if (opener) opener.focus(); });
  }

  // ----- share -----
  var btn = document.querySelector('.share-btn');
  if (btn) {
    var status = document.querySelector('.share-status');
    btn.addEventListener('click', function () {
      var data = { title: document.title, url: location.href };
      if (navigator.share) { navigator.share(data).catch(function () {}); return; }
      var done = function () {
        status.textContent = fr ? btn.dataset.frCopied : btn.dataset.copied;
        setTimeout(function () { status.textContent = ''; }, 2500);
      };
      if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(done, function () {});
      else { prompt('', location.href); }
    });
  }
})();
