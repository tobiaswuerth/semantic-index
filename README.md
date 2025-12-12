# semantic-search

Create a searchable semantic index to find documents and sites.

![image](https://github.com/user-attachments/assets/eab28a58-bc28-45f9-8fe3-80d8c4e5b334)

**Note:**
- This is only a proof of concept. Tested on Windows.
- Currently only supports indexing the file system. It should, however, be easily extensible to other source types, e.g. crawling a wiki.
- When processing large amounts of data, it is advisable to have a GPU with CUDA support.

# Usage

```
usage: index.py [-h] [--ingest HANDLER SOURCE] [--process] [--search QUERY] [--kcount KCOUNT]

Semantic Index Manager

options:
  -h, --help            show this help message and exit
  --ingest HANDLER SOURCE, -i HANDLER SOURCE
                        Ingest sources using the specified handler and source (e.g., -i file
                        /path/to/folder, -i jira https://my.url/api)
  --process, -p         Process all sources
  --search QUERY, -s QUERY
                        Find k-nearest neighbors for the query
  --kcount KCOUNT, -kc KCOUNT
                        Number of results to return for KNN search (default: 5)
```

### Examples
Either individual commands, like
```
py .\index.py --ingest file "D:\my_data"
py .\index.py --ingest jira "https://jira.company.ch" -a key=MY_API_KEY
py .\index.py --process
py .\index.py --knn "test" --kcount 5
```

or chain multiple ones, like
```
py .\index.py --ingest "D:\my_data" --process --knn "test" --kcount 5
```

which might output something like

```
09:01:18 [ INFO ] Starting Semantic Index Manager...
09:01:18 [ INFO ] Loading database...
09:01:18 [ INFO ] Loading database sources...
09:01:19 [ INFO ] Loading database embeddings...
09:01:23 [ INFO ] Loaded 29715 sources and 698563 embeddings from the database
09:01:23 [ INFO ] Using device: cpu
09:01:23 [ INFO ] Loading model...
09:01:25 [ INFO ] Model loaded successfully.
09:01:25 [ INFO ] Initialized Semantic Index Manager
09:01:25 [ INFO ] ----------------------------------------
09:01:25 [ INFO ] Ingesting sources from: D:\my_data
09:01:25 [ INFO ] Ingesting sources into the database...
09:01:25 [ INFO ] Inserted 1 sources into the database
09:01:25 [ INFO ] Loading database...
09:01:25 [ INFO ] Loading database sources...
09:01:26 [ INFO ] Loading database embeddings...
09:01:30 [ INFO ] Loaded 29716 sources and 698563 embeddings from the database
09:01:30 [ INFO ] Ingested sources from D:\my_data
09:01:30 [ INFO ] ----------------------------------------
09:01:30 [ INFO ] Processing all sources
09:01:30 [ INFO ] Processing sources...
09:01:30 [ INFO ] Found 1 sources to process.
Processing sources: 100%|████████████████████| 1/1 [00:12<00:00, 12.28s/source]
09:01:42 [ INFO ] Finished processing sources.
09:01:42 [ INFO ] Loading database...
09:01:42 [ INFO ] Loading database sources...
09:01:43 [ INFO ] Loading database embeddings...
09:01:47 [ INFO ] Loaded 29716 sources and 698568 embeddings from the database
09:01:47 [ INFO ] Processed all sources
09:01:47 [ INFO ] ----------------------------------------
09:01:47 [ INFO ] Finding KNN for query: test with k=5
09:01:47 [ INFO ] Finding 5 nearest neighbors for query: test
09:01:54 [ INFO ] Top 5 results for: 'test'
09:01:54 [ INFO ]  > ID 13593 similarity 0.9335: file:///.../my_file.pdf
09:01:54 [ INFO ]  > ID 13594 similarity 0.9335: file:///.../my_file2.pdf
09:01:54 [ INFO ]  > ID 28425 similarity 0.8642: file:///.../test.md
09:01:54 [ INFO ]  > ID 16135 similarity 0.8546: file:///.../wordyword.docx
09:01:54 [ INFO ]  > ID 14267 similarity 0.7517: file:///.../another one.pdf
```

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
this should start a server, e.g. on http://localhost:5000/api/.

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
