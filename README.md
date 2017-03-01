# Arma 3 PBO Server Optimizer
PBO Server Optimizer is a simple Python script that optimizes mods pbo file for Arma 3 servers. The original game is over 10GB, the server only ~4GB. What is the secret file server? It's simple. PBO file server does not have the texture and sound is downsampling. This script replaces the texture files in PBO to blank texture.

## Installation and usage
1. Install [Arma 3 Tools](http://store.steampowered.com/app/233800/) from Steam
2. Install [Python 3.6](https://www.python.org/downloads/) and [add Python to PATH](https://docs.python.org/3/using/windows.html#installation-steps)
3. Unpack pboServerOptimizer
5. If you install Steam in custom folder fix path to Arma 3 Tools in pboServerOptimizer.py file
6. Create folder in pboServerOptimizer for mods to optimize
7. Copy mods to created folder (Steam Workshop mods location: `Steam\steamapps\common\Arma 3\!Workshop`)
8. Run console in pboServerOptimizer folder and type the `python pboServerOptimizer.py -h` to show usage
9. Run `python pboServerOptimizer.py modsFolder outputFolder` to optimize mods in modsFolder. Optimize mods is in outputFolder
10. Install mods from output folder on you server

## Visualization
![Visualization](http://i.imgur.com/wQ6f2Vg.gif)

## Examples of optimization results
* Community Upgrade Project (CUP) - Full 21,5 GB => 5,44 GB
