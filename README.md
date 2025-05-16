# semantic-search

Create a searchable semantic index to find documents and sites.

# Setup

Clone the repository:
```bash
git clone https://github.com/tobiaswuerth/semantic-index.git
cd .\semantic-index\
```

### Setup Python Backend
Tested on Windows
```bash
py -m venv .venv
.\.venv\Scripts\activate
python.exe -m pip install --upgrade pip

# for users with CUDA supported GPU
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 

pip3 install -r .\requirements.txt
```

#### REST API
Host API by running:
```bash
uvicorn backend:app --host 0.0.0.0 --port 5000
```
this should start a server, e.g. on http://localhost:5000/.

#### Embedding Factory
If the webserver that handles the data and REST API does not have a GPU, invoking the embedding model might result in suboptimal performance. One can host an embedding factory separately by running:
```bash
uvicorn embedding_factory:app --host 0.0.0.0 --port 8000
```
this should start a server, e.g. on http://localhost:8000/.
Now one can specify the remote host embedding factory by modifying [config.yaml](config.yaml).


### Setup VueJS Frontend
Requires [Node.js](https://nodejs.org/en/download/)
```bash
cd .\frontend\
npm install -g npm
npm install
```

run with
```bash
npm run dev
```
this should start a localhost server, e.g. on http://localhost:5173/.
