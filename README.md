# SDG Prueba Técnica

Este repositorio contiene todos los archivos necesarios para montar el entorno de la prueba en cuestión. Las pruebas se han realizado desde un Ubuntu 22.04, por lo tanto, se recomienda su uso si se quiere replicar. Es necesario tener instalado en la máquina Docker y Docker compose.

## Introducción

El objetivo de esta prueba es crear un proceso automático con la siguiente funcionalidad:
- Recibir unos datos de entrada en formato JSON, que son leídos a través de unos metadatos
- Poder validar y transformar los datos de entrada para verificar que cumplen con las validaciones, también registradas en los metadatos
- Guardar el proceso, ya sea en los directorios propuestos en los metadatos o en alguna base de datos
- Los valores de los metadatos pueden cambiar, por tanto el código debe ser lo menos estático posible para facilitar los cambios

Este proyecto consta de 3 servicios principales ejecutándose en contendores:
- **Apache Airflow**: Plataforma de gestión de flujo de trabajo, donde se ejecutará el proceso automático
- **MySQL**: Base de datos que utiliza Apache Airflow
- **Mongo DB**: Base de datos donde se guardan los registros

## Instalación

Para desplegar el proyecto, descomprimir el archivo ZIP o descargar directamente del repositorio.

- Acceder a la carpeta:
```bash
   cd SDG
   ```

Dentro de la carpeta es necesario crear un archivo que aloje las variables de entorno necesarias. 

- Crear archivo `.env`:
```bash
   nano .env
   ```

Ejemplo:
```bash
# AIRFLOW
ADMIN_USER=admin
ADMIN_PASSWORD=admin

# MYSQL
MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=airflow
MYSQL_USER=airflow
MYSQL_PASSWORD=airflow

# MONGODB
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=root_password
```
**Se recomienda cambiar los valores, en especial las contraseñas.**

- Dar permisos de ejecución al script de instalación:
```bash
   chmod +x airflow_setup.sh
   ```

- Ejecutar el script:
```bash
   ./airflow_setup.sh
   ``` 

Una vez finalizado el script, se puede acceder a Airflow:
<http://localhost:8090>