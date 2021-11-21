<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![PyPI](https://img.shields.io/pypi/v/labelme2datasets.svg)](https://pypi.python.org/pypi/labelme2datasets)
[![PythonVersion](https://img.shields.io/pypi/pyversions/labelme2datasets.svg)](https://pypi.org/project/labelme2datasets)
[![Pylint](https://github.com/veraposeidon/labelme2Datasets/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/veraposeidon/labelme2Datasets/actions/workflows/pylint.yml)
[![codebeat badge](https://codebeat.co/badges/5f99fcd3-c3a5-4154-91ca-4bb58b32bd53)](https://codebeat.co/projects/github-com-veraposeidon-labelme2datasets-opensourcejourney)
[![english][en-sheild]][en-url]
<br />
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />

<div align="center">
  <a href="https://github.com/veraposeidon/labelme2Datasets">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">labelme2Datasets</h3>

  <p align="center">
    python scripts to convert labelme-generated-jsons to voc/coco style datasets.
    <br />
    <a href="https://github.com/veraposeidon/labelme2Datasets/issues">Report Bug</a>
    ·
    <a href="https://github.com/veraposeidon/labelme2Datasets/issues">Request Feature</a>
  </p>
</div>


[（中文 README）](https://github.com/veraposeidon/labelme2Datasets//blob/main/README.zh.md)

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

Scripts in this repository are used to convert [labelme](https://github.com/wkentaro/labelme)-annotated jsons into standard datasets in [PASCAL VOC](http://host.robots.ox.ac.uk/pascal/VOC/) format or [MS COCO](https://cocodataset.org/#home) format.

Scripts are written in [Python](https://www.python.org/).

Most of the scripts refer to the [examples](https://github.com/wkentaro/labelme/tree/main/examples) section of labelme. Then I add some features according my own dataset, like class name conversion, customise image name, etc.

**Attention**: these scripts are not complicated, and if you have the basis of python, please go through the convert workflows, and ensure that it fits your datasets. There are some places I annotated `MARK`, which means pay attention to it, and you could customize it to fit your needs.

**Customize**: these scripts are only for the conversion of data I currently have. If you want to convert datasets in other areas, like instance segmentation, segmantic segmentation, video annotation, etc. please take a look at the [examples](https://github.com/wkentaro/labelme/tree/main/examples) section in labelme.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [Python](https://www.python.org/)
* [labelme](https://github.com/wkentaro/labelme)
* [imgviz](https://github.com/wkentaro/imgviz)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

1. gather the labelme-annotated jsons into a folder. In the next steps, we will refer to this folder as `labelme_jsons_dir`.

2. prepare a text file to store class names in your dataset. named it `label_names.txt`. take a look at `test/label_names.txt` for an example.

3. if need class name conversion, prepare a text file to store the conversion rules. named it `label_dict.txt`. take a look at `test/label_dict.txt` for an example.
### Installation

#### install in develop mode
1. suggested to use virtualenv to install python packages.
  
    ```sh
    conda create --name=labelme python=3.6
    conda activate labelme
    pip install -r requirements.txt
    ```
2. clone the repo.
    ```sh
    git clone git@github.com:veraposeidon/labelme2Datasets.git
    ```
3. install the package
   ```sh
    cd labelme2Datasets
    # (prefer this way!) install in editable mode, so that you can modify the package 
    pip install -e .
    # install in non-editable mode, so that you can use the package, but cannot modify it
    #python setup.py install
   ```
   
#### simply use PyPI

I also published a PyPI package named [labelme2datasets](https://pypi.org/project/labelme2datasets/).

you can just use `pip3 install labelme2datasets` to install this package.

if the baseline in this project not work for your datasets, you can install in develop mode, and modify the code by your own.


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

- convert a single json into dataset. (`labelme_json2dataset.py`)
    ```shell
    labelme_json2dataset --json_file=data/test.json \
      --output_dir=output/test_single_output
    ```

- convert a folder of jsons into voc-format dataset. (`labelme_bbox_json2voc.py`)
  - without label conversion
    ```shell
    labelme_bbox_json2voc --json_dir=data/test_jsons \
      --output_dir=output/test_voc_output --labels data/label_names.txt
    ```
  - with label conversion
    ```shell
    labelme_bbox_json2voc --json_dir=data/test_jsons \
      --output_dir=output/test_voc_output \
      --labels data/label_names.txt \
      --label_dict data/label_dict.txt
    ```
- splitting voc datasets into train set and test set. (`split_voc_datasets.py`)
  ```shell
    split_voc_datasets --voc_dir output/test_voc_output --test_ratio 0.3 --random_seed 42
  ```
  `train.txt` and `test.txt` should be generated in `voc_dir/ImageSets/Main/`.

- turn voc format dataset into coco style dataset. (`voc2coco.py`)
  ```shell
    voc2coco --voc_dir output/test_voc_output --coco_dir output/test_coco_output
  ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] add all scripts with pylint passed
- [x] chinese and english readme
- [x] modify project architecture
- [x] publish as package

See the [open issues](https://github.com/veraposeidon/labelme2Datasets/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

veraposeidon - veraposeidon@gmail.com

Project Link: [https://github.com/veraposeidon/labelme2Datasets](https://github.com/veraposeidon/labelme2Datasets)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [labelme](https://github.com/wkentaro/labelme)
* [labelme2coco](https://github.com/fcakyon/labelme2coco)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[en-sheild]:https://img.shields.io/badge/language-english-blue
[en-url]:https://github.com/veraposeidon/labelme2Datasets//blob/main/README.md
[contributors-shield]: https://img.shields.io/github/contributors/veraposeidon/labelme2Datasets.svg?style=for-the-badge
[contributors-url]: https://github.com/veraposeidon/labelme2Datasets/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/veraposeidon/labelme2Datasets.svg?style=for-the-badge
[forks-url]: https://github.com/veraposeidon/labelme2Datasets/network/members
[stars-shield]: https://img.shields.io/github/stars/veraposeidon/labelme2Datasets.svg?style=for-the-badge
[stars-url]: https://github.com/veraposeidon/labelme2Datasets/stargazers
[issues-shield]: https://img.shields.io/github/issues/veraposeidon/labelme2Datasets.svg?style=for-the-badge
[issues-url]: https://github.com/veraposeidon/labelme2Datasets/issues
[license-shield]: https://img.shields.io/github/license/veraposeidon/labelme2Datasets.svg?style=for-the-badge
[license-url]: https://github.com/veraposeidon/labelme2Datasets/blob/main/LICENSE
[product-screenshot]: images/screenshot.png
