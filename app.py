from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime, date
import json

app = Flask(__name__)

# 🔹 Función para conectar con la base de datos
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",          # 👈 tu usuario de MySQL
            password="123456",    # 👈 tu contraseña de MySQL
            database="hotel_reservas"
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

# 🔹 Ruta principal - Servir el index.html
@app.route('/')
def index():
    return render_template('index.html')

# 🔹 API: Verificar disponibilidad de habitaciones
@app.route('/api/check-availability', methods=['POST'])
def check_availability():
    try:
        data = request.json
        checkin = data.get('checkin')
        checkout = data.get('checkout')
        
        if not checkin or not checkout:
            return jsonify({'error': 'Fechas requeridas'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Consulta para verificar habitaciones disponibles
        query = """
        SELECT h.*, 
               CASE 
                   WHEN EXISTS (
                       SELECT 1 FROM reservas r 
                       WHERE r.id_habitacion = h.id_habitacion 
                       AND r.estado IN ('Pendiente', 'Confirmada')
                       AND (
                           (r.fecha_ingreso <= %s AND r.fecha_salida > %s) OR
                           (r.fecha_ingreso < %s AND r.fecha_salida >= %s) OR
                           (r.fecha_ingreso >= %s AND r.fecha_salida <= %s)
                       )
                   ) THEN 0 
                   ELSE 1 
               END as disponible
        FROM habitaciones h
        WHERE h.estado = 'Disponible'
        """
        
        cursor.execute(query, (checkin, checkin, checkout, checkout, checkin, checkout))
        habitaciones = cursor.fetchall()
        
        # Agrupar por tipo de habitación
        availability = {
            'estandar': {'available': False, 'price': 150000, 'rooms': 0},
            'deluxe': {'available': False, 'price': 250000, 'rooms': 0},
            'suite': {'available': False, 'price': 400000, 'rooms': 0},
            'presidencial': {'available': False, 'price': 500000, 'rooms': 0}
        }
        
        # Mapear tipos de habitación de BD a frontend
        type_mapping = {
            'Sencilla': 'estandar',
            'Doble': 'deluxe', 
            'Suite': 'suite'
        }
        
        for hab in habitaciones:
            tipo_frontend = type_mapping.get(hab['tipo_habitacion'], 'presidencial')
            if hab['disponible']:
                availability[tipo_frontend]['available'] = True
                availability[tipo_frontend]['price'] = float(hab['precio'])
                availability[tipo_frontend]['rooms'] += 1
        
        cursor.close()
        conn.close()
        
        return jsonify(availability)
        
    except Exception as e:
        print(f"Error en check_availability: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# 🔹 API: Crear nueva reserva
@app.route('/api/create-reservation', methods=['POST'])
def create_reservation():
    try:
        data = request.json
        
        # Validar datos requeridos
        required_fields = ['checkin', 'checkout', 'huespedes', 'tipoHabitacion', 'cliente']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Error de conexión'}), 500
            
        cursor = conn.cursor()
        
        # 1. Crear o buscar cliente
        cliente_data = data['cliente']
        
        # Verificar si el cliente ya existe
        cursor.execute("SELECT id_cliente FROM clientes WHERE email = %s", 
                      (cliente_data['email'],))
        cliente_existente = cursor.fetchone()
        
        if cliente_existente:
            id_cliente = cliente_existente[0]
        else:
            # Crear nuevo cliente
            cursor.execute("""
                INSERT INTO clientes (nombre, apellido, telefono, email, documento_identidad)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                cliente_data['nombre'], 
                cliente_data['apellido'],
                cliente_data.get('telefono', ''),
                cliente_data['email'],
                cliente_data.get('documento', '')
            ))
            id_cliente = cursor.lastrowid
        
        # 2. Buscar habitación disponible del tipo solicitado
        tipo_mapping = {
            'estandar': 'Sencilla',
            'deluxe': 'Doble',
            'suite': 'Suite',
            'presidencial': 'Suite'  # Asumiendo que presidencial es también Suite
        }
        
        tipo_bd = tipo_mapping[data['tipoHabitacion']]
        
        cursor.execute("""
            SELECT id_habitacion FROM habitaciones h
            WHERE h.tipo_habitacion = %s 
            AND h.estado = 'Disponible'
            AND NOT EXISTS (
                SELECT 1 FROM reservas r 
                WHERE r.id_habitacion = h.id_habitacion 
                AND r.estado IN ('Pendiente', 'Confirmada')
                AND (
                    (r.fecha_ingreso <= %s AND r.fecha_salida > %s) OR
                    (r.fecha_ingreso < %s AND r.fecha_salida >= %s) OR
                    (r.fecha_ingreso >= %s AND r.fecha_salida <= %s)
                )
            )
            LIMIT 1
        """, (tipo_bd, data['checkin'], data['checkin'], 
              data['checkout'], data['checkout'], 
              data['checkin'], data['checkout']))
        
        habitacion = cursor.fetchone()
        
        if not habitacion:
            return jsonify({'error': 'No hay habitaciones disponibles del tipo seleccionado'}), 400
        
        id_habitacion = habitacion[0]
        
        # 3. Crear la reserva
        cursor.execute("""
            INSERT INTO reservas (id_cliente, id_habitacion, fecha_ingreso, fecha_salida, estado)
            VALUES (%s, %s, %s, %s, 'Pendiente')
        """, (id_cliente, id_habitacion, data['checkin'], data['checkout']))
        
        id_reserva = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'reservationId': f'HTR-{id_reserva:06d}',
            'message': 'Reserva creada exitosamente'
        })
        
    except Exception as e:
        print(f"Error en create_reservation: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({'error': 'Error interno del servidor'}), 500

# 🔹 Mostrar habitaciones (página admin)
@app.route('/habitaciones')
def habitaciones():
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a la base de datos"
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM habitaciones")
    habitaciones_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('habitaciones.html', habitaciones=habitaciones_list)

# 🔹 Mostrar clientes (página admin)
@app.route('/clientes')
def clientes():
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a la base de datos"
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    clientes_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('clientes.html', clientes=clientes_list)

# 🔹 Mostrar reservas (página admin)
@app.route('/reservas')
def reservas():
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a la base de datos"
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, c.nombre, c.apellido, c.email, 
               h.numero_habitacion, h.tipo_habitacion, h.precio
        FROM reservas r
        JOIN clientes c ON r.id_cliente = c.id_cliente
        JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
        ORDER BY r.fecha_ingreso DESC
    """)
    reservas_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('reservas.html', reservas=reservas_list)

# 🔹 API: Obtener estadísticas del dashboard
@app.route('/api/dashboard-stats')
def dashboard_stats():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Error de conexión'}), 500
            
        cursor = conn.cursor()
        
        # Total de reservas
        cursor.execute("SELECT COUNT(*) FROM reservas")
        total_reservas = cursor.fetchone()[0]
        
        # Reservas activas (confirmadas y pendientes)
        cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado IN ('Pendiente', 'Confirmada')")
        reservas_activas = cursor.fetchone()[0]
        
        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor.fetchone()[0]
        
        # Habitaciones disponibles
        cursor.execute("SELECT COUNT(*) FROM habitaciones WHERE estado = 'Disponible'")
        habitaciones_disponibles = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_reservas': total_reservas,
            'reservas_activas': reservas_activas,
            'total_clientes': total_clientes,
            'habitaciones_disponibles': habitaciones_disponibles
        })
        
    except Exception as e:
        print(f"Error en dashboard_stats: {e}")
        return jsonify({'error': 'Error interno'}), 500

# 🔹 Página de administración
@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)