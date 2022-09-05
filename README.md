# DeepFlicc
DeepFlicc is the name of my  Bsc. graduation project.The idea is applied DeepLearning Algorithm on Distributed
Computer vision Systems.
# To Do
 - [x] Fix JPEG data corruption bug with custom ***peg_healthy_check(jpeg_buffer_size)*** function
   [Bug to fix](bug1.png)
 - [ ] Connected more than one remote device
 - [ ] Finished the Qt interface to display more than one remote display simultanously
 
 # How to use the code 🔥
 :fire: Warning :fire: This Project was `developed and tested on Linux based operating sistem`,I dont know if everything could gone well on Microsoft Window Operating Systems.
 - ***Client Side source Code<br/>***
> first of all prepare you raspberry pi 3B+ or superior with pi camera runing raspbian operating system.<br/>
Use [this tutorial](https://www.hostinger.com/tutorials/how-to-use-putty-ssh) to connect to your raspberry pi throught putty.<br/>
>  Make sure you have pip3 install in you system.You can check it by runing the command below:<br/>
>
```
which pip3
or 
pip3 --version
```
if pip3 hasn't been installed you can installed by doing:
```
 sudo apt-get install python3-pip
```
After pip have been installed ,you can now install `python-opencv` and other dependencies by runing :
```
pip install -r requirements.txt
```
inside `client folder`</br>
Since we are using `User Datagram Protocol (UDP)` you can start the client by runing:
```
python client.py <server-ip-address>
```
Dont forget to replace `<server-ip-address>` by the ip adress of your host computer.
If your host computer's OS is Linux based operating system, you can get the ip with these commands:`hostname -I `,`ifconfig` </br>
if the Os is based on microsoft windows you can  run `ipconfig` by specifing other parameter of course.
- ***Server Side Code</br>***
First of all,go into the server folder and then the folder named `data` and create some subfolder.The name of each subfolder must represent the name  of the persone you want your Model to identify.You have to take one or two short video like `10 secondes` each who capture every aspect of the face of the persone you want identify and make sure that it's this persone onlly who appear in the video to confuse the Network when training.
After that go back to `server` folder
