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

### Setup VueJS Frontend
Requires [Node.js](https://nodejs.org/en/download/)
```bash
cd .\frontend\
npm install -g npm
npm install
npm run dev
```