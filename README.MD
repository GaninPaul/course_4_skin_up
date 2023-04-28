#setup env & requirements
pip install -r requirements.txt

sh db/start.sh

conda create -n vkr python=3.8

conda activate vkr

conda deactivate

#setup DB
python main.py

#run app
uvicorn main:app --reload

