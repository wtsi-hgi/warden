THIS PROGRAM IS NOT YET FULLY FUNCTIONAL
========================================

# Warden
Warden is a web-based frontend used to interact with [Arboretum](https://github.com/wtsi-hgi/arboretum), allowing the user to see available groups and launch/destroy instances for them. 

### Dependencies 
Python libraries:
 - `Flask`
 - `gunicorn`
 - `python-ldap`

### Quick start guide
Warden won't work unless the Arboretum API is running on `localhost:8000`. 
To launch Warden, run `gunicorn -b 0.0.0.0:[port] wsgi:app`. 
Note: To run on port 80, `gunicorn` must be started with superuser privileges.
