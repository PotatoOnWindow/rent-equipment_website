// Обработка возврата страницы из bfcache -- решение для всех браузеров
window.addEventListener('pageshow', (event) => {
	console.log('pageshow fired, persisted: ', event.persisted);

	// На всякий случай
	renderNavbar();
});


const AuthManager = {
    saveToken: (token) => {
        localStorage.setItem('token', token);
    },

    getToken: () => {
        return localStorage.getItem('token');
    },

    logout: () => {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    },

    isAuthenticated: () => {
        return !!localStorage.getItem('token');
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


function renderNavbar() {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) return;

    const cartCount = CartManager.count();

    if (AuthManager.isAuthenticated()) {
        navContainer.innerHTML = `
            <a href="index.html">Каталог</a>
            <a href="cart.html">🛒 Корзина (${cartCount})</a>
            <a href="profile.html">Профиль</a>
            <button onclick="AuthManager.logout()">Выйти</button>
        `;
    } else {
        navContainer.innerHTML = `
            <a href="index.html">Каталог</a>
            <a href="cart.html">🛒 Корзина (${cartCount})</a>
            <a href="login.html">Войти</a>
            <a href="register.html">Регистрация</a>
        `;
    }
}


// Рендеринг навигации
/*
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
}*/

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, initializing...');
    console.log('Current user:', AuthManager.getToken());
    console.log('Current cart:', CartManager.get());
    
    renderNavbar();
    
    // Проверяем авторизацию для защищенных страниц
    const protectedPages = ['profile.html'];
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    console.log('Current page:', currentPage);
    
    if (protectedPages.includes(currentPage)) {
        const user = AuthManager.getToken();
        if (!user) {
            console.log('Protected page accessed without auth, redirecting to login');
            // Сохраняем текущую страницу для возврата после логина
            sessionStorage.setItem('redirectAfterLogin', currentPage);
            window.location.href = 'login.html';
        }
    }
    
    // Для страниц логина и регистрации проверяем, не авторизован ли уже пользователь
    if (currentPage === 'login.html' || currentPage === 'register.html') {
        const user = AuthManager.getToken();
        if (user) {
            console.log('Already logged in, accessing login/register page');
            // Не делаем автоматического редиректа, страницы сами обработают это
        }
    }
});

// Экспортируем функции для использования в консоли (для отладки)
window.debug = {
    getUser: () => AuthManager.getToken(),
    getCart: () => CartManager.get(),
    clearAll: () => {
        localStorage.clear();
        window.location.reload();
    }
};
