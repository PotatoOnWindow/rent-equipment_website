// Принудительная очистка кэша состояния для Firefox
if (navigator.userAgent.includes('Firefox')) {
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            console.log('Page was loaded from bfcache, refreshing state');
            renderNavbar();
        }
    });
}

// Управление состоянием пользователя
const UserManager = {
    save: (user) => {
        console.log('Saving user:', user);
        localStorage.setItem('user', JSON.stringify(user));
        // Обновляем навигацию сразу после сохранения
        renderNavbar();
    },
    get: () => {
        try {
            const user = localStorage.getItem('user');
            console.log('Getting user from storage:', user);
            return user ? JSON.parse(user) : null;
        } catch (e) {
            console.error('Error parsing user data:', e);
            return null;
        }
    },
    remove: () => {
        console.log('Removing user');
        localStorage.removeItem('user');
        renderNavbar();
    },
    isLoggedIn: () => {
        const loggedIn = !!localStorage.getItem('user');
        console.log('Is logged in:', loggedIn);
        return loggedIn;
    }
};

// Управление корзиной
const CartManager = {
    get: () => {
        try {
            const cart = localStorage.getItem('cart');
            return cart ? JSON.parse(cart) : [];
        } catch (e) {
            console.error('Error parsing cart data:', e);
            return [];
        }
    },
    save: (cart) => {
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartDisplay();
    },
    add: (item) => {
        console.log('Adding to cart:', item);
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
        console.log('Removing from cart:', machineryId);
        const cart = CartManager.get().filter(i => i.machinery_type_id !== machineryId);
        CartManager.save(cart);
    },
    clear: () => {
        console.log('Clearing cart');
        localStorage.setItem('cart', '[]');
        updateCartDisplay();
    },
    count: () => CartManager.get().reduce((sum, item) => sum + item.amount, 0)
};

// Функция для обновления отображения корзины в навигации
function updateCartDisplay() {
    const count = CartManager.count();
    console.log('Updating cart display, count:', count);
    
    // Обновляем все элементы с классом cart-badge
    const cartBadges = document.querySelectorAll('.cart-badge');
    cartBadges.forEach(badge => {
        badge.textContent = `🛒 Корзина (${count})`;
    });
    
    // Также обновляем навигацию полностью
    renderNavbar();
}

// Рендеринг навигации
function renderNavbar() {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) {
        console.log('Navbar container not found');
        return;
    }

    const user = UserManager.get();
    const cartCount = CartManager.count();
    
    console.log('Rendering navbar. User:', user, 'Cart count:', cartCount);

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
                    <a href="login.html" id="loginLink">Войти</a>
                    <a href="register.html" id="registerLink">Регистрация</a>
                `}
            </div>
        </div>
    `;

    // Добавляем обработчик для кнопки выхода
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Logout clicked');
            UserManager.remove();
            // После выхода перенаправляем на главную
            window.location.href = 'index.html';
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, initializing...');
    console.log('Current user:', UserManager.get());
    console.log('Current cart:', CartManager.get());
    
    renderNavbar();
    
    // Проверяем авторизацию для защищенных страниц
    const protectedPages = ['profile.html'];
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    console.log('Current page:', currentPage);
    
    if (protectedPages.includes(currentPage)) {
        const user = UserManager.get();
        if (!user) {
            console.log('Protected page accessed without auth, redirecting to login');
            // Сохраняем текущую страницу для возврата после логина
            sessionStorage.setItem('redirectAfterLogin', currentPage);
            window.location.href = 'login.html';
        }
    }
    
    // Для страниц логина и регистрации проверяем, не авторизован ли уже пользователь
    if (currentPage === 'login.html' || currentPage === 'register.html') {
        const user = UserManager.get();
        if (user) {
            console.log('Already logged in, accessing login/register page');
            // Не делаем автоматического редиректа, страницы сами обработают это
        }
    }
});

// Экспортируем функции для использования в консоли (для отладки)
window.debug = {
    getUser: () => UserManager.get(),
    getCart: () => CartManager.get(),
    clearAll: () => {
        localStorage.clear();
        window.location.reload();
    }
};
