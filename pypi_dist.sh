python setup.py bdist_wheel --universal
twine upload dist/*
# travis encrypt --add deploy.password