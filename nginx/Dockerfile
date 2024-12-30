FROM nginx:1.25.5

COPY nginx.conf /etc/nginx/nginx.conf

CMD ["mkdir", "/staticfiles"] 
CMD ["nginx", "-g", "daemon off;"]