# Land Use Classification Prototype

This repository contains a prototype system for land use classification using satellite imagery. It processes multispectral satellite data, applies machine learning algorithms, and classifies the land surface into distinct land use categories. The system is built to support the full workflow: from data preprocessing, feature extraction, model training, to final classification and visualization. This prototype aims to serve as a foundation for further research and development in remote sensing, environmental monitoring, and automated land use mapping.

## Requirements
To run the system, it is important to download and install Python. You can do this at:  [Python downloads](https://www.python.org/downloads/). 
> [!TIP]
> It is recommended to download any version of 3.11.X. Code written on 3.11.9.

## Satellite Data Access
To download the necessary satellite data, you must create a free account on the ***Copernicus Data Space Ecosystem*** platform: [Copernicus Data Space Ecosystem](https://browser.dataspace.copernicus.eu).
Registration is required to access and download Sentinel-2 Level 2A products.

Alternatively, to streamline the setup process, you may use the account credentials provided for this demonstration. These credentials should be securely stored in the ```.env``` file located in the main project directory.

*The latter ```.env``` file*:

```bash
USERNAME=julius.jancevicius@stud.vilniustech.lt
PASSWORD=TestinePaskyra123+
```

## Prototype Setup:
Before beginning the system installation, it is important to perform a git clone and download the repository to your local machine. Using the terminal or command prompt, you must also navigate to the project directory. For example:
```
juliusjancevicius@Juliuss-MacBook-Pro ~ % cd Desktop 
juliusjancevicius@Juliuss-MacBook-Pro Desktop % mkdir GitExample
juliusjancevicius@Juliuss-MacBook-Pro Desktop % cd GitExample 
juliusjancevicius@Juliuss-MacBook-Pro GitExample % git clone git@github.com:janceviciusjulius/land-use-classification.git
Cloning into 'land-use-classification'...
remote: Enumerating objects: 1283, done.
remote: Counting objects: 100% (35/35), done.
remote: Compressing objects: 100% (24/24), done.
remote: Total 1283 (delta 18), reused 21 (delta 11), pack-reused 1248 (from 1)
Receiving objects: 100% (1283/1283), 149.63 MiB | 14.09 MiB/s, done.
Resolving deltas: 100% (834/834), done.
juliusjancevicius@Juliuss-MacBook-Pro GitExample % cd land-use-classification 
juliusjancevicius@Juliuss-MacBook-Pro land-use-classification % 
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
