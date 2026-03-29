# Servidor ligero para contenido estático (HTML, CSS, JS)
FROM nginx:alpine

# Copiamos la configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiamos todos los archivos de la carpeta actual (frontend) a la carpeta pública de Nginx
COPY . /usr/share/nginx/html

# Aseguramos los permisos correctos
RUN chmod -R 755 /usr/share/nginx/html

# Exponer el puerto para Dokploy
EXPOSE 80

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
