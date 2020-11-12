docker run -it --rm --net=host -v /etc/letsencrypt:/etc/letsencrypt \
                    -v /var/log/letsencrypt:/var/log/letsencrypt \
                    -v /var/www:/var/www \
                    certbot/certbot \
                    --staging  certonly \
                    --webroot --register-unsafely-without-email \
                    --agree-tos  --webroot-path=/var/www/letsencrypt/ -d text.com -d  www.test.com
