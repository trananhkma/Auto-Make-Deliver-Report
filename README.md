# Auto-Make-Deliver-Report
Just because of my laziness

**DISCLAIMER: this is just a play-around tools and the code IS-NOT refactored yet, feel free to use and if you want to contribute, god bless you when start reading the source**


### Latest Version by hieulq
#### I. Environment
- Any linux distro support python 2.7
- Make sure your machine contains your private key suitable with your gerrit username.

#### II. Installation
Install dependencies

  `$ sudo pip install --proxy <proto://IP:port> -r requirements.txt`

Drop proxy part if you do not use proxy


#### III. How to use
- Run `./xdeliver.py -h` for usage

```bash
hieulq@pwner:~/$ ./xdeliver.py -h
Usage: xdeliver.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -o OWNER, --owner=OWNER
                        gerrit pwner [default: hieulq]
  -s SERVER, --server=SERVER
                        gerrit server [default: review.openstack.org]
  -p PORT, --port=PORT  gerrit port [default: 29418]
  --start-time=STARTTIME
                        start time for querrying in gerrit, in format: YYYY-
                        MM-DD
  -k FILE, --keyfile=FILE
                        gerrit ssh keyfile [default: use local keyfile]
  -P PASS, --passphrase=PASS
                        passphrase in case of enrypting keyfile
  -u USER, --user=USER  gerrit user to querry [default: hieulq]
  -d OPTION, --del=OPTION
                        whether to delete delivery folder and loc file
                        [default: 0]
```

For example, if my username is `cap` and I want to query results of user `iron` from `2016-04-01`, before start querying it will delete the current output folder (default is `Delivery`). And note that default `xdeliver` will use my local private key (at `~/.ssh/id_rsa`), if you want to use another keyfile please use option `-k <key_path>` with passphrase along with `-P <pass>`:

   `$ ./xdeliver.py -o cap -u iron  --start-time=2016-04-01 -d 1`

- After that, you will have your `Deliver` folder containing all gerrit patch-set at PDF format. **Please restructure this folder and put another research documents.. into this folder.**

- Run `./gtree.py -h` for usage

```bash
hieulq@pwner:~/$ ./gtree.py -h
Usage: gtree.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -p PATH, --path=PATH  delivery folder path [default: ~/Deliver]

```

For example, I want to generate the tree file 'list_of_file_Container_20161205.txt' with LOC and page count from folder generate from `xdeliver`:
   
   `$ ./gtree.py -p Deliver >list_of_file_Container_20161205.txt`

- And the result is the file 'list_of_file_Container_20161205.txt' is created with the following content:

```bash
                                                                                  [Page count (for documents)]       [Line count (for source code)]
Total Pages count:--------------------------------------------------------------------------435 pages
Total Lines count:-------------------------------------------------------------------------------------------------21594 insertion(+), 10609 deletions(-)
Folder PATH listing
|   List_of_files---------------------------------------------------------------------------38
|   
+---1. XXXXXXX
|   +---1.1. XXXXXX
|   |   +---1.1.1. XXXXXXXXXX
|   |   |   +---XXXXXXXXXXXXXXXX
|   |   |   |       XXXXXXXXXXXXXXXXXXXXXXXXXX.pdf------------------------------------------16
|   |   |   |       XXXXXXXXXXXXXXXXXXXXXXX.pdf---------------------------------------------20
|   |   |   |       
|   |   |   +---XXXXXXXXXXXX
|   |   |   |       XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX----------1
|   |   |   |       
|   |   |   +---XX
|   |   |   |       XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-------------------------21
|   |   |   |       XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-------------------------20
|   |   |   |       
|   |   |   \---XXXXXXXXX
|   |   |           XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX--------------------15
|   |   |  
|    .....
|
|       
\---2. XXXXXXXXX
    +---2.1. XXXXXXXXXXX
    +---2.2. XXXXXXX
    \---2.3. XXXXXXXXXXXXX
        +---2.3.1_XXXXXXXXXXXX
        |   \---XXXXXX
        |       +---XXXXXXXXXXXXXXXX
        |       |         - XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        |       |   \---XXXXXXXXXXXX
        |       |           XXXXXXXXXXXXXXXXXXXXXXXXXXX ------------------------------------------------------------58 insertions(+), 28 deletions(-)
        |       |           XXXXXXXXXXXXXXXXXXXXXXXXXXX ------------------------------------------------------------57 insertions(+), 28 deletions(-)
        |       |           XXXXXXXXXXXXXXXXXXXXXXXXXXX ------------------------------------------------------------62 insertions(+), 28 deletions(-)
        ......
```

### Legacy Version by trananhkma
#### I. Environment
-- Ubuntu 14.04 <br>
-- Mozilla Firefox 43.0.4

#### II. Installation
Install Xvfb – The X Virtual FrameBuffer (Need to run with selenium)

  `$ sudo apt-get install xvfb`

Install selenium - Need to get HTML of JS page. Because gerrit use JS to generate HTML.

  `$ sudo pip install -U selenium`

Install reportlab - A Python lib allow to work with PDF file.

  `$ sudo pip install -U reportlab`


#### III. How to use
1. Copy and paste your gerrit links to <b>input.txt</b> file. <br>
Make sure your gerrit links matched with this format:
  `https://review.openstack.org/#/c/xxxxx/`

2. Replace <b>FIREFOX_BIN</b> in <b>deliver.py</b> file by your firefox dir. <br>
Show this dir with

  `$ which firefox`

3. Edit some configurations on <b>txt2pdf.py</b> if you want.

4. Get your deliver

  `$ xvfb-run python deliver.py`

5. Follow screen to make sure you don't miss anything.
