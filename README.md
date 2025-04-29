# Land Use Classification Prototype

This repository contains a prototype system for land use classification using satellite imagery. It processes multispectral satellite data, applies machine learning algorithms, and classifies the land surface into distinct land use categories. The system is built to support the full workflow: from data preprocessing, feature extraction, model training, to final classification and visualization. This prototype aims to serve as a foundation for further research and development in remote sensing, environmental monitoring, and automated land use mapping.

## Requirements
To run the system, it is important to download and install Python. You can do this at:  https://www.python.org/downloads/. 
> [!TIP]
> It is recommended to download any version of 3.11.X. Code written on 3.11.9.

## Prototype Setup:
Before beginning the system installation, it is important to perform a git clone and download the repository to your local machine. Using the terminal or command prompt, you must also navigate to the project directory. For example:
```
juliusjancevicius@Juliuss-MBP ~ % cd Desktop 
juliusjancevicius@Juliuss-MBP Desktop % mkdir Test
juliusjancevicius@Juliuss-MBP Desktop % cd Test 
juliusjancevicius@Juliuss-MBP Test % git clone git@github.com:janceviciusjulius/Programu-sistemu-modeliavimas-ir-kurimas.git
Cloning into 'Programu-sistemu-modeliavimas-ir-kurimas'...
remote: Enumerating objects: 202, done.
remote: Counting objects: 100% (202/202), done.
remote: Compressing objects: 100% (125/125), done.
remote: Total 202 (delta 109), reused 161 (delta 71), pack-reused 0 (from 0)
Receiving objects: 100% (202/202), 48.81 KiB | 476.00 KiB/s, done.
Resolving deltas: 100% (109/109), done.
juliusjancevicius@Juliuss-MBP Test % cd Programu-sistemu-modeliavimas-ir-kurimas
juliusjancevicius@Juliuss-MBP Programu-sistemu-modeliavimas-ir-kurimas % 
```

### 1. Method (Using pipenv)
1.	First, install the pipenv library. This can be done with the command:
```python
pip install pipenv
```

2.	Then, install all the required libraries:
```
pipenv install
```

3.	After successfully installing the libraries, run:
```
pipenv shell
```

4.	Launch the system:
```
cd src
pipenv run python main.py
```

### 2. Method (Using standard pip)
1.	Create a ```virtual environment```:
```
python -m venv venv
```

2. Activate ```virtual environment```:
> [!TIP]
> MacOS/Linux: ```source venv/bin/activate```
> 
> Windows: ```venv\Scripts\activate```

3. Install the libraries:
```
pip install -r requirements.txt
```

4.	Launch the system:
```
cd src
python main.py
```
