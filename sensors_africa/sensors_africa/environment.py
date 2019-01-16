ENVIRONMENT = 'test'
# ENVIRONMENT = 'development'
# ENVIRONMENT = 'production'

if ENVIRONMENT == 'test':
    SETTINGS_MODULE = 'sensors_africa.settings.test'
if ENVIRONMENT == 'development':
    SETTINGS_MODULE = 'sensors_africa.settings.development'
if ENVIRONMENT == 'production':
    SETTINGS_MODULE = 'sensors_africa.settings.production'
