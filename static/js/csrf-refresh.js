(function () {
    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split('; ').find((item) => item.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : '';
    }

    document.addEventListener('submit', function (event) {
        const token = getCookie('csrftoken');
        if (!token) return;

        event.target.querySelectorAll('input[name="csrfmiddlewaretoken"]').forEach(function (input) {
            input.value = token;
        });
    }, true);
})();
