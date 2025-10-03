// ===== SISTEMA DE RESERVAS HOTEL TRANSILVANIA =====
// JavaScript para manejar formularios, validaciones y comunicación con backend

document.addEventListener('DOMContentLoaded', function() {
    initializeReservationSystem();
});

// ===== INICIALIZACIÓN DEL SISTEMA =====
function initializeReservationSystem() {
    console.log('🏨 Sistema de Reservas Hotel Transilvania iniciado');
    
    // Configurar fechas mínimas
    setupDateValidation();
    
    // Event listeners para el formulario
    setupFormListeners();
    
    // Event listeners para botones de selección de habitaciones
    setupRoomSelectors();
    
    // Cargar habitaciones disponibles
    loadAvailableRooms();
}

// ===== CONFIGURACIÓN DE VALIDACIÓN DE FECHAS =====
function setupDateValidation() {
    const checkinInput = document.getElementById('checkin');
    const checkoutInput = document.getElementById('checkout');
    
    // Establecer fecha mínima como hoy
    const today = new Date().toISOString().split('T')[0];
    checkinInput.min = today;
    
    // Cuando cambia check-in, actualizar check-out mínimo
    checkinInput.addEventListener('change', function() {
        const checkinDate = new Date(this.value);
        const nextDay = new Date(checkinDate);
        nextDay.setDate(nextDay.getDate() + 1);
        
        checkoutInput.min = nextDay.toISOString().split('T')[0];
        
        // Si checkout es anterior a la nueva fecha mínima, limpiarlo
        if (checkoutInput.value && checkoutInput.value <= this.value) {
            checkoutInput.value = '';
        }
        
        // Verificar disponibilidad cuando cambien las fechas
        checkAvailability();
    });
    
    checkoutInput.addEventListener('change', function() {
        checkAvailability();
    });
}

// ===== CONFIGURACIÓN DE EVENTOS DEL FORMULARIO =====
function setupFormListeners() {
    const reservaForm = document.getElementById('reservaForm');
    
    if (reservaForm) {
        reservaForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleReservationSubmit();
        });
    }
    
    // Listener para cambios en número de huéspedes
    const huespedes = document.getElementById('huespedes');
    if (huespedes) {
        huespedes.addEventListener('change', function() {
            filterRoomsByGuests();
        });
    }
}

// ===== CONFIGURACIÓN DE BOTONES DE HABITACIONES =====
function setupRoomSelectors() {
    const selectButtons = document.querySelectorAll('.btn-seleccionar');
    
    selectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const roomType = this.dataset.tipo;
            selectRoomType(roomType);
        });
    });
}

// ===== FUNCIONES DE DISPONIBILIDAD =====
async function checkAvailability() {
    const checkin = document.getElementById('checkin').value;
    const checkout = document.getElementById('checkout').value;
    
    if (!checkin || !checkout) {
        return;
    }
    
    // Mostrar loading
    showLoadingMessage('Verificando disponibilidad...');
    
    try {
        const response = await fetch('/api/check-availability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                checkin,
                checkout
            })
        });
        
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        
        const availability = await response.json();
        updateRoomAvailability(availability);
        hideLoadingMessage();
        
    } catch (error) {
        console.error('Error checking availability:', error);
        showErrorMessage('Error al verificar disponibilidad');
        hideLoadingMessage();
    }
}

// ===== LLAMADAS REALES AL BACKEND =====
async function submitReservationToBackend(formData, clientData) {
    const response = await fetch('/api/create-reservation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            checkin: formData.checkin,
            checkout: formData.checkout,
            huespedes: formData.huespedes,
            tipoHabitacion: formData.tipoHabitacion,
            cliente: clientData
        })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error del servidor');
    }
    
    return await response.json();
}

// ===== ACTUALIZACIÓN DE DISPONIBILIDAD EN UI =====
function updateRoomAvailability(availability) {
    const roomCards = document.querySelectorAll('.habitacion-card');
    
    roomCards.forEach(card => {
        const button = card.querySelector('.btn-seleccionar');
        const roomType = button.dataset.tipo;
        const priceElement = card.querySelector('.precio');
        
        if (availability[roomType]) {
            const room = availability[roomType];
            
            if (room.available) {
                button.disabled = false;
                button.textContent = `Seleccionar (${room.rooms} disponibles)`;
                button.classList.remove('disabled');
                card.style.opacity = '1';
                
                // Actualizar precio si es diferente
                priceElement.innerHTML = `$${room.price.toLocaleString()} <span>/noche</span>`;
            } else {
                button.disabled = true;
                button.textContent = 'No disponible';
                button.classList.add('disabled');
                card.style.opacity = '0.6';
            }
        }
    });
}

