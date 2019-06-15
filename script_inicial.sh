#!/bin/bash

#AMBIENTE DE DESARROLLO
BASEDIR="$PWD"
read -p "Ingrese el path donde sera guardado el proyecto de IS2 para el ambiente de desarrollo: " path_desarrollo

echo "Comprobando si existe el directorio"

if [ ! -d $path_desarrollo/IS2_Equipo09 ]; then
  echo "Creando directorio IS2_Equipo09"
  mkdir -p $path_desarrollo/IS2_Equipo09;
fi

echo "Clonando el repositorio en la direccion: $path_desarrollo "

git clone git@gitlab.com:endagafi/ProyectoIS2_9.git $path_desarrollo/IS2_Equipo09

echo "Cargando Lista de Tag hechos\n"


cd $path_desarrollo/IS2_Equipo09

python3 -m venv venv

echo "Inicializando Git" 

git fetch --all

echo "Mostrando Lista de Tags"

git tag -l 

read -p "Ingrese el nombre del tag que quiere descargar : " nombre_tag

echo "Tagging $nombre_tag"

git checkout tags/$nombre_tag 

echo "Ajustes de Base de Datos"

sudo -u postgres psql -c "DROP DATABASE IF EXISTS is2db;"
sudo -u postgres psql -c "create DATABASE is2db;"

source "$PWD""/venv/bin/activate"

pip install -r requirements.txt

echo ' entorno de Desarrollo listo'

#llamar a poblar 
chmod u+x datos_de_prueba/poblar.sh
./datos_de_prueba/poblar.sh

echo 'Fin de configuracion del entorno de desarrollo'

#CONFIGURANDO ENTORNO DE PRODUCCION
sudo apt-get install libapache2-mod-wsgi-py3

sudo -u postgres psql -c "DROP DATABASE IF EXISTS is2db_produccion;"
sudo -u postgres psql -c "create DATABASE is2db_produccion;"

cd $BASEDIR

read -p "Ingrese el path donde sera guardado el proyecto de IS2 para el ambiente de produccion: " path_produccion


echo "Comprobando si existe el directorio"

if [ ! -d $path_produccion ]; then
  echo "Creando directorio IS2_Equipo09"
  mkdir -p $path_produccion;
fi

echo "Clonando el repositorio en la direccion: $path_produccion "

git clone git@gitlab.com:endagafi/ProyectoIS2_9.git $path_produccion

cd $path_produccion

python3 -m venv venv_produccion

git checkout master

source "$BASEDIR"/"$path_produccion"/venv_produccion/bin/activate

pip install -r requirements.txt

chmod u+x datos_de_prueba/poblar.sh

./datos_de_prueba/poblar.sh

echo "Sobreescribiendo el archivo /etc/apache2/sites-available/000-default.conf"

echo "
Define proyecto_is2_path $PWD
Define venv_path $PWD/venv_produccion/
<VirtualHost *:80>

	Alias /static/ \${proyecto_is2_path}/static/
	

	<Directory \${proyecto_is2_path}/static>
		Require all granted
		 Allow from all 
	</Directory>

	Alias /static/admin/ \${venv_path}lib/python3.5/site-packages/django/contrib/admin/static/admin/
	<Directory \${venv_path}lib/python3.5/site-packages/django/contrib/admin/static/admin>
		Require all granted
		 Allow from all 
	</Directory>

	
	<Directory \${proyecto_is2_path}/ProyectoIS2_9>
            ##Options Indexes FollowSymLinks Includes ExecCGI
            ##AllowOverride All
            ##Order allow,deny
            ##Allow from all
            Require all granted
        </Directory>

	<Directory \${proyecto_is2_path}/ProyectoIS2_9>
		<Files wsgi.py>
			Require all granted
			 Allow from all

		</Files>
	</Directory>
	WSGIDaemonProcess ProyectoIS2_9 python-home=\${venv_path} python-path=\${proyecto_is2_path}
	WSGIScriptAlias / \${proyecto_is2_path}/ProyectoIS2_9/wsgi.py process-group=ProyectoIS2_9
        WSGIApplicationGroup %{GLOBAL}


</VirtualHost> >
" | sudo tee /etc/apache2/sites-available/000-default.conf

sudo service apache2 restart


source "$BASEDIR"/"$path_desarrollo"/IS2_Equipo09/venv/bin/activate
cd "$BASEDIR"/"$path_desarrollo"/IS2_Equipo09
python manage.py runserver