#setup env & requirements

pip install -r requirements.txt

sh db/start.sh

conda create -n vkr python=3.8

conda activate vkr

conda deactivate

#setup DB

cd src
python main.py

#run app

cd src
uvicorn main:app --reload

