FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN chmod -R 755 /usr/share/nginx/html && chown -R nginx:nginx /usr/share/nginx/html
EXPOSE 80
