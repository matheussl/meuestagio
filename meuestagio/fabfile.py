from fabric.api import run, settings
from fabric.contrib import console
from fabric.contrib import files

from fab_deploy import *
from fab_deploy.utils import run_as_sudo
from fab_deploy.utils import upload_config_template
import fab_deploy.deploy


DEFAULT_SERVER_ADMIN = 'contato@popcode.com.br'

# Settings.
STANDARD_SETTINGS = {
    'VCS': 'git',
    'SERVER_ADMIN': DEFAULT_SERVER_ADMIN,
    'USER': 'ubuntu',
    'SUDO_USER': 'ubuntu',
    'INSTANCE_NAME': 'production',
    'DB_NAME': 'meuestagio',
    'DB_USER': 'meuestagio',
    'DB_PASSWORD': 'm3u35t4gi0',
    'DB_ROOT_PASSWORD': 'm3u35t4gi0',
    'CONFIG_TEMPLATES_PATHS': ['config_templates'],
    'REMOTE_CONFIG_TEMPLATE': 'meuestagio/settings_production.py',  # relative
    'LOCAL_CONFIG': 'meuestagio/settings_local.py',
    'PIP_REQUIREMENTS_PATH': 'meuestagio/requirements/',
    'PIP_REQUIREMENTS': 'production.txt',
    'OS': 'lucid',
    'GUNICORN_PORT': '8001',
    'GIT_BRANCH': 'deploy',
}


# Host definitions.

@define_host('ubuntu@beta.meuestagio.com')
def beta():
    """Popcode production server."""
    new_settings = {
        'INSTANCE_NAME': 'beta',
        'DB_NAME': 'beta_meuestagio',
        'PROJECT_DIR': '/home/ubuntu/src/beta/meuestagio',
        'ENV_DIR': '/home/ubuntu/envs/beta',
        'GUNICORN_PORT': '9001',
    }
    STANDARD_SETTINGS.update(new_settings)
    return STANDARD_SETTINGS



# Commands & utilities.
def aptitude_update():
    run('DEBIAN_FRONTEND=noninteractive sudo aptitude update')


def mysql_drop_db():
    """WARNING: drops the entire database."""
    mysql_execute('DROP database pck')


def profile_template():
    """Installs profile (shell) template."""
    upload_config_template('profile', '~/.profile', use_sudo=False)


@inside_project
def compilemessages():
    """compile django translations."""
    django_commands.manage('compilemessages')


def install_gettext():
    """intall gettext."""
    sudo("apt-get install gettext")


def install_pil_dependences():
    """intall gettext."""
    with settings(warn_only=True):
        sudo("apt-get build-dep python-imaging")
        sudo("""
            ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/;
            ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/;
            ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/;
        """)


def supervisor_install():
    with settings(warn_only=True):
        sudo('DEBIAN_FRONTEND=noninteractive apt-get install supervisor')
        sudo('service supervisor start')
        pass



# Web Server

def gunicorn_setup():
    """ Updates nginx config and restarts nginx. """
    name = env.conf['INSTANCE_NAME']
    run('mkdir -p %s/logs' % env.conf['ENV_DIR'])
    utils.upload_config_template('gunicorn.config',
                                 '/etc/supervisor/conf.d/%s_gunicorn.conf' % name,
                                 use_sudo=True)
    with settings(warn_only=True):
        sudo('supervisorctl stop %s-gunicorn' %name)
        sudo('supervisorctl remove %s-gunicorn' %name)
        sudo('supervisorctl reread')
        sudo('supervisorctl add %s-gunicorn' % name)
        sudo('supervisorctl start %s-gunicorn' %name)


def gunicorn_restart():
    with settings(warn_only=True):
        sudo('supervisorctl restart %s-gunicorn' % env.conf['INSTANCE_NAME'])


def gunicorn_stop():
    with settings(warn_only=True):
        sudo('supervisorctl stop %s-gunicorn' % env.conf['INSTANCE_NAME'])


def gunicorn_start():
    with settings(warn_only=True):
        sudo('supervisorctl start %s-gunicorn' % env.conf['INSTANCE_NAME'])


@utils.run_as_sudo
def nginx_setup():
    """ Updates nginx config and restarts nginx. """
    name = env.conf['INSTANCE_NAME']
    utils.upload_config_template('nginx.config',
                                 '/etc/nginx/sites-available/%s' % name,
                                 use_sudo=True)
    with settings(warn_only=True):
        sudo('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (name, name))
    sudo('invoke-rc.d nginx restart')


def setup_web_server():
    """ Sets up a web server (gunicorn + nginx). """
    instance_name = env.conf['INSTANCE_NAME']
    run('mkdir -p envs/%s/logs' % instance_name)

    nginx.nginx_install()
    supervisor_install()
    gunicorn_setup()
    nginx_setup()



# Celery

def rabbitmq_install():
    with settings(warn_only=True):
        sudo('apt-get install rabbitmq-server')
        sudo('rabbitmqctl start')


def redis_install():
    with settings(warn_only=True):
        sudo('apt-get install redis-server')
        sudo('/etc/init.d/redis-server start')


def celery_setup():
    """ Updates nginx config and restarts nginx. """
    name = env.conf['INSTANCE_NAME']
    utils.upload_config_template('celery.config',
                                 '/etc/supervisor/conf.d/%s.conf' % name,
                                 use_sudo=True)
    sudo('supervisorctl reread')
    with settings(warn_only=True):
        sudo('supervisorctl stop %s-celery' %name)
        sudo('supervisorctl remove %s-celery' %name)
        sudo('supervisorctl reread')
        sudo('supervisorctl add %s-celery' % name)
        sudo('supervisorctl start %s-celery' %name)


def celery_restart():
    with settings(warn_only=True):
        sudo('supervisorctl restart %s-celery' % env.conf['INSTANCE_NAME'])


def celery_start():
    with settings(warn_only=True):
        sudo('supervisorctl start %s-celery' % env.conf['INSTANCE_NAME'])


def celery_stop():
    with settings(warn_only=True):
        sudo('supervisorctl stop %s-celery' % env.conf['INSTANCE_NAME'])


# Django

def update_django_config():
    """ Updates :file:`config.py` on server (using :file:`config.server.py`) """
    instance_name = env.conf['INSTANCE_NAME']
    run('mkdir -p envs/%s/var/wsgi' % instance_name)
    files.upload_template(
        utils._project_path(env.conf.REMOTE_CONFIG_TEMPLATE),
        utils._remote_project_path(env.conf.LOCAL_CONFIG),
        env.conf, True
    )



# Full deploy.
def full_deploy():
    """Full, complete deploy."""

    os = utils.detect_os()
    if not console.confirm("Is the OS detected correctly (%s)?" % os, default=False):
        abort("Detection fails. Please set env.conf.OS to correct value.")
    system.prepare_server()
    install_pil_dependences()

    mysql_install()
    mysql_create_db()
    mysql_create_user()
    mysql_grant_permissions()

    install_gettext()
    deploy()



# Deploy.
def deploy():
    """Deploy project and restart apache."""
    gunicorn_stop()
    with settings(warn_only=True):
        virtualenv.virtualenv_create()
    gunicorn_start()
    make_clone()
    virtualenv.pip_install(env.conf.PIP_REQUIREMENTS, restart=False)

    update_django_config()
    syncdb()
    migrate()
    collectstatic()
    setup_web_server()
    gunicorn_restart()
