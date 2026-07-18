window.__bootErrors = [];
window.addEventListener('error', function (event) {
  var file = (event.filename || 'unknown').split('/').pop();
  var kind = event.error && event.error.name ? event.error.name : 'Error';
  var message = String(event.message || '').slice(0, 80).replace(/\W+/g, '_').toUpperCase();
  window.__bootErrors.push('BOOT_' + file.replace(/\W+/g, '_').toUpperCase() + '_L' + (event.lineno || 0) + '_' + kind.toUpperCase() + '_' + message);
});
