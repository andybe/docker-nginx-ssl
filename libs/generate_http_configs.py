single_forward_http = \
    'server {\n' \
    '    listen 80;\n' \
    '    listen [::]:80;\n' \
    '\n' \
    '    server_name __DOMAINS__\n' \
    '    return 301 http://__DOMAIN__$request_uri \n' \
    '}\n' \
    '\n'

single_http = \
    'server {\n' \
    '    listen 80;\n' \
    '    listen [::]:80;\n' \
    '\n' \
    '    server_name __DOMAIN__\n' \
    '\n' \
    'location / { \n'\
    '    root / var/www/__DOMAIN__/html;\n' \
    '    index index.html;\n' \
    '   }\n' \
    '}\n'

def http_conf_data(xs):
    if isinstance(xs, list) and len(xs) == 1:
        xs = xs[0]

    if isinstance(xs, str):
        return single_http.replace('__DOMAIN__', xs)

    domain = xs[-1]
    xs = xs[:-1]

    stream = single_forward_http.replace('__DOMAINS__', ' '.join(xs))
    stream += single_http

    return stream.replace('__DOMAIN__', domain)

def create_http_domain(domains = []):
    domain = domains[0]
    conf_dir = directories['nginx.conf.d'] 
    composer_dir = directories['docker-composer'] +  "/" + domain
    log_dir= directories["nginx.log"] + "/" + domain
    ssl_dir = composer_dir + "/ssl"

    default_config = conf_dir + "/" + domain + ".conf"
    try:
        f = open(default_config)
        f.close()
        print("Default configuration exist:" +default_config)
        return
    except FileNotFoundError as e:
        pass
    #create default http
#    f = open(templates['default'],"r")
#    data = f.read()
#    f.close
#    data = data.replace('__DOMAINS__', ' '.join(domains))
#    data =data.replace('__DOMAIN__', domain)
#    f = open(default_config,'w')
#    f.write(data)
#    f.close

    if not path.isdir(composer_dir):
        mkdir(composer_dir)
        #create a default html directory
        mkdir(composer_dir + "/html")
        shutil.copy2(templates['index.html'], composer_dir + "/html/index.html")

    if not path.isdir(log_dir):
        mkdir(log_dir)

    if not path.isdir(ssl_dir):
        mkdir(ssl_dir)

    # append ssl / for now we over write
    with open(default_config,'w') as config:
        f = open(templates['ssl'],"r")
        data = f.read()
        f.close
        data = data.replace('__DOMAINS__', ' '.join(domains))
        data =data.replace('__DOMAIN__', domain)
        config.write(data)
        config.close

    create_ssl_cert(ssl_dir, domain)