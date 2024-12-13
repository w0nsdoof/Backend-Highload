sudo service postgresql down

sudo systemctl daemon-reload

sudo service gunicorn-django-1 restart
sudo service gunicorn-django-2 restart
sudo service gunicorn-django-3 restart

sudo nginx -t && sudo systemctl restart nginx
