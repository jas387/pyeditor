import os
import importlib

def load(*w, folder: str='pluggins', **kw):
	pluggins = []
	pluggins_files = [pluggin for pluggin in os.listdir(folder) if pluggin.endswith('.py') and not pluggin.startswith('template')] # list of .py files
	for plug in pluggins_files:
		path=f'{folder}.{plug[:-3]}'
		module=importlib.import_module(f'{path}')
		pluggin = module.Pluggin()
		pluggins.append(pluggin)
	return pluggins

