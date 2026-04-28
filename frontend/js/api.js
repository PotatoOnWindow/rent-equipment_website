const API_BASE = 'http://localhost:8000'; // Поменяй порт, если у тебя другой


async function apiRequest(endpoint, method = 'GET', body = null) {
	const token = localStorage.getItem('token');

	const options = {
        	method,
		headers: {
			'Content-Type': 'application/json',
			...(token ? { 'Authorization': 'Bearer ' + token } : {})
		},
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка запроса');
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        alert(error.message);
        throw error;
    }
}




// API функции
/*const API = {
    // Техника
    getMachinery: () => apiRequest('/'),
    getMachineryDetails: (id) => apiRequest(`/machinery/${id}`),
    
    // Пользователи
    register: (data) => apiRequest('/registration', 'POST', data),
    
    // Расчёты
    calculateCost: (machineryId, amount, start, end) => 
        apiRequest(`/calculate-cost?machinery_type_id=${machineryId}&amount=${amount}&start_date=${start}&expiration_date=${end}`, 'POST'),
    
    // Заказы
    createOffers: (data) => apiRequest('/offer/create', 'POST', data),
    getUserOffers: (userId) => apiRequest(`/offers/user/${userId}`),
    getOfferDetails: (offerId) => apiRequest(`/offer/${offerId}`)
};
*/

const API = {
    baseUrl: 'http://127.0.0.1:8000',

    login: (data) => apiRequest('/login', 'POST', data),
	
	// for profile.html
	getMe: () => apiRequest('/me'), 

	cancelOffer: (offerId) =>
		apiRequest(`/offer/$(offerId)/cancel`, 'POST'),

	//for other things
	getMachinery: async () => {
		return await apiRequest('/');
	},

	getMachineryDetails: (id) => apiRequest(`/machinery/${id}`),

	calculateCost: (machineryId, amount, start, end) =>
		apiRequest(`/calculate-cost?machinery_type_id=${machineryId}&amount=${amount}&start_date=${start}&expiration_date=${end}`, 'POST'),

	createOffers: (data) => apiRequest('/offer/create', 'POST', data), 

	getUserOffers: () => apiRequest('/offers/user'),

    getHeaders: () => {
        const token = AuthManager.getToken();
        return {
	    'Content-Type': 'application/json',
            ...(token ? { 'Authorization': 'Bearer ' + token} : {})
        };
    },
};
