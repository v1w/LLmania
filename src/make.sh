#! /bin/bash
cd "$( dirname "${BASH_SOURCE[0]}" )"
rm -rf ../dist;
cython -3 -D libres.py;
clang -c  -fPIC -I /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/include/python3.5m libres.c;
clang -O3 -shared -L /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/lib -l python3.5 libres.o -o libres.so;
rm libres.c;
rm libres.o;
mv -f libres.so ../;
cython -3 -D game.py;
clang -c  -fPIC -I /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/include/python3.5m game.c;
clang -O3 -shared -L /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/lib -l python3.5 game.o -o game.so;
rm game.c;
rm game.o;
mv -f game.so ../;
cython -3 -D gamewindow.py;
clang -c  -fPIC -I /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/include/python3.5m gamewindow.c;
clang -O3 -shared -L /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/lib -l python3.5 gamewindow.o -o gamewindow.so;
rm gamewindow.c;
rm gamewindow.o;
mv -f gamewindow.so ../;
cd ..;
cp -f ./src/main.py ./
pyinstaller -F main.py;
rm -rf build;
rm -rf __pycache__;
rm -f main.spec;
rm -f main.py;
mv -f gamewindow.so ./lib/;
mv -f game.so ./lib/;
mv -f libres.so ./lib/;
cp -rf ./src/resources dist/;
cp ./src/launcher ./dist;
tar -zvcf ./dist/dist.tar.gz ./dist;