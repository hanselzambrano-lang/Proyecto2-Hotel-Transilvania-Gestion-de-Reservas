#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar automáticamente la base de datos del Hotel Transilvania
"""
import mysql.connector
from mysql.connector import Error

def crear_base_datos():
    """Crear la base de datos y las tablas necesarias"""
    try:
        # Conectar a MySQL sin especificar base de datos
        print("🔄 Conectando a MySQL...")
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456'
        )
        
        cursor = conexion.cursor()
        
        # Crear base de datos
        print("🔄 Creando base de datos 'hotel_reservas'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS hotel_reservas")
        cursor.execute("USE hotel_reservas")
        
        # Crear tabla clientes
        print("🔄 Creando tabla 'clientes'...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            telefono VARCHAR(20) NOT NULL,
            dni VARCHAR(20) UNIQUE NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Crear tabla habitaciones
        print("🔄 Creando tabla 'habitaciones'...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS habitaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo VARCHAR(50) NOT NULL,
            numero INT UNIQUE NOT NULL,
            precio_noche DECIMAL(10,2) NOT NULL,
            capacidad INT NOT NULL,
            descripcion TEXT,
            disponible BOOLEAN DEFAULT TRUE
        )
        """)
        
        # Crear tabla reservas
        print("🔄 Creando tabla 'reservas'...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT,
            habitacion_id INT,
            fecha_checkin DATE NOT NULL,
            fecha_checkout DATE NOT NULL,
            num_huespedes INT NOT NULL,
            precio_total DECIMAL(10,2) NOT NULL,
            estado VARCHAR(20) DEFAULT 'confirmada',
            fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id)
        )
        """)
        
        # Insertar habitaciones de ejemplo
        print("🔄 Insertando habitaciones de ejemplo...")
        habitaciones_data = [
            ('Estándar', 101, 150.00, 2, 'Habitación cómoda con vista al jardín'),
            ('Estándar', 102, 150.00, 2, 'Habitación cómoda con vista al jardín'),
            ('Deluxe', 201, 250.00, 3, 'Habitación espaciosa con balcón'),
            ('Deluxe', 202, 250.00, 3, 'Habitación espaciosa con balcón'),
            ('Suite', 301, 400.00, 4, 'Suite con sala de estar separada'),
            ('Suite Presidencial', 401, 800.00, 6, 'La mejor suite del hotel con jacuzzi')
        ]
        
        cursor.executemany("""
        INSERT IGNORE INTO habitaciones (tipo, numero, precio_noche, capacidad, descripcion)
        VALUES (%s, %s, %s, %s, %s)
        """, habitaciones_data)
        
        # Confirmar cambios
        conexion.commit()
        print("✅ Base de datos configurada exitosamente!")
        print("✅ Tablas creadas: clientes, habitaciones, reservas")
        print(f"✅ Habitaciones insertadas: {cursor.rowcount} registros")
        
        # Mostrar un resumen
        cursor.execute("SELECT COUNT(*) FROM habitaciones")
        total_habitaciones = cursor.fetchone()[0]
        print(f"📊 Total de habitaciones disponibles: {total_habitaciones}")
        
        return True
        
    except Error as e:
        print(f"❌ Error al configurar la base de datos: {e}")
        return False
        
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
            print("🔌 Conexión cerrada")

def verificar_conexion():
    """Verificar que la aplicación puede conectarse a la base de datos"""
    try:
        print("\n🔄 Verificando conexión de la aplicación...")
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='hotel_reservas'
        )
        
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM habitaciones")
        total = cursor.fetchone()[0]
        
        print(f"✅ Conexión exitosa! Habitaciones disponibles: {total}")
        return True
        
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return False
        
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    print("🏨 Configurando Hotel Transilvania - Base de Datos")
    print("=" * 50)
    
    if crear_base_datos():
        if verificar_conexion():
            print("\n🎉 ¡Configuración completada exitosamente!")
            print("📌 Ahora puedes ejecutar tu aplicación Flask con: python app.py")
        else:
            print("\n⚠️  Base de datos creada pero hay problemas de conexión")
    else:
        print("\n❌ Falló la configuración de la base de datos")