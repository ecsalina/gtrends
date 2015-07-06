from setuptools.core import setup

setup(
	name="gtrends",
	version = "0.1a",
	py_modules = ["gtrends", "_login"],
	description = "Automated Google Trends downloader.",
	author = "Eric Salina",
	author_email = "ecsalina@gmail.com",
	url = "",
	license = "MIT",
	long_description = open("README.rst").read(),

	classifiers = [
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"Topic :: Utilities",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 2.7"
	]
)