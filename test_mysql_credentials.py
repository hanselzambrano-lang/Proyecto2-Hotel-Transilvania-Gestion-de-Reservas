#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar diferentes credenciales de MySQL
"""
import mysql.connector
from mysql.connector import Error

def probar_credenciales():
    """Probar diferentes combinaciones de usuario/contraseña"""
    credenciales = [
        ('root', ''),           # Usuario root sin contraseña
        ('root', 'root'),       # Usuario root con contraseña root
        ('root', 'password'),   # Usuario root con contraseña password
        ('root', 'admin'),      # Usuario root con contraseña admin
        ('root', '123456'),     # Usuario root con contraseña simple
        ('mysql', ''),          # Usuario mysql sin contraseña
        ('mysql', 'mysql'),     # Usuario mysql con contraseña mysql
    ]
    
    print("🔍 Probando credenciales de MySQL...")
    print("=" * 40)
    
    for usuario, contraseña in credenciales:
        try:
            print(f"🔄 Probando: Usuario='{usuario}', Contraseña='{contraseña if contraseña else '(vacía)'}'")
            
            conexion = mysql.connector.connect(
                host='localhost',
                user=usuario,
                password=contraseña,
                connect_timeout=5
            )
            
            if conexion.is_connected():
                print(f"✅ ¡CONEXIÓN EXITOSA!")
                print(f"   Usuario: {usuario}")
                print(f"   Contraseña: {'(vacía)' if not contraseña else contraseña}")
                
                # Obtener información del servidor
                cursor = conexion.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                print(f"   Versión MySQL: {version}")
                
                # Listar bases de datos existentes
                cursor.execute("SHOW DATABASES")
                databases = cursor.fetchall()
                print(f"   Bases de datos: {len(databases)} encontradas")
                for db in databases:
                    print(f"     - {db[0]}")
                
                cursor.close()
                conexion.close()
                return usuario, contraseña
                
        except Error as e:
            if "Access denied" in str(e):
                print(f"❌ Acceso denegado")
            elif "Can't connect" in str(e):
                print(f"❌ No se puede conectar al servidor")
            else:
                print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        print()
    
    print("❌ No se encontraron credenciales válidas")
    print("\n💡 Opciones:")
    print("1. Buscar en MySQL Workbench las credenciales guardadas")
    print("2. Resetear la contraseña de MySQL")
    print("3. Usar la herramienta MySQL Command Line Client")
    
    return None, None

if __name__ == "__main__":
    print("🏨 Hotel Transilvania - Detector de Credenciales MySQL")
    print("=" * 60)
    
    usuario, contraseña = probar_credenciales()
    
    if usuario:
        print(f"\n🎉 ¡Credenciales encontradas!")
        print(f"📋 Usuario: {usuario}")
        print(f"📋 Contraseña: {'(vacía)' if not contraseña else contraseña}")
        print("\n📌 Ahora puedo configurar tu base de datos automáticamente.")
    else:
        print(f"\n🔍 No se encontraron credenciales automáticamente.")
        print("💭 ¿Tienes MySQL Workbench instalado? Ahí podrías ver las conexiones guardadas.")