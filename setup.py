# please install python if it is not present in the system
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
 name='anomaly_detection_app',
 version='1.0.0',
 packages=[],
 license = 'MIT',
 description = 'anomaly detection service',
 author = 'Chaim Paciorkowski',
 author_email = 'chaim@webiks.com',
 keywords = [],
 long_description=long_description,
 long_description_content_type="text/markdown",
 url="https://github.com/Webiks/anomaly-detection-service",
 include_package_data=True,
)