1. Measuring results of three topologies are stored in corresponding json file.
2. Keys of entries in json files represent the two hosts involved. 
3. There are 3 elements in each value. They are measured time of ping test, iperf test and concurrent test([ping, iperf]) respectively. e.g. h1->h2:[12ms, 13ms, [14ms, 15ms]] means that this is a test from host h1 to host h2, ping test alone lasts 12ms, iperf test alone lasts 13ms, in concurrent test, ping test costs 14ms while iperf test costs 15ms. 
4. There might be indent format issue in python file since I copied it from Linux to OSX. It displays and works well on Ubuntu 16.04 as I've obtained the results shown in the folder.

U07913832
Da Sun