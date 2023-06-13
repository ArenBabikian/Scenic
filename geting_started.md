```shell
# Linux
sudo apt install python3.7
curl -sSL https://install.python-poetry.org | python3 - # might need to change to python3.7
poetry --version #validation

poetry env use python3.7

### in pyprject.toml, for validation
python = "^3.7" -> python = "3.7.*"
###

poetry install # should create the virtualenv
poetry shell

# VS Code integration
which python

[Python: Select Interpreter]
[browse to scenic python installation]

# Test
dos2unix scripts/runScenic.sh
bash scripts/runScenic.sh


# if [matplotlib is currently using agg which is a non-gui backend], then
sudo apt-get install python3-tk



```