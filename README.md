# IS2-equipo9

Proyecto de Ingeniería del Software 2 , Metodología ágil para gestión de proyectos, Facultad Politécnica-UNA.

# Importante
Se utilizara:

* Django-guardian
* Django 1.11 LTS
* Psycopg2
* PostgreSQL 10


## Reglas Importantes para la realizacion del proyecto

# Ramas
Las ramas son bifurcaciones del proyecto, que permiten desarrollar diferentes partes de un software en paralelo.

- Para crear una rama:

> git branch Rama

- Para movernos a esa rama:

> git checkout Rama

- O el equivalente a los dos comandos anteriores:

> git checkout -b Rama

Para conveniencia trabajaremos la mayor parte del tiempo en la rama ***develop***

# Recibir/enviar cambios a los repositorios

**git pull**. Obtiene todos los últimos cambios del repositorio y hace un **merge**.
**git push**. Envía nuestros últimos commits al repositorio.

**IMPORTANTE** nunca hacer **git push** directamente sobre la rama **master**. **Siempre** realizar un **git pull** antes de pushear los cambios.

Ejemplo:

- Añadimos nuestros cambios a nuestros repositorio **Local**.

> git add .

> git commit -m "Mensaje de cambio detallado"

- Actualizamos nuestros repositorio local al mas actual.

> git pull

- Por ultimo enviamos nuestros cambios.

> git push origin **develop** (O otra rama que no se Master)


**Nota**:Para no tener que colocar siempre su user y password vayan a Settings->SSH keys-> Peguen aqui su clave SSH que pueden encontrar en /home/su_nick/.ssh/**id_ssh.pub** y si no lo tienen usen el comando **ssh keygen**

