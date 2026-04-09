// Управление состоянием пользователя
const UserManager = {
    save: (user) => {
        localStorage.setItem('user', JSON.stringify(user));
        window.dispatchEvent(new Event('userUpdated')); // Событие для обновления UI
    },
    get: () => {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },
    remove: () => {
        localStorage.removeItem('user');
        window.dispatchEvent(new Event('userUpdated'));
    },
    isLoggedIn: () => {
        return !!localStorage.getItem('user');
    }
};

// Управление корзиной
const CartManager = {
    get: () => {
        const cart = localStorage.getItem('cart');
        return cart ? JSON.parse(cart) : [];
    },
    save: (cart) => {
        localStorage.setItem('cart', JSON.stringify(cart));
        window.dispatchEvent(new Event('cartUpdated'));
    },
    add: (item) => {
        const cart = CartManager.get();
        const existing = cart.find(i => i.machinery_type_id === item.machinery_type_id);
        if (existing) {
            existing.amount += item.amount;
        } else {
            cart.push(item);
        }
        CartManager.save(cart);
    },
    remove: (machineryId) => {
        const cart = CartManager.get().filter(i => i.machinery_type_id !== machineryId);
        CartManager.save(cart);
    },
    clear: () => CartManager.save([]),
    count: () => CartManager.get().reduce((sum, item) => sum + item.amount, 0)
};

// Рендеринг навигации
function renderNavbar() {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) return;

    const user = UserManager.get();
    const cartCount = CartManager.count();

    navContainer.innerHTML = `
        <div class="container">
            <a href="index.html" class="logo">🚜 RentTech</a>
            <div class="nav-links">
                <a href="index.html">Каталог</a>
                <a href="cart.html" class="cart-badge">🛒 Корзина (${cartCount})</a>
                ${user ? `
                    <a href="profile.html" class="user-profile-link">👤 ${user.username}</a>
                    <button id="logoutBtn" class="btn-logout">Выйти</button>
                ` : `
                    <a href="login.html">Войти</a>
                    <a href="register.html">Регистрация</a>
                `}
            </div>
        </div>
    `;

    // Добавляем обработчик для кнопки выхода
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            UserManager.remove();
            window.location.reload(); // Перезагружаем страницу после выхода
        });
    }
}

// Слушаем обновления пользователя и корзины
window.addEventListener('userUpdated', renderNavbar);
window.addEventListener('cartUpdated', renderNavbar);

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', renderNavbar);
