const clients = document.querySelectorAll('#client');
const icon = document.querySelector('i');
clients.forEach(
    client => client.addEventListener("click", (event) => {
        if (client.classList.contains('collapsed')) {
            client.classList.remove('active');
            icon.classList = 'bi bi-caret-down-fill';
        }
        else {
            client.classList.add('active');
            icon.classList = 'bi bi-caret-up-fill';
        }
    })
);
