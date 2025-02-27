// static/js/service-worker.js
self.addEventListener('push', function(event) {
    const data = event.data.json();
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/static/images/icon.png',
    });
  });