self.addEventListener('push', function(event) {
    if (event.data) {
        const payload = event.data.json();
        const options = {
            body: payload.body,
            data: { url: payload.url }
        };
        event.waitUntil(
            self.registration.showNotification(payload.title, options)
        );
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    if (event.notification.data && event.notification.data.url) {
        event.waitUntil(clients.openWindow(event.notification.data.url));
    }
});
