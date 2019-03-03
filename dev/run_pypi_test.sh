deactivate_venv
conda create -n test_pypi_ubelt python=3.6 -y
conda activate test_pypi_ubelt
cd ~/tmp
pip install ubelt[all]
pytest ~/code/ubelt
pytest ~/code/timerit
pytest ~/code/progiter
conda deactivate
conda env remove --name test_pypi_ubelt
