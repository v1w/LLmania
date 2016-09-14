#! /bin/bash
cd "$( dirname "${BASH_SOURCE[0]}" )"
rm -rf ../dist;
cython -3 -D libres.py;
gcc-6 -c  -fPIC -I /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/include/python3.5m libres.c;
gcc-6 -O3 -shared -L /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/lib -l python3.5 libres.o -o libres.so;
rm libres.c;
rm libres.o;
mv -f libres.so ../;
cython -3 -D libgame.py;
gcc-6 -c  -fPIC -I /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/include/python3.5m libgame.c;
gcc-6 -O3 -shared -L /usr/local/Cellar/python3/3.5.2_1/Frameworks/Python.framework/Versions/3.5/lib -l python3.5 libgame.o -o libgame.so;
rm libgame.c;
rm libgame.o;
mv -f libgame.so ../;
cd ..;
cp -f ./src/main.py ./
pyinstaller -F main.py --key KnALGVu5QwZ6ehyDd;
rm -rf build;
rm -rf __pycache__;
rm -f main.spec;
rm -f main.py;
mv -f libgame.so ./lib/;
mv -f libres.so ./lib/;
cp -rf ./src/resources dist/;
cp ./src/launcher ./dist;
tar -zvcf ./dist/dist.tar.gz ./dist;