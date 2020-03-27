from distutils.core import setup

pkg = 'Extensions.InadynServiceManager'
setup (name = 'enigma2-plugin-extensions-inadynservicemanager',
	version = '1.0',
	description = 'Inadyn service monitor and configuration file editor',
	packages = [pkg],
	package_dir = {pkg: 'plugin'},
	package_data = {pkg: ['*.png']},
)
