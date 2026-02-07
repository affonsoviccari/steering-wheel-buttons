from PyQt5.QtCore import QSettings

def get_gpio_binded_button(settings: QSettings, id: str) -> bool:
    '''Get the correspondig button id gpio bind, it return `None` if doesn't.'''
    return settings.value(f"/bind/gpio/{id}", None)

def get_key_binded_button(settings: QSettings, id: str) -> bool:
    '''Get the correspondig button id key bind, it return `None` if doesn't.'''
    return settings.value(f"/bind/key/{id}", None)

def set_gpio_bind_button(settings: QSettings, id: str, gpio: str):
    '''Set the correspondig button id gpio bind.'''
    settings.setValue(f"/bind/gpio/{id}", gpio)

def set_key_bind_button(settings: QSettings, id: str, key: str):
    '''Set the correspondig button id key bind.'''
    settings.setValue(f"/bind/key/{id}", key)