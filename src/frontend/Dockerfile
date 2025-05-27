

# Production stage with Nginx
FROM nginx

# Copy custom nginx config
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# # Copy build output to nginx public folder
# COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]