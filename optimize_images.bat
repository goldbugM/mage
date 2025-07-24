@echo off
echo Installing required dependencies...
pip install -r requirements.txt

echo.
echo Starting image optimization...
python optimize_images.py

echo.
echo Optimization complete! Check the public/images/optimized folder.
pause
