# ENVIRONMENT = 'development'
ENVIRONMENT = 'production'

if ENVIRONMENT == 'development':
    SETTINGS_MODULE = 'sensors_africa.settings.development'
if ENVIRONMENT == 'production':
    SETTINGS_MODULE = 'sensors_africa.settings.production'