// ===== SELECCIÓN DE TIPO DE HABITACIÓN =====
function selectRoomType(roomType) {
    // Actualizar select del formulario
    const tipoHabitacion = document.getElementById('tipo-habitacion');
    tipoHabitacion.value = roomType;
    
    // Resaltar card seleccionada
    document.querySelectorAll('.habitacion-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    const selectedCard = document.querySelector(`[data-tipo="${roomType}"]`).closest('.habitacion-card');
    selectedCard.classList.add('selected');
    
    // Scroll to form
    document.querySelector('.reservas-section').scrollIntoView({ 
        behavior: 'smooth',
        block: 'center'
    });
    
    showSuccessMessage('Habitación seleccionada. Complete el formulario para continuar.');
}

// ===== FILTRAR POR NÚMERO DE HUÉSPEDES =====
function filterRoomsByGuests() {
    const numGuests = parseInt(document.getElementById('huespedes').value);
    const roomCards = document.querySelectorAll('.habitacion-card');
    
    roomCards.forEach(card => {
        const button = card.querySelector('.btn-seleccionar');
        const roomType = button.dataset.tipo;
        
        // Definir capacidad máxima por tipo de habitación
        const maxCapacity = {
            'estandar': 2,
            'deluxe': 3,
            'suite': 4,
            'presidencial': 6
        };
        
        if (numGuests && numGuests > maxCapacity[roomType]) {
            card.style.opacity = '0.5';
            button.disabled = true;
            button.textContent = 'Capacidad insuficiente';
        } else {
            card.style.opacity = '1';
            button.disabled = false;
            button.textContent = 'Seleccionar';
        }
    });
}

// ===== MANEJO DEL ENVÍO DEL FORMULARIO =====
async function handleReservationSubmit() {
    const formData = getFormData();
    
    // Validar datos
    if (!validateFormData(formData)) {
        return;
    }
    
    // Solicitar datos del cliente
    const clientData = await getClientData();
    if (!clientData) {
        return; // Usuario canceló
    }
    
    // Mostrar loading
    showLoadingMessage('Procesando reserva...');
    
    try {
        const result = await submitReservationToBackend(formData, clientData);
        
        if (result.success) {
            showReservationSuccess(result);
            resetForm();
        } else {
            showErrorMessage(result.message || 'Error al procesar la reserva');
        }
        
    } catch (error) {
        console.error('Error submitting reservation:', error);
        showErrorMessage(error.message || 'Error de conexión. Intente nuevamente.');
    } finally {
        hideLoadingMessage();
    }
}

// ===== RECOPILAR DATOS DEL CLIENTE =====
async function getClientData() {
    return new Promise((resolve) => {
        // Crear modal para datos del cliente
        const modal = document.createElement('div');
        modal.className = 'client-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Datos del Cliente</h3>
                <form id="clientForm">
                    <div class="client-form-grid">
                        <div class="form-group">
                            <label for="cliente-nombre">Nombre *</label>
                            <input type="text" id="cliente-nombre" required>
                        </div>
                        <div class="form-group">
                            <label for="cliente-apellido">Apellido *</label>
                            <input type="text" id="cliente-apellido" required>
                        </div>
                        <div class="form-group">
                            <label for="cliente-email">Email *</label>
                            <input type="email" id="cliente-email" required>
                        </div>
                        <div class="form-group">
                            <label for="cliente-telefono">Teléfono</label>
                            <input type="tel" id="cliente-telefono">
                        </div>
                        <div class="form-group">
                            <label for="cliente-documento">Documento</label>
                            <input type="text" id="cliente-documento">
                        </div>
                    </div>
                    <div class="modal-buttons">
                        <button type="button" class="btn-cancel">Cancelar</button>
                        <button type="submit" class="btn-confirm">Confirmar Reserva</button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Event listeners
        const form = modal.querySelector('#clientForm');
        const cancelBtn = modal.querySelector('.btn-cancel');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const clientData = {
                nombre: document.getElementById('cliente-nombre').value,
                apellido: document.getElementById('cliente-apellido').value,
                email: document.getElementById('cliente-email').value,
                telefono: document.getElementById('cliente-telefono').value,
                documento: document.getElementById('cliente-documento').value
            };
            
            modal.remove();
            resolve(clientData);
        });
        
        cancelBtn.addEventListener('click', function() {
            modal.remove();
            resolve(null);
        });
    });
}

