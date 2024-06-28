@ECHO OFF

python -m pip --version

if %ERRORLEVEL% NEQ 0 (
  echo Error: Could not locate pip package manager. 
  echo Please ensure you have Python 3 and pip package manager installed & updated.
  echo Go to: https://www.python.org/downloads/ to install Python.
  EXIT /B 99)

pip3 install --upgrade pip

pip3 install numpy --upgrade
pip3 install scipy --upgrade
pip3 install pickle-mixin --upgrade
pip3 install Pillow --upgrade
pip3 install tk --upgrade
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116

:: Constructs and saves all required sprite (car) image files...
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/black_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/blue_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/forest_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/green_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/navy_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/orange_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/pink_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/purple_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/red_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/special_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/white_car.png
python ./race/car_sprite_images/_sprite_generator.py ./race/car_sprite_images/yellow_car.png

set NL=
echo:
echo Attempted to install all required dependencies...  
echo If you still encounter an error attempting to run the game then please 
echo verify that the correct version of PyTorch has been installed for your system.
echo Visit: https://pytorch.org/get-started/locally/ for more information.
echo Also, verify that your PATH environmental variable is configured properly.
echo:

cmd /k