# image_downloader_multiprocessing_python


Here we will use multiprocessing to download images in batch with python.

This saved me a lot of time while downloading images.


## Installation

### Clone the repository to your machine.

```
git clone https://github.com/nOOBIE-nOOBIE/image_downloader_multiprocessing_python
```
### Install the requirements

```
pip install -r requirements.txt
```


### Usage

```
python3 image_downloader.py <filename_with_urls_seperated_by_newline.txt> <num_of_process>
```

This will read all the urls in the text file and download them into a folder with name same as the filename.
num_of_process is optional.(by default it uses 10 process)


### Example

```
python3 image_downloader.py cats.txt
```

![cat images downloading](https://snipboard.io/VOXItq.jpg)

![cat image downloading](https://snipboard.io/6UgtE2.jpg)



### Benchmark

1183 images in 121.99 seconds with 10 process.


#### Asynchrone versus Multiprocessing

```bash
╰─ /usr/bin/time -v make image_downloader_mp
find cats -name '*.jpg' -exec rm -f {} +
Nb url images: 1183
MESSAGE: Running 10 process
Downloading: https://cdn.pixabay.com/photo/2017/06/12/19/02/cat-2396473__480.jpg
[...]
Download complete: https://cdn.pixabay.com/photo/2015/07/13/21/54/gray-cat-843916__480.jpg
Command being timed: "make image_downloader_mp"
        User time (seconds): 39.94
        System time (seconds): 1.81
        Percent of CPU this job got: 113%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:36.74
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 72540
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 31988
        Voluntary context switches: 55631
        Involuntary context switches: 2240
        Swaps: 0
        File system inputs: 0
        File system outputs: 132160
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
```

```sh
╰─ /usr/bin/time -v make image_downloader_aio
find cats -name '*.jpg' -exec rm -f {} +
Nb url images: 1183
Downloading: https://cdn.pixabay.com/photo/2017/06/12/19/02/cat-2396473__480.jpg
[...]
Download complete: https://cdn.pixabay.com/photo/2014/10/29/22/12/cat-508665__480.jpg
Command being timed: "make image_downloader_aio"
        User time (seconds): 3.95
        System time (seconds): 0.98
        Percent of CPU this job got: 34%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:14.51
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 59300
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 10
        Minor (reclaiming a frame) page faults: 14560
        Voluntary context switches: 37895
        Involuntary context switches: 653
        Swaps: 0
        File system inputs: 7096
        File system outputs: 132632
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0
```

### Images folder sample

![cats](https://snipboard.io/VzlD78.jpg)
