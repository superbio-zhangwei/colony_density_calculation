#step 1 根据conda_enviroment.yaml创建conda虚拟环境
conda env create -f conda_environment.yaml

#step2 激活环境
conda activate images_opencv

#step3 pyinstaller打包成exe
pyinstaller --onefile --noconsole CDC.py

#step4
双击打开CDC.exe即可选择图片进行使用，只需要用鼠标框选对应的菌落即可实现菌落平均密度的计算