// ===== OBTENER DATOS DEL FORMULARIO =====
function getFormData() {
    return {
        checkin: document.getElementById('checkin').value,
        checkout: document.getElementById('checkout').value,
        huespedes: document.getElementById('huespedes').value,
        tipoHabitacion: document.getElementById('tipo-habitacion').value
    };
}

// ===== VALIDACIÓN DE DATOS =====
function validateFormData(data) {
    if (!data.checkin) {
        showErrorMessage('Por favor seleccione la fecha de entrada');
        return false;
    }
    
    if (!data.checkout) {
        showErrorMessage('Por favor seleccione la fecha de salida');
        return false;
    }
    
    if (!data.huespedes) {
        showErrorMessage('Por favor seleccione el número de huéspedes');
        return false;
    }
    
    if (!data.tipoHabitacion) {
        showErrorMessage('Por favor seleccione el tipo de habitación');
        return false;
    }
    
    return true;
}

// ===== CARGAR HABITACIONES DISPONIBLES AL INICIO =====
async function loadAvailableRooms() {
    try {
        // Las habitaciones se cargarán cuando el usuario seleccione fechas
        console.log('Sistema de habitaciones listo');
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}
function showLoadingMessage(message) {
    // Crear o actualizar loading overlay
    let loading = document.getElementById('loading-overlay');
    if (!loading) {
        loading = document.createElement('div');
        loading.id = 'loading-overlay';
        loading.className = 'loading-overlay';
        document.body.appendChild(loading);
    }
    
    loading.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    loading.style.display = 'flex';
}

function hideLoadingMessage() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.style.display = 'none';
    }
}

function showSuccessMessage(message) {
    showNotification(message, 'success');
}

function showErrorMessage(message) {
    showNotification(message, 'error');
}

function showNotification(message, type) {
    // Crear notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Auto-remove después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function showReservationSuccess(result) {
    const message = `
        <div class="reservation-success">
            <h3>¡Reserva Exitosa!</h3>
            <p>Número de reserva: <strong>${result.reservationId}</strong></p>
            <p>Recibirá un email de confirmación pronto.</p>
        </div>
    `;
    
    // Crear modal de éxito
    const modal = document.createElement('div');
    modal.className = 'success-modal';
    modal.innerHTML = `
        <div class="modal-content">
            ${message}
            <button onclick="this.closest('.success-modal').remove()" class="btn-close">Cerrar</button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function resetForm() {
    document.getElementById('reservaForm').reset();
    
    // Remover selección de habitaciones
    document.querySelectorAll('.habitacion-card').forEach(card => {
        card.classList.remove('selected');
        card.style.opacity = '1';
    });
    
    // Reset buttons
    document.querySelectorAll('.btn-seleccionar').forEach(button => {
        button.disabled = false;
        button.textContent = 'Seleccionar';
    });
}

// ===== CARGAR HABITACIONES DISPONIBLES AL INICIO =====
async function loadAvailableRooms() {
    try {
        // Las habitaciones se cargarán cuando el usuario seleccione fechas
        console.log('Sistema de habitaciones listo');
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}

// ===== FUNCIONES DE UI/UX =====

// ===== FUNCIONES AUXILIARES =====
function formatPrice(price) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
    }).format(price);
}

function calculateNights(checkin, checkout) {
    const start = new Date(checkin);
    const end = new Date(checkout);
    const diffTime = Math.abs(end - start);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

// ===== RESPONSIVE MENU (Mobile) =====
function toggleMobileMenu() {
    const aside = document.querySelector('aside');
    aside.classList.toggle('active');
}

// Event listener para botón de menú mobile (agregar button en HTML si es necesario)
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('mobile-menu-toggle')) {
        toggleMobileMenu();
    }
});
